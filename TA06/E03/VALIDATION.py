import os
import sys
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from tqdm import tqdm
from DATA_PROCESSING import get_file_path, detect_delimiter, normalize_delimiter, validate_header, validate_metadata, validate_data_line, BASE_DIR, DATA_DIR
from STADISTICS import generate_summary

console = Console()

def validate_file(filename, expected_columns=34):
    """Valida un archivo completo y recopila estadísticas."""
    file_path = get_file_path(filename)

    if not os.path.exists(file_path):
        console.print(Panel(f"El archivo {filename} no existe en {DATA_DIR}", title="Error", style="bold red"))
        sys.exit(1)

    errors = []
    total_values, missing_values, total_rainfall, lines_processed = 0, 0, 0, 0
    yearly_data = {}

    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
            delimiter = detect_delimiter(lines[0])
            normalize_delimiter(file_path, delimiter)
            lines = [line.replace(delimiter, '\t') for line in lines]

            if not validate_header(lines[0]):
                errors.append(f"Encabezado inválido: {lines[0].strip()}")

            metadata_valid, error = validate_metadata(lines[1])
            if not metadata_valid:
                errors.append(f"Error en metadatos: {error}")

            for i, line in enumerate(lines[2:], start=3):
                lines_processed += 1  # Incrementa el contador de líneas procesadas en cada iteración

                valid, error = validate_data_line(line, expected_columns)
                if not valid:
                    errors.append(f"Error en línea {i}: {error}")
                else:
                    total_values += len(line.split()[3:])
                    missing_values += line.split()[3:].count("-999")
                    rainfall = sum(float(v) for v in line.split()[3:] if v != "-999")
                    total_rainfall += rainfall
                    year = int(line.split()[1])
                    if year not in yearly_data:
                        yearly_data[year] = {'total_rainfall': 0, 'count': 0}
                    yearly_data[year]['total_rainfall'] += rainfall
                    yearly_data[year]['count'] += 1
    except Exception as e:
        errors.append(f"Error procesando archivo {filename}: {str(e)}")

    return errors, total_values, missing_values, total_rainfall, lines_processed, yearly_data

def validate_all_files(directory, log_file_path, expected_columns=34):
    if not os.path.isdir(directory):
        console.print(Panel(f"Directory not found: {directory}", title="Error", style="bold red"))
        return
    files = [os.path.join(root, file) for root, _, files in os.walk(directory) for file in files if file.endswith(".dat")]

    total_errors = 0
    total_values = 0
    missing_values = 0
    total_rainfall = 0
    lines_processed = 0
    file_line_counts = {}
    all_yearly_data = {}

    try:
        with open(log_file_path, 'w') as log_file:
            desc = "Validating files"
            with tqdm(total=len(files), desc=desc) as pbar:
                for file_path in sorted(files):
                    errors, file_total_values, file_missing_values, file_total_rainfall, file_lines_processed, yearly_data = validate_file(file_path, expected_columns)
                    total_errors += len(errors)
                    total_values += file_total_values
                    missing_values += file_missing_values
                    total_rainfall += file_total_rainfall
                    lines_processed += file_lines_processed
                    file_line_counts[file_path] = file_lines_processed

                    # Acumular datos anuales
                    for year, data in yearly_data.items():
                        if year not in all_yearly_data:
                            all_yearly_data[year] = {'total_rainfall': 0, 'count': 0}
                        all_yearly_data[year]['total_rainfall'] += data['total_rainfall']
                        all_yearly_data[year]['count'] += data['count']

                    if errors:
                        log_file.write(f"Invalid file format: {file_path}\n")
                        for error in errors:
                            log_file.write(f"  {error}\n")
                    pbar.update(1)
    except Exception as e:
        console.print(Panel(f"Error writing to log file: {str(e)}", title="Error", style="bold red"))

    generate_summary(total_errors, lines_processed, total_values, missing_values, all_yearly_data)

if __name__ == "__main__":
    log_file_path = os.path.join(BASE_DIR, "validation_log.txt")
    validate_all_files(DATA_DIR, log_file_path)