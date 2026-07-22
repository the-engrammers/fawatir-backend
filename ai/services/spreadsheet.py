import io
import json
import re
from typing import Optional

import pandas as pd
from django.conf import settings
import google.generativeai as genai
from pydantic import BaseModel, Field

from pydantic import BaseModel, Field
from typing import Optional, Literal

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

Analyse ce contenu et renvoie un objet JSON decrivant le type de donnees et le mapping. \
Il doit y avoir exactement un objet dans "columns" pour CHAQUE en-tete fourni, dans le meme ordre. \
Utilise le contenu des exemples pour deviner le sens d'une colonne si son en-tete est ambigu ou \
abrege (ex: une colonne de nombres comme "5.99, 12.50, 3.00" est probablement un prix). \
N'utilise jamais un field_name qui n'est pas un identifiant valide (minuscules, chiffres, \
underscores uniquement)."""


class ColumnMapping(BaseModel):
    source_column: str = Field(description="Exact original header")
    field_name: Optional[str] = Field(description="Snake_case technical name or null if ignored")
    label: str = Field(description="Human readable label")

class MappingResponse(BaseModel):
    data_type: Literal['products', 'suppliers', 'clients', 'inventory', 'other'] = Field(description="Classification")
    columns: list[ColumnMapping]


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


def propose_mapping(headers, sample_rows):
    """Asks the Gemini model to classify the data and propose a clean column mapping.

    Never raises on a malformed model response — falls back to a slugified mapping instead,
    since the human review step (not this function) is the real safety net.
    """
    if not settings.GEMINI_API_KEY:
        # Fallback to simple slugification if API key is not configured
        return {'data_type': 'other', 'columns': _fallback_columns(headers)}

    genai.configure(api_key=settings.GEMINI_API_KEY, transport="rest")
    model = genai.GenerativeModel('gemini-flash-latest')

    prompt = MAPPING_PROMPT_TEMPLATE.format(
        headers=json.dumps(headers, ensure_ascii=False),
        sample_rows=json.dumps(sample_rows[:MAX_PROMPT_ROWS], ensure_ascii=False, default=str),
    )

    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                response_schema=MappingResponse,
                temperature=0.0,
            )
        )
        parsed = json.loads(response.text)
    except Exception:
        # Silently catch exceptions to fallback safely instead of crashing the UI
        parsed = None

    data_type = parsed.get('data_type') if isinstance(parsed, dict) else None
    columns = parsed.get('columns') if isinstance(parsed, dict) else None

    # Guarantee uniqueness of field_names
    if isinstance(columns, list):
        seen = set()
        clean_columns = []
        for col in columns:
            if not isinstance(col, dict):
                continue
            field_name = col.get('field_name')
            if field_name:
                field_name = re.sub(r'[^a-z0-9_]', '_', str(field_name).lower()).strip('_') or None
            if field_name:
                while field_name in seen:
                    field_name = f'{field_name}_2'
                seen.add(field_name)
            
            clean_columns.append({
                'source_column': col.get('source_column'),
                'field_name': field_name,
                'label': col.get('label')
            })
        columns = clean_columns

    if not columns or len(columns) != len(headers):
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
