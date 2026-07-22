import io
import json
import math
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import MagicMock, patch

import requests
from django.test import TestCase
from PIL import Image

import openpyxl
from django.core.files.uploadedfile import SimpleUploadedFile
from api.models import Company

from ai.models import Document, SpreadsheetImport
from ai.services.forecast import InsufficientHistoryError, forecast_cashflow
from ai.services.ocr import OCRExtractionError, _extract_amounts_by_pattern, extract_invoice
from ai.services.spreadsheet import (
    SpreadsheetError,
    apply_mapping,
    parse_spreadsheet,
    propose_mapping,
)


def _tiny_png_bytes():
    buf = io.BytesIO()
    Image.new('RGB', (10, 10), color='white').save(buf, format='PNG')
    return buf.getvalue()


def _fake_ollama_response(payload_text):
    mock_resp = MagicMock()
    mock_resp.raise_for_status.return_value = None
    mock_resp.json.return_value = {'response': payload_text}
    return mock_resp


CONSISTENT_PAYLOAD = {
    'doc_type': 'invoice',
    'langue': 'fr',
    'fournisseur': 'ACME SARL',
    'date': '2026-06-01',
    'numero': 'F-2026-001',
    'montant_ht': 100.0,
    'montant_tva': 20.0,
    'montant_ttc': 120.0,
    'lignes': [{'description': 'Service A', 'quantite': 1, 'prix_unitaire': 100.0, 'montant': 100.0}],
}


class ExtractInvoiceTests(TestCase):
    @patch('ai.services.ocr.requests.post')
    @patch('ai.services.ocr.pytesseract.image_to_string')
    def test_consistent_invoice_does_not_need_review(self, mock_ocr, mock_post):
        mock_ocr.return_value = 'ACME SARL\nFacture F-2026-001\nTotal TTC 120.00'
        mock_post.return_value = _fake_ollama_response(json.dumps(CONSISTENT_PAYLOAD))

        result = extract_invoice(_tiny_png_bytes(), 'image/jpeg')

        self.assertFalse(result['needs_review'])
        self.assertEqual(result['extracted_data']['fournisseur'], 'ACME SARL')
        self.assertEqual(result['extracted_data']['montant_ttc'], 120.0)
        self.assertEqual(result['extracted_data']['doc_type'], 'invoice')

    @patch('ai.services.ocr.requests.post')
    @patch('ai.services.ocr.pytesseract.image_to_string')
    def test_arithmetic_mismatch_flags_for_review(self, mock_ocr, mock_post):
        mock_ocr.return_value = 'ACME SARL\nFacture F-2026-001'
        payload = dict(CONSISTENT_PAYLOAD)
        payload['montant_ttc'] = 999.0  # inconsistent with montant_ht + montant_tva
        mock_post.return_value = _fake_ollama_response(json.dumps(payload))

        result = extract_invoice(_tiny_png_bytes(), 'image/jpeg')

        self.assertTrue(result['needs_review'])
        self.assertLess(result['field_confidence']['montant_ttc'], 0.7)

    @patch('ai.services.ocr.requests.post')
    @patch('ai.services.ocr.pytesseract.image_to_string')
    def test_missing_field_flags_for_review(self, mock_ocr, mock_post):
        mock_ocr.return_value = 'ACME SARL, montant illisible'
        payload = dict(CONSISTENT_PAYLOAD)
        payload['numero'] = None
        mock_post.return_value = _fake_ollama_response(json.dumps(payload))

        result = extract_invoice(_tiny_png_bytes(), 'image/jpeg')

        self.assertTrue(result['needs_review'])
        self.assertEqual(result['field_confidence']['numero'], 0.0)

    @patch('ai.services.ocr.requests.post')
    @patch('ai.services.ocr.pytesseract.image_to_string')
    def test_invalid_json_raises_extraction_error(self, mock_ocr, mock_post):
        mock_ocr.return_value = 'some ocr text'
        mock_post.return_value = _fake_ollama_response('this is not json')

        with self.assertRaises(OCRExtractionError):
            extract_invoice(_tiny_png_bytes(), 'image/jpeg')

    @patch('ai.services.ocr.pytesseract.image_to_string')
    def test_no_text_detected_raises(self, mock_ocr):
        mock_ocr.return_value = '   '

        with self.assertRaises(OCRExtractionError):
            extract_invoice(_tiny_png_bytes(), 'image/jpeg')

    @patch('ai.services.ocr.requests.post')
    @patch('ai.services.ocr.pytesseract.image_to_string')
    def test_ollama_unreachable_raises(self, mock_ocr, mock_post):
        mock_ocr.return_value = 'ACME SARL'
        mock_post.side_effect = requests.ConnectionError('connection refused')

        with self.assertRaises(OCRExtractionError):
            extract_invoice(_tiny_png_bytes(), 'image/jpeg')

    def test_pdf_not_supported_raises(self):
        with self.assertRaises(OCRExtractionError):
            extract_invoice(b'%PDF-fake', 'application/pdf')

    @patch('ai.services.ocr.requests.post')
    @patch('ai.services.ocr.pytesseract.image_to_string')
    def test_pattern_match_overrides_wrong_llm_amount(self, mock_ocr, mock_post):
        # Real invoice layouts put a tax *rate* next to the tax *amount* on the same line —
        # the pattern matcher must pick the amount (9.06), not the rate (6.25), and its result
        # should win over an LLM guess that got it wrong.
        mock_ocr.return_value = 'Subtotal 145.00\nSales Tax 6.25% 9.06\nTOTAL $154.06'
        payload = dict(CONSISTENT_PAYLOAD)
        payload['montant_ht'] = None
        payload['montant_tva'] = 6.25  # wrong: this is the LLM mistaking the rate for the amount
        payload['montant_ttc'] = 999.0  # wrong, to prove the pattern match wins independently
        payload['lignes'] = [{'description': 'Service A', 'quantite': 1, 'prix_unitaire': 145.0, 'montant': 145.0}]
        mock_post.return_value = _fake_ollama_response(json.dumps(payload))

        result = extract_invoice(_tiny_png_bytes(), 'image/jpeg')

        self.assertEqual(result['extracted_data']['montant_ht'], 145.0)
        self.assertEqual(result['extracted_data']['montant_tva'], 9.06)
        self.assertEqual(result['extracted_data']['montant_ttc'], 154.06)
        self.assertEqual(result['field_confidence']['montant_tva'], 0.95)
        self.assertFalse(result['needs_review'])


