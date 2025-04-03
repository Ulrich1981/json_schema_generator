#!/usr/bin/env python3

"""
JSON Schema Generator

This script takes a JSON file and generates a skeleton for the JSON schema,
saving the output to a new file with `.schema.json` extension.

Usage:
    python json_schema_generator.py <input_file>

Dependencies:
    - `click` module (install via `pip install click`)
"""

import json
import click
from itertools import chain

class MixedType:
    """Represents mixed types in schema inference."""
    pass

@click.group()
def cli():
    pass

def extract_unique_types(lst):
    """Extract unique types from a list."""
    return list(set(type(x).__name__ for x in lst))

def merge_nested_dicts(dict_list):
    """Merge multiple dictionaries while handling nested structures sensibly."""
    merged = {}
    for d in dict_list:
        for key, value in d.items():
            if key in merged:
                if isinstance(merged[key], dict) and isinstance(value, dict):
                    merged[key] = merge_nested_dicts([merged[key], value])  # Merge nested dicts
                elif isinstance(merged[key], list) and isinstance(value, list):
                    merged[key].extend(value)  # Merge lists efficiently
                elif isinstance(merged[key], list) != isinstance(value, list):
                    merged[key] = MixedType()  # Handle type mismatches
            else:
                merged[key] = value
    return merged

def infer_dict_schema(data):
    """Generate a schema representation for a dictionary."""
    return {key: infer_schema(value) for key, value in data.items()}

def infer_list_schema(lst):
    """Generate a schema representation for a list."""
    if lst:
        types = extract_unique_types(lst)
        if len(types) > 1:
            return types
        if types[0] == "dict":
            return [infer_dict_schema(merge_nested_dicts(lst))]
        if types[0] == "list":
            return [infer_list_schema(list(chain.from_iterable(lst)))]
        return [types[0]]
    return []

def infer_schema(obj):
    """Infer schema structure from a given object."""
    if isinstance(obj, (list, tuple)):
        return infer_list_schema(obj)
    elif isinstance(obj, dict):
        return infer_dict_schema(obj)
    elif obj is None:
        return None
    return type(obj).__name__

@cli.command()
@click.option("-i", "--input_file",
              help="The path to the json file.")
def generate_schema(input_file):
    """CLI function to process JSON file and generate schema."""
    try:
        with open(input_file, encoding="utf8") as f:
            json_data = json.load(f)
    except Exception as e:
        click.echo(f"Error reading file '{input_file}': {e}")
        return

    schema_data = infer_schema(json_data)
    output_file = input_file.replace(".json", ".schema.json")

    try:
        with open(output_file, "w", encoding="utf8") as f:
            json.dump(schema_data, f, indent=4)
        click.echo(f"Schema written to: {output_file}")
    except Exception as e:
        click.echo(f"Error writing file '{output_file}': {e}")

if __name__ == "__main__":
    cli()