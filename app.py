from ai import AI
from datetime import datetime
from dotenv import load_dotenv
load_dotenv(override=True)
import os
import time
import shutil


ai = AI()

def _format_time(seconds):
    if seconds < 60:
        return f'{seconds:.1f}s'
    minutes = int(seconds // 60)
    secs = seconds % 60
    if minutes < 60:
        return f'{minutes}m {secs:.0f}s'
    hours = int(minutes // 60)
    mins = minutes % 60
    return f'{hours}h {mins}m {secs:.0f}s'

def _print_progress(index, total, last_results, last_time, avg_time, elapsed_times):
    terminal_width = shutil.get_terminal_size((80, 20)).columns
    processed = index + 1
    remaining = total - processed
    percentage = (processed / total) * 100
    eta = avg_time * remaining if avg_time > 0 else 0

    separator = '─' * terminal_width

    # Progress bar
    bar_label = ' Progreso '
    bar_inner_width = terminal_width - 2  # for [ and ]
    filled = int(bar_inner_width * percentage / 100)
    bar = '█' * filled + '░' * (bar_inner_width - filled)
    bar_line = f'[{bar}]'

    # Stats
    stats_line = f'  {percentage:5.1f}%  |  Procesadas: {processed}/{total}  |  Restantes: {remaining}'
    time_line = f'  Última línea: {_format_time(last_time)}  |  Promedio: {_format_time(avg_time)}  |  Tiempo restante: {_format_time(eta)}'

    # Results
    results_lines = []
    if last_results:
        results_lines.append('  Resultados última línea:')
        for key, val in last_results.items():
            display_val = str(val)[:60]
            results_lines.append(f'    • {key}: {display_val}')

    # Clear screen and print
    print('\033[2J\033[H', end='')  # clear screen + move cursor to top
    print(separator)
    print(bar_label.center(terminal_width))
    print(bar_line)
    print(stats_line)
    print(separator)
    print(time_line)
    print(separator)
    for rl in results_lines:
        print(rl)
    if results_lines:
        print(separator)
    print()

def processCSV(csv, formatter):
    processingLimit = os.getenv('PROCESSING_LIMIT', False)
    try:
        processingLimit = int(processingLimit) if processingLimit else False
        if not processingLimit or processingLimit <= 0:
            processingLimit = False
    except:
        processingLimit = False

    total = min(len(csv), processingLimit) if processingLimit else len(csv)
    elapsed_times = []

    new_csv = []
    for index, line in enumerate(csv):
        if processingLimit and index >= processingLimit:
            break

        start_time = time.time()
        new_columns = ai.generateColumns(line, formatter)
        end_time = time.time()

        line_time = end_time - start_time
        elapsed_times.append(line_time)
        avg_time = sum(elapsed_times) / len(elapsed_times)

        new_csv.append({
            **line,
            **new_columns,
        })

        _print_progress(index, total, new_columns, line_time, avg_time, elapsed_times)

    return new_csv

def getPath(picked_csv, new_fields):
    original_name, _ = os.path.splitext(picked_csv)
    timestamp = datetime.now().strftime('%Y_%m_%d %H_%M_%S')
    output_filename = f"{timestamp} - {' '.join(new_fields)} - {original_name}.csv"
    output_path = os.path.join('results', output_filename)

    return output_path