class ExtractAmountsByPatternTests(TestCase):
    def test_finds_all_three_amounts(self):
        text = 'East Repair Inc.\nSubtotal 145.00\nSales Tax 6.25% 9.06\nTOTAL $154.06'
        result = _extract_amounts_by_pattern(text)
        self.assertEqual(result, {'montant_ht': 145.0, 'montant_tva': 9.06, 'montant_ttc': 154.06})

    def test_does_not_confuse_subtotal_with_total(self):
        text = 'Subtotal 145.00\nTOTAL $154.06'
        result = _extract_amounts_by_pattern(text)
        self.assertEqual(result['montant_ht'], 145.0)
        self.assertEqual(result['montant_ttc'], 154.06)

    def test_ignores_percentage_and_takes_amount(self):
        text = 'TVA 20% 145.00'
        result = _extract_amounts_by_pattern(text)
        self.assertEqual(result['montant_tva'], 145.0)

    def test_french_decimal_comma(self):
        text = 'Montant HT 145,00\nMontant TTC 174,00'
        result = _extract_amounts_by_pattern(text)
        self.assertEqual(result['montant_ht'], 145.0)
        self.assertEqual(result['montant_ttc'], 174.0)

    def test_no_labels_found_returns_none(self):
        text = 'some unrelated text with 42 in it'
        result = _extract_amounts_by_pattern(text)
        self.assertEqual(result, {'montant_ht': None, 'montant_tva': None, 'montant_ttc': None})


class PromoteFieldsTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name='Test Co', email='test@example.com')

    def _document(self, extracted_data):
        return Document.objects.create(company=self.company, extracted_data=extracted_data)

    def test_promotes_valid_fields(self):
        doc = self._document({
            'doc_type': 'invoice', 'langue': 'en', 'fournisseur': 'ACME SARL',
            'date': '2026-06-01', 'numero': 'F-2026-001', 'montant_ttc': 120.5,
        })
        doc.promote_fields()

        self.assertEqual(doc.doc_type, 'invoice')
        self.assertEqual(doc.langue, 'en')
        self.assertEqual(doc.fournisseur, 'ACME SARL')
        self.assertEqual(doc.date, date(2026, 6, 1))
        self.assertEqual(doc.numero, 'F-2026-001')
        self.assertEqual(doc.montant_ttc, Decimal('120.5'))

    def test_invalid_doc_type_and_langue_become_none(self):
        doc = self._document({'doc_type': 'not-a-real-type', 'langue': 'klingon'})
        doc.promote_fields()

        self.assertIsNone(doc.doc_type)
        self.assertIsNone(doc.langue)

    def test_unparseable_date_stays_none(self):
        doc = self._document({'date': 'sometime last week'})
        doc.promote_fields()

        self.assertIsNone(doc.date)

    def test_unparseable_amount_stays_none(self):
        doc = self._document({'montant_ttc': 'not a number'})
        doc.promote_fields()

        self.assertIsNone(doc.montant_ttc)

    def test_missing_extracted_data_does_not_raise(self):
        doc = self._document(None)
        doc.promote_fields()  # should not raise

        self.assertIsNone(doc.doc_type)
        self.assertIsNone(doc.montant_ttc)


