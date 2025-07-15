import os
import json
import csv
import openpyxl

REQUIRED_FIELDS = ["CVEID", "KBID", "Severity", "AffectedPackage"]

def detect_type(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext not in [".xlsx", ".csv", ".json"]:
        raise ValueError(f"Unsupported file type: {ext}")
    return ext

def validate_fields(headers):
    missing = [f for f in REQUIRED_FIELDS if f not in headers]
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")

def parse_excel(file_path):
    wb = openpyxl.load_workbook(file_path)
    sheet = wb.active
    rows = list(sheet.iter_rows(values_only=True))
    headers = [str(h).strip() for h in rows[0]]
    validate_fields(headers)
    return [dict(zip(headers, r)) for r in rows[1:] if any(r)]

def parse_csv(file_path):
    with open(file_path, newline='', encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        validate_fields(reader.fieldnames)
        return list(reader)

def parse_json(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        if isinstance(data, dict):
            data = [data]
        validate_fields(data[0].keys())
        return data

def parse_report(file_path):
    ext = detect_type(file_path)
    if ext == ".xlsx":
        return parse_excel(file_path)
    elif ext == ".csv":
        return parse_csv(file_path)
    elif ext == ".json":
        return parse_json(file_path)
