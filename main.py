from texts import texts
from menu import menu
from dotenv import load_dotenv
load_dotenv(override=True)
import os
import csv as csv_module
import json
from datetime import datetime
from lister import lister
from app import processCSV, getPath



language = os.getenv('LANGUAGE', False)
if not language or not(language in ['es', 'en']):
    language = menu(
        texts['language-picker-header']['en'],
        ['es', 'en'],
        texts['language-picker-line']['en'],
        texts['language-picker-error']['en'],
    )



csvs = lister('csvs', '.csv')
picked_csv = menu(
    texts['csv-picker-header'][language],
    csvs,
    texts['csv-picker-line'][language],
    texts['csv-picker-error'][language],
)



formatters = lister('formatters', '.json')
picked_formatter = menu(
    texts['formatter-picker-header'][language],
    formatters,
    texts['formatter-picker-line'][language],
    texts['formatter-picker-error'][language],
)



csv_path = os.path.join('csvs', picked_csv)
with open(csv_path, 'r', encoding='utf-8', newline='') as file:
    csv = list(csv_module.DictReader(file))

formatter_path = os.path.join('formatters', picked_formatter)
with open(formatter_path, 'r', encoding='utf-8') as file:
    formatter = json.load(file)




new_csv = processCSV(csv, formatter)

os.makedirs('results', exist_ok=True)

new_fields = list(formatter.keys())
output_path = getPath(picked_csv, new_fields)

original_fieldnames = list(csv[0].keys()) if csv else []
new_fieldnames = [field for field in new_fields if field not in original_fieldnames]
fieldnames = original_fieldnames + new_fieldnames

with open(output_path, 'w', encoding='utf-8', newline='') as file:
    writer = csv_module.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(new_csv)

print(f'Saved result: {output_path}')