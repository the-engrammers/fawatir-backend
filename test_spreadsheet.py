import os
import django
import sys
import pandas as pd
import io

sys.path.append(r'c:\Users\Lenovo\Downloads\FAWATIR\fawatir-backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fawatir_backend.settings')
django.setup()

from ai.services.spreadsheet import parse_spreadsheet, propose_mapping, apply_mapping

def create_mock_excel() -> bytes:
    df = pd.DataFrame({
        "Réf. Produit": ["P-001", "P-002", "P-003"],
        "Désignation": ["Laptop Dell", "Souris Logitech", "Clavier mécanique"],
        "Prix Unitaire (DH)": [8500.0, 150.0, 450.0],
        "En stock": [12, 50, 30]
    })
    
    excel_buffer = io.BytesIO()
    df.to_excel(excel_buffer, index=False)
    return excel_buffer.getvalue()

def run_test():
    print("Generating mock Excel file...")
    excel_bytes = create_mock_excel()
    
    print("Parsing Excel file...")
    headers, rows = parse_spreadsheet(excel_bytes)
    print(f"Found headers: {headers}")
    print(f"Found {len(rows)} rows. Sample: {rows[0]}")
    
    print("\nRequesting AI mapping proposal from Gemini...")
    mapping_result = propose_mapping(headers, rows)
    
    print(f"\nAI Data Type Classification: {mapping_result['data_type']}")
    print("AI Column Mapping:")
    for col in mapping_result['columns']:
        print(f"  - {col['source_column']} -> {col['field_name']} (Label: {col['label']})")
        
    print("\nApplying Mapping to rows...")
    normalized = apply_mapping(rows, mapping_result['columns'])
    print(f"Normalized Row 1: {normalized[0]}")

if __name__ == "__main__":
    run_test()