def _xlsx_bytes(headers, rows):
    """Builds a minimal in-memory .xlsx — no fixture file needed, no mocking needed either
    since this exercises the real openpyxl/pandas parsing path directly."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(headers)
    for row in rows:
        ws.append(row)
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


class ParseSpreadsheetTests(TestCase):
    def test_parses_headers_and_rows(self):
        content = _xlsx_bytes(
            ['Nom du produit', 'Prix'],
            [['Vis 4mm', 0.5], ['Ecrou 4mm', 0.3]],
        )
        headers, rows = parse_spreadsheet(content)

        self.assertEqual(headers, ['Nom du produit', 'Prix'])
        self.assertEqual(rows, [
            {'Nom du produit': 'Vis 4mm', 'Prix': 0.5},
            {'Nom du produit': 'Ecrou 4mm', 'Prix': 0.3},
        ])

    def test_missing_cells_become_none(self):
        content = _xlsx_bytes(['A', 'B'], [['x', None]])
        _, rows = parse_spreadsheet(content)
        self.assertIsNone(rows[0]['B'])

    def test_empty_sheet_raises(self):
        content = _xlsx_bytes(['A', 'B'], [])
        with self.assertRaises(SpreadsheetError):
            parse_spreadsheet(content)

    def test_invalid_file_raises(self):
        with self.assertRaises(SpreadsheetError):
            parse_spreadsheet(b'this is not a real xlsx file')


class ApplyMappingTests(TestCase):
    def test_renames_keys_per_mapping(self):
        rows = [{'Nom': 'Vis', 'Prix EUR': 0.5}]
        mapping = [
            {'source_column': 'Nom', 'field_name': 'product_name', 'label': 'Nom'},
            {'source_column': 'Prix EUR', 'field_name': 'unit_price', 'label': 'Prix'},
        ]
        result = apply_mapping(rows, mapping)
        self.assertEqual(result, [{'product_name': 'Vis', 'unit_price': 0.5}])

    def test_ignored_column_is_dropped(self):
        rows = [{'Nom': 'Vis', 'Notes internes': 'secret'}]
        mapping = [
            {'source_column': 'Nom', 'field_name': 'product_name', 'label': 'Nom'},
            {'source_column': 'Notes internes', 'field_name': None, 'label': 'Notes internes'},
        ]
        result = apply_mapping(rows, mapping)
        self.assertEqual(result, [{'product_name': 'Vis'}])


class ProposeMappingTests(TestCase):
    @patch('ai.services.spreadsheet.requests.post')
    def test_valid_model_response_is_used_as_is(self, mock_post):
        payload = {
            'data_type': 'products',
            'columns': [
                {'source_column': 'Nom du produit', 'field_name': 'product_name', 'label': 'Nom du produit'},
                {'source_column': 'Prix', 'field_name': 'unit_price', 'label': 'Prix'},
            ],
        }
        mock_post.return_value = _fake_ollama_response(json.dumps(payload))

        result = propose_mapping(['Nom du produit', 'Prix'], [{'Nom du produit': 'Vis', 'Prix': 0.5}])

        self.assertEqual(result['data_type'], 'products')
        self.assertEqual(result['columns'][0]['field_name'], 'product_name')
        self.assertEqual(result['columns'][1]['field_name'], 'unit_price')

    @patch('ai.services.spreadsheet.requests.post')
    def test_malformed_response_falls_back_to_slugified_headers(self, mock_post):
        mock_post.return_value = _fake_ollama_response('this is not json')

        result = propose_mapping(['Nom du Produit!', 'Prix (EUR)'], [])

        self.assertEqual(result['data_type'], 'other')
        self.assertEqual(result['columns'][0]['field_name'], 'nom_du_produit')
        self.assertEqual(result['columns'][1]['field_name'], 'prix_eur')

    @patch('ai.services.spreadsheet.requests.post')
    def test_wrong_column_count_falls_back(self, mock_post):
        # Model only returned one column mapping for two headers — must not silently misalign.
        payload = {'data_type': 'products', 'columns': [{'source_column': 'A', 'field_name': 'a', 'label': 'A'}]}
        mock_post.return_value = _fake_ollama_response(json.dumps(payload))

        result = propose_mapping(['A', 'B'], [])

        self.assertEqual(len(result['columns']), 2)

    @patch('ai.services.spreadsheet.requests.post')
    def test_ollama_unreachable_raises(self, mock_post):
        mock_post.side_effect = requests.ConnectionError('connection refused')
        with self.assertRaises(SpreadsheetError):
            propose_mapping(['A'], [])


class SpreadsheetImportViewTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name='Test Co', email='test@example.com')

    @patch('ai.services.spreadsheet.requests.post')
    def test_upload_then_confirm_full_flow(self, mock_post):
        payload = {
            'data_type': 'products',
            'columns': [
                {'source_column': 'Nom du produit', 'field_name': 'product_name', 'label': 'Nom du produit'},
                {'source_column': 'Prix', 'field_name': 'unit_price', 'label': 'Prix'},
            ],
        }
        mock_post.return_value = _fake_ollama_response(json.dumps(payload))

        content = _xlsx_bytes(['Nom du produit', 'Prix'], [['Vis 4mm', 0.5], ['Ecrou 4mm', 0.3]])
        upload = SimpleUploadedFile(
            'products.xlsx', content,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )

        response = self.client.post('/api/ai/spreadsheets/', {'company': self.company.id, 'file': upload})
        self.assertEqual(response.status_code, 201)
        body = response.json()
        self.assertEqual(body['status'], 'mapped')
        self.assertEqual(body['data_type'], 'products')
        self.assertEqual(body['row_count'], 2)
        self.assertIsNone(body['normalized_rows'])

        import_id = body['id']
        confirm_response = self.client.post(f'/api/ai/spreadsheets/{import_id}/confirm/')
        self.assertEqual(confirm_response.status_code, 200)
        confirmed = confirm_response.json()
        self.assertEqual(confirmed['status'], 'confirmed')
        self.assertFalse(confirmed['needs_review'])
        self.assertEqual(confirmed['normalized_rows'], [
            {'product_name': 'Vis 4mm', 'unit_price': 0.5},
            {'product_name': 'Ecrou 4mm', 'unit_price': 0.3},
        ])

    @patch('ai.services.spreadsheet.requests.post')
    def test_corrected_mapping_is_applied_on_confirm(self, mock_post):
        payload = {
            'data_type': 'other',
            'columns': [{'source_column': 'Nom', 'field_name': 'wrong_name', 'label': 'Nom'}],
        }
        mock_post.return_value = _fake_ollama_response(json.dumps(payload))

        content = _xlsx_bytes(['Nom'], [['Vis 4mm']])
        upload = SimpleUploadedFile('p.xlsx', content)
        response = self.client.post('/api/ai/spreadsheets/', {'company': self.company.id, 'file': upload})
        import_id = response.json()['id']

        # Human corrects the AI's proposed field_name before confirming.
        patch_response = self.client.patch(
            f'/api/ai/spreadsheets/{import_id}/',
            data=json.dumps({'column_mapping': [
                {'source_column': 'Nom', 'field_name': 'product_name', 'label': 'Nom'},
            ]}),
            content_type='application/json',
        )
        self.assertEqual(patch_response.status_code, 200)

        confirm_response = self.client.post(f'/api/ai/spreadsheets/{import_id}/confirm/')
        self.assertEqual(confirm_response.json()['normalized_rows'], [{'product_name': 'Vis 4mm'}])


def _synthetic_history(num_days, start_value=1000.0, daily_growth=5.0, weekly_amplitude=50.0):
    history = []
    start = date(2026, 1, 1)
    for i in range(num_days):
        d = start + timedelta(days=i)
        seasonal = weekly_amplitude * math.sin(2 * math.pi * (i % 7) / 7)
        amount = start_value + daily_growth * i + seasonal
        history.append({'date': d.strftime('%Y-%m-%d'), 'amount': amount})
    return history


class ForecastCashflowTests(TestCase):
    def test_insufficient_history_raises(self):
        with self.assertRaises(InsufficientHistoryError):
            forecast_cashflow(_synthetic_history(5), horizon_days=7)

    def test_forecast_shape(self):
        result = forecast_cashflow(_synthetic_history(60), horizon_days=14)

        self.assertEqual(len(result['forecast']), 14)
        self.assertEqual(len(result['baseline']), 14)
        self.assertTrue(result['indicative_only'])
        first_point = result['forecast'][0]
        self.assertIn('yhat', first_point)
        self.assertIn('yhat_lower', first_point)
        self.assertIn('yhat_upper', first_point)

    def test_forecast_beats_moving_average_baseline_on_trend_data(self):
        horizon = 14
        full_history = _synthetic_history(90 + horizon)
        train, held_out = full_history[:90], full_history[90:]

        result = forecast_cashflow(train, horizon_days=horizon)

        actual = [point['amount'] for point in held_out]
        model_predictions = [point['yhat'] for point in result['forecast']]
        baseline_predictions = [point['amount'] for point in result['baseline']]

        model_mae = sum(abs(a - p) for a, p in zip(actual, model_predictions)) / horizon
        baseline_mae = sum(abs(a - b) for a, b in zip(actual, baseline_predictions)) / horizon

        self.assertLess(model_mae, baseline_mae)
