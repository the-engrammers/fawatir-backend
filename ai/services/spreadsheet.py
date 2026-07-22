import io
import json
import re

import pandas as pd
import requests
from django.conf import settings

MAX_PROMPT_ROWS = 5  # sample rows shown to the model for context

MAPPING_PROMPT_TEMPLATE = """Tu es un moteur d'analyse de fichiers Excel utilises par des PME \
(listes de produits, fournisseurs, clients, stocks, etc.), en francais, anglais ou arabe.

Voici les en-tetes de colonnes du fichier, suivies de quelques lignes d'exemple :

<en_tetes>
{headers}
</en_tetes>

<exemples>
{sample_rows}
</exemples>

Analyse ce contenu et renvoie UNIQUEMENT un objet JSON strict (aucun texte autour, aucun bloc \
markdown), avec exactement cette forme :

{{
  "data_type": string (court, ex: "products", "suppliers", "clients", "inventory", "other"),
  "columns": [
    {{
      "source_column": string (recopie exactement l'en-tete d'origine),
      "field_name": string (nom technique propre, en anglais, snake_case, ex: "unit_price") ou null si la colonne doit etre ignoree,
      "label": string (libelle humain, peut garder la langue d'origine)
    }}
  ]
}}

Il doit y avoir exactement un objet dans "columns" pour CHAQUE en-tete fourni, dans le meme ordre. \
Utilise le contenu des exemples pour deviner le sens d'une colonne si son en-tete est ambigu ou \
abrege (ex: une colonne de nombres comme "5.99, 12.50, 3.00" est probablement un prix). \
N'utilise jamais un field_name qui n'est pas un identifiant valide (minuscules, chiffres, \
underscores uniquement)."""


class SpreadsheetError(Exception):
    pass


def _to_native(value):
    """Converts a pandas/numpy scalar to a plain JSON-serializable Python value."""
    if pd.isna(value):
        return None
    if hasattr(value, 'item'):  # numpy scalar (int64, float64, bool_, ...)
        value = value.item()
    if isinstance(value, pd.Timestamp):
        return value.strftime('%Y-%m-%d')
    return value


def parse_spreadsheet(file_bytes):
    """Reads the first sheet of an Excel file.

    Returns (headers, rows) — rows is a list of dicts keyed by the ORIGINAL column headers,
    with values converted to plain JSON-serializable Python types.
    """
    try:
        df = pd.read_excel(io.BytesIO(file_bytes), sheet_name=0, engine='openpyxl')
    except Exception as exc:
        raise SpreadsheetError(f'Could not read spreadsheet: {exc}') from exc

    if df.empty:
        raise SpreadsheetError('The spreadsheet has no data rows')

    headers = [str(c) for c in df.columns]
    rows = [
        {header: _to_native(value) for header, value in zip(headers, record)}
        for record in df.itertuples(index=False, name=None)
    ]
    return headers, rows


def _parse_json_response(text):
    cleaned = text.strip()
    cleaned = re.sub(r'^```(json)?', '', cleaned).strip()
    cleaned = re.sub(r'```$', '', cleaned).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise SpreadsheetError(f'Local model did not return valid JSON: {exc}') from exc


def _slugify(text):
    slug = re.sub(r'[^a-z0-9]+', '_', str(text).strip().lower()).strip('_')
    return slug or 'column'


def _fallback_columns(headers):
    """Used when the model's response is malformed — a plain slugified mapping is still
    usable (just less semantically meaningful) rather than failing the whole request."""
    seen = set()
    columns = []
    for header in headers:
        field_name = _slugify(header)
        if field_name in seen:
            field_name = f'{field_name}_{len(seen)}'
        seen.add(field_name)
        columns.append({'source_column': header, 'field_name': field_name, 'label': header})
    return columns


def _validate_columns(headers, columns):
    if not isinstance(columns, list) or len(columns) != len(headers):
        return None

    seen = set()
    result = []
    for header, col in zip(headers, columns):
        if not isinstance(col, dict):
            return None
        field_name = col.get('field_name')
        if field_name:
            field_name = re.sub(r'[^a-z0-9_]', '_', str(field_name).lower()).strip('_') or None
        if field_name:
            while field_name in seen:
                field_name = f'{field_name}_2'
            seen.add(field_name)
        label = col.get('label') or header
        result.append({'source_column': header, 'field_name': field_name, 'label': label})
    return result


def propose_mapping(headers, sample_rows):
    """Asks the local model to classify the data and propose a clean column mapping.

    Never raises on a malformed model response — falls back to a slugified mapping instead,
    since the human review step (not this function) is the real safety net.
    """
    prompt = MAPPING_PROMPT_TEMPLATE.format(
        headers=json.dumps(headers, ensure_ascii=False),
        sample_rows=json.dumps(sample_rows[:MAX_PROMPT_ROWS], ensure_ascii=False, default=str),
    )
    url = f'{settings.OLLAMA_BASE_URL}/api/generate'
    payload = {
        'model': settings.OLLAMA_MODEL,
        'prompt': prompt,
        'format': 'json',
        'stream': False,
        'options': {'temperature': 0},
    }
    try:
        response = requests.post(url, json=payload, timeout=300)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise SpreadsheetError(f'Ollama request failed (is `ollama serve` running?): {exc}') from exc

    try:
        parsed = _parse_json_response(response.json().get('response', ''))
    except SpreadsheetError:
        parsed = None

    data_type = parsed.get('data_type') if isinstance(parsed, dict) else None
    columns = _validate_columns(headers, parsed.get('columns') if isinstance(parsed, dict) else None)
    if columns is None:
        columns = _fallback_columns(headers)

    return {'data_type': data_type or 'other', 'columns': columns}


def apply_mapping(rows, column_mapping):
    """Renames every row's keys per column_mapping; columns with no field_name are dropped."""
    normalized = []
    for row in rows:
        new_row = {}
        for col in column_mapping:
            field_name = col.get('field_name')
            if field_name:
                new_row[field_name] = row.get(col['source_column'])
        normalized.append(new_row)
    return normalized
