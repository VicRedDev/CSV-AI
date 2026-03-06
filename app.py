from ai import AI
from datetime import datetime
from dotenv import load_dotenv
load_dotenv(override=True)
import os


ai = AI()

def processCSV(csv, formatter):
    processingLimit = os.getenv('PROCESSING_LIMIT', False)
    try:
        processingLimit = int(processingLimit) if processingLimit else False
        if not processingLimit or processingLimit <= 0:
            processingLimit = False
    except:
        processingLimit = False

    new_csv = []
    for index, line in enumerate(csv):
        if processingLimit and index >= processingLimit:
            break
        data_index = False
        
        for key in line.keys():
            value = line.get(key, False)
            if value:
                data_index = value
                break

        index_text = f' | {key}: {data_index[:30]}' if data_index else ''

        print(f'Procesing line {index}{index_text}')
        new_columns = ai.generateColumns(line, formatter)
        new_csv.append({
            **line,
            **new_columns,
        })

        print('Results:')
        for key in new_columns.keys():
            print(f'- {key}: {new_columns[key][:30]}')

        print()

    return new_csv

def getPath(picked_csv, new_fields):
    original_name, _ = os.path.splitext(picked_csv)
    timestamp = datetime.now().strftime('%Y_%m_%d %H_%M_%S')
    output_filename = f"{timestamp} - {' '.join(new_fields)} - {original_name}.csv"
    output_path = os.path.join('results', output_filename)

    return output_path