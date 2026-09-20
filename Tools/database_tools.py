"""
ZENITH Database Tool (SQLite)
Provides: query, create_table, insert, select, export, list_tables
"""

import sqlite3
import csv
import json
import os
from typing import Optional
from livekit.agents import function_tool

TOOL = {
    "name": "database_tools",
    "description": "Manage SQLite databases: run queries, create tables, insert/select data, and export results. Use when the user wants to work with SQLite database operations.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {"type": "STRING", "description": "Action: 'query', 'create_table', 'insert', 'select', 'list_tables', 'export'"},
            "db_path": {"type": "STRING", "description": "Path to the SQLite database file"},
            "table_name": {"type": "STRING", "description": "Table name for table operations"},
            "query": {"type": "STRING", "description": "SQL query to execute"},
            "columns": {"type": "STRING", "description": "Column definitions for create_table (e.g. 'name TEXT, age INTEGER')"},
            "values": {"type": "STRING", "description": "Values for insert (e.g. 'John, 25, john@email.com')"},
            "where": {"type": "STRING", "description": "WHERE clause for select"},
            "limit": {"type": "INTEGER", "description": "Row limit for select (default: 50)"}
        },
        "required": ["action", "db_path"]
    },
    "handler": "sqlite_query",
}


def _get_conn(db_path: str) -> sqlite3.Connection:
    return sqlite3.connect(db_path)


@function_tool()
async def sqlite_query(db_path: str, query: str) -> str:
    """Execute any SQL query and return results."""
    try:
        conn = _get_conn(db_path)
        cursor = conn.cursor()
        cursor.execute(query)

        if query.strip().upper().startswith(("INSERT", "UPDATE", "DELETE", "CREATE", "DROP", "ALTER")):
            conn.commit()
            result = f"Query executed. Rows affected: {cursor.rowcount}"
        else:
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            if not rows:
                result = "No results found."
            else:
                lines = [" | ".join(str(c) for c in columns)]
                lines.append("-" * len(lines[0]))
                for row in rows[:100]:
                    lines.append(" | ".join(str(v) for v in row))
                if len(rows) > 100:
                    lines.append(f"... and {len(rows) - 100} more rows")
                result = "\n".join(lines)

        conn.close()
        return result
    except Exception as e:
        return f"SQL Error: {str(e)}"


@function_tool()
async def sqlite_create_table(db_path: str, table_name: str, columns: str) -> str:
    """Create a table. columns format: 'name TEXT, age INTEGER, email TEXT'"""
    try:
        conn = _get_conn(db_path)
        cursor = conn.cursor()
        cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})")
        conn.commit()
        conn.close()
        return f"Table '{table_name}' created with columns: {columns}"
    except Exception as e:
        return f"Error: {str(e)}"


@function_tool()
async def sqlite_insert(db_path: str, table_name: str, values: str) -> str:
    """Insert a row. values format: 'John, 25, john@example.com'"""
    try:
        conn = _get_conn(db_path)
        cursor = conn.cursor()
        cols = cursor.execute(f"PRAGMA table_info({table_name})").fetchall()
        num_cols = len(cols)
        placeholders = ", ".join(["?" for _ in range(num_cols)])
        vals = [v.strip() for v in values.split(",")]
        cursor.execute(f"INSERT INTO {table_name} VALUES ({placeholders})", vals[:num_cols])
        conn.commit()
        conn.close()
        return f"Inserted into '{table_name}': {values}"
    except Exception as e:
        return f"Error: {str(e)}"


@function_tool()
async def sqlite_select(db_path: str, table_name: str, where: str = "", limit: int = 50) -> str:
    """Select data from a table with optional WHERE clause."""
    query = f"SELECT * FROM {table_name}"
    if where:
        query += f" WHERE {where}"
    query += f" LIMIT {limit}"
    return await sqlite_query(db_path, query)


@function_tool()
async def sqlite_list_tables(db_path: str) -> str:
    """List all tables in the database."""
    try:
        conn = _get_conn(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        conn.close()
        if not tables:
            return "No tables found."
        return "Tables:\n" + "\n".join(f"  - {t[0]}" for t in tables)
    except Exception as e:
        return f"Error: {str(e)}"


@function_tool()
async def sqlite_export_csv(db_path: str, table_name: str, output_path: str = "") -> str:
    """Export a table to CSV file."""
    try:
        conn = _get_conn(db_path)
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        conn.close()

        if not output_path:
            output_path = f"{table_name}_export.csv"

        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(columns)
            writer.writerows(rows)

        return f"Exported {len(rows)} rows to {output_path}"
    except Exception as e:
        return f"Error: {str(e)
}"
