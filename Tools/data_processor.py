"""
ZENITH Data Processor Tool
Provides: csv_analyze, json_parse, csv_filter, csv_sort, data_statistics, csv_to_json
"""

import csv
import json
import os
import math
from typing import Optional
from livekit.agents import function_tool

TOOL = {
    "name": "data_processor",
    "description": "Analyze, filter, sort, and convert CSV and JSON data files. Use when the user wants to work with structured data files like CSV or JSON.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {"type": "STRING", "description": "Action: 'csv_analyze', 'json_parse', 'csv_filter', 'csv_sort', 'data_statistics', 'csv_to_json'"},
            "file_path": {"type": "STRING", "description": "Path to the CSV or JSON file"},
            "column": {"type": "STRING", "description": "Column name for filtering or sorting"},
            "condition": {"type": "STRING", "description": "Filter condition (e.g. '>5', '==value', 'contains text')"},
            "descending": {"type": "BOOLEAN", "description": "Sort in descending order (default: false)"},
            "output_path": {"type": "STRING", "description": "Output file path (optional)"}
        },
        "required": ["action", "file_path"]
    },
    "handler": "csv_analyze",
}


@function_tool()
async def csv_analyze(file_path: str) -> str:
    """Read and summarize a CSV file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            headers = next(reader, None)
            rows = list(reader)

        lines = [f"CSV: {os.path.basename(file_path)}"]
        lines.append(f"  Rows: {len(rows)}, Columns: {len(headers)}")
        lines.append(f"  Headers: {', '.join(headers)}")
        if rows:
            lines.append(f"  First row: {', '.join(rows[0][:5])}")
        return "\n".join(lines)
    except Exception as e:
        return f"Error: {str(e)}"


@function_tool()
async def json_parse(file_path: str) -> str:
    """Parse and summarize a JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if isinstance(data, list):
            return f"JSON Array: {len(data)} items"
        elif isinstance(data, dict):
            return f"JSON Object: {len(data)} keys: {', '.join(list(data.keys())[:10])}"
        else:
            return f"JSON: {type(data).__name__}"
    except Exception as e:
        return f"Error: {str(e)}"


@function_tool()
async def csv_filter(file_path: str, column: str, condition: str, output_path: str = "") -> str:
    """Filter CSV rows. condition: '>5', '<10', '==value', 'contains text'"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames
            if column not in headers:
                return f"Column '{column}' not found. Available: {', '.join(headers)}"

            filtered = []
            for row in reader:
                val = row[column]
                if condition.startswith('>'):
                    try:
                        if float(val) > float(condition[1:]):
                            filtered.append(row)
                    except ValueError:
                        pass
                elif condition.startswith('<'):
                    try:
                        if float(val) < float(condition[1:]):
                            filtered.append(row)
                    except ValueError:
                        pass
                elif condition.startswith('=='):
                    if val == condition[2:].strip():
                        filtered.append(row)
                elif condition.startswith('contains'):
                    if condition[8:].strip().lower() in val.lower():
                        filtered.append(row)
                else:
                    if val == condition:
                        filtered.append(row)

        if not output_path:
            output_path = file_path.replace('.csv', '_filtered.csv')

        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(filtered)

        return f"Filtered {len(filtered)} rows ({column} {condition}) -> {output_path}"
    except Exception as e:
        return f"Error: {str(e)}"


@function_tool()
async def csv_sort(file_path: str, column: str, descending: bool = False, output_path: str = "") -> str:
    """Sort CSV by a column."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames
            rows = list(reader)

        if column not in headers:
            return f"Column '{column}' not found. Available: {', '.join(headers)}"

        def sort_key(row):
            try:
                return float(row[column])
            except (ValueError, TypeError):
                return row[column]

        rows.sort(key=sort_key, reverse=descending)

        if not output_path:
            output_path = file_path.replace('.csv', '_sorted.csv')

        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(rows)

        return f"Sorted {len(rows)} rows by '{column}' -> {output_path}"
    except Exception as e:
        return f"Error: {str(e)}"


@function_tool()
async def data_statistics(file_path: str) -> str:
    """Calculate statistics for all numeric columns in a CSV."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames
            rows = list(reader)

        results = []
        for col in headers:
            values = []
            for row in rows:
                try:
                    values.append(float(row[col]))
                except (ValueError, TypeError, KeyError):
                    continue

            if not values:
                continue

            n = len(values)
            mean = sum(values) / n
            variance = sum((x - mean) ** 2 for x in values) / n
            std_dev = math.sqrt(variance)
            sorted_vals = sorted(values)
            median = sorted_vals[n // 2] if n % 2 else (sorted_vals[n // 2 - 1] + sorted_vals[n // 2]) / 2

            results.append(f"  {col}: mean={mean:.2f}, median={median:.2f}, std={std_dev:.2f}, min={min(values):.2f}, max={max(values):.2f}")

        if not results:
            return "No numeric columns found."

        return "Statistics:\n" + "\n".join(results)
    except Exception as e:
        return f"Error: {str(e)}"


@function_tool()
async def csv_to_json(file_path: str, output_path: str = "") -> str:
    """Convert a CSV file to JSON."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            data = list(reader)

        if not output_path:
            output_path = file_path.replace('.csv', '.json')

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

        return f"Converted {len(data)} rows to {output_path}"
    except Exception as e:
        return f"Error: {str(e)
}"
