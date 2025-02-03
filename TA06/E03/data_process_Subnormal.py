import os
import sys
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from tqdm import tqdm

console = Console()

# Configurar ruta base del script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "../E01/data")

def get_file_path(filename):
    """Obtiene la ruta absoluta del archivo dentro del directorio de datos."""
    return os.path.join(DATA_DIR, filename)

def detect_delimiter(line):
    """Detecta el delimitador más frecuente en una línea."""
    delimiters = {'\t': line.count('\t'), ',': line.count(','), ' ': line.count(' ')}
    return max(delimiters, key=delimiters.get)

def normalize_delimiter(file_path, delimiter, target_delimiter='\t'):
    """Normaliza delimitadores en un archivo."""
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
        normalized_lines = [line.replace(delimiter, target_delimiter) for line in lines]
        with open(file_path, 'w') as file:
            file.writelines(normalized_lines)
    except Exception as e:
        console.print(Panel(f"Error normalizando delimitadores: {str(e)}", title="Error", style="bold red"))

def validate_header(header):
    """Valida que el encabezado sea el esperado."""
    expected_header = "precip\tMIROC5\tRCP60\tREGRESION\tdecimas\t1"
    return header.strip() == expected_header

def validate_metadata(metadata):
    """Valida los metadatos del archivo."""
    parts = metadata.split('\t')
    if len(parts) != 8:
        return False, "Los metadatos deben tener 8 columnas"
    try:
        float(parts[1])  # Latitud
        float(parts[2])  # Longitud
        int(parts[3])  # Elevación o código
        int(parts[5])  # Año de inicio
        int(parts[6])  # Año de fin
    except ValueError as e:
        return False, str(e)
    return True, None

def validate_data_line(line, expected_columns=34):
    """Valida que cada línea de datos tenga el formato correcto."""
    parts = line.split()
    if len(parts) != expected_columns:
        return False, f"Se esperaban {expected_columns} columnas, se encontraron {len(parts)}"
    try:
        int(parts[1])  # Año
        int(parts[2])  # Mes
        for value in parts[3:]:
            if value != "-999":
                float(value)
    except ValueError as e:
        return False, str(e)
    return True, None

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

def generate_summary(total_errors, lines_processed, total_values, missing_values):
    missing_percentage = (missing_values / total_values * 100) if total_values else 0
    console.print(Panel(Text(f"Validation completed.\n"
                            f"Errors found: {total_errors:,}\n"
                            f"Lines processed: {lines_processed:,}\n"
                            f"Total values processed: {total_values:,}\n"
                            f"Missing values (-999) found: {missing_values:,}\n"
                            f"Percentage of missing values: {missing_percentage:.2f}%", justify="center"),
                            border_style="bold cyan", title="Summary", expand=False))

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

    try:
        with open(log_file_path, 'w') as log_file:
            desc = "Validating files"
            with tqdm(total=len(files), desc=desc) as pbar:
                for file_path in sorted(files):
                    errors, file_total_values, file_missing_values, file_total_rainfall, file_lines_processed, _ = validate_file(file_path, expected_columns)
                    total_errors += len(errors)
                    total_values += file_total_values
                    missing_values += file_missing_values
                    total_rainfall += file_total_rainfall
                    lines_processed += file_lines_processed
                    file_line_counts[file_path] = file_lines_processed
                    if errors:
                        log_file.write(f"Invalid file format: {file_path}\n")
                        for error in errors:
                            log_file.write(f"  {error}\n")
                    pbar.update(1)
    except Exception as e:
        console.print(Panel(f"Error writing to log file: {str(e)}", title="Error", style="bold red"))

    generate_summary(total_errors, lines_processed, total_values, missing_values)

if __name__ == "__main__":
    log_file_path = os.path.join(BASE_DIR, "validation_log.txt")
    validate_all_files(DATA_DIR, log_file_path)