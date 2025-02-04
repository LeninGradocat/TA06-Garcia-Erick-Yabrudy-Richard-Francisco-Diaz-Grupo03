import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from tqdm import tqdm
import numpy as np

console = Console()

# Configurar ruta base del script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "../E01/data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

# Crear subcarpetas para gráficos y estadísticas
STATS_DIR = os.path.join(OUTPUT_DIR, "stats")
GRAPHS_DIR = os.path.join(OUTPUT_DIR, "graphs")
os.makedirs(STATS_DIR, exist_ok=True)
os.makedirs(GRAPHS_DIR, exist_ok=True)

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
                        yearly_data[year] = {'total_rainfall': 0, 'count': 0, 'values': []}
                    yearly_data[year]['total_rainfall'] += rainfall
                    yearly_data[year]['count'] += 1
                    yearly_data[year]['values'].extend([float(v) for v in line.split()[3:] if v != "-999"])
    except Exception as e:
        errors.append(f"Error procesando archivo {filename}: {str(e)}")

    return errors, total_values, missing_values, total_rainfall, lines_processed, yearly_data

def generate_summary(total_errors, lines_processed, total_values, missing_values, yearly_data):
    missing_percentage = (missing_values / total_values * 100) if total_values else 0
    summary_text = Text(f"Validation completed.\n"
                        f"Errors found: {total_errors:,}\n"
                        f"Lines processed: {lines_processed:,}\n"
                        f"Total values processed: {total_values:,}\n"
                        f"Missing values (-999) found: {missing_values:,}\n"
                        f"Percentage of missing values: {missing_percentage:.2f}%\n\n"
                        f"Annual Precipitation Averages:\n", justify="center")

    summary_data = []
    for year, data in sorted(yearly_data.items()):
        average_rainfall = data['total_rainfall'] / data['count'] if data['count'] else 0
        max_rainfall = max(data['values']) if data['values'] else 0
        min_rainfall = min(data['values']) if data['values'] else 0
        std_dev = np.std(data['values']) if data['values'] else 0
        variability_index = (std_dev / average_rainfall) * 100 if average_rainfall else 0

        summary_text.append(f"Year {year}: Avg={average_rainfall:.2f} mm, Max={max_rainfall:.2f} mm, Min={min_rainfall:.2f} mm, Std Dev={std_dev:.2f}, Variability Index={variability_index:.2f}%\n", style="bold green")
        summary_data.append({
            'Year': year,
            'Average Rainfall': average_rainfall,
            'Max Rainfall': max_rainfall,
            'Min Rainfall': min_rainfall,
            'Std Dev': std_dev,
            'Variability Index': variability_index
        })

    console.print(Panel(summary_text, border_style="bold cyan", title="Summary", expand=False))

    # Guardar las estadísticas en un archivo CSV con fecha y hora
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    summary_csv_path = os.path.join(STATS_DIR, f"annual_precipitation_summary_{timestamp}.csv")
    summary_df = pd.DataFrame(summary_data)
    summary_df.to_csv(summary_csv_path, index=False)
    console.print(f"Summary saved to {summary_csv_path}", style="bold green")

    # Generar gráfico con fecha y hora
    plt.figure(figsize=(12, 8))
    years = [data['Year'] for data in summary_data]
    avg_rainfall = [data['Average Rainfall'] for data in summary_data]
    max_rainfall = [data['Max Rainfall'] for data in summary_data]
    min_rainfall = [data['Min Rainfall'] for data in summary_data]
    std_dev = [data['Std Dev'] for data in summary_data]

    plt.plot(years, avg_rainfall, marker='o', linestyle='-', color='b', label='Average Rainfall')
    plt.fill_between(years, min_rainfall, max_rainfall, color='lightblue', alpha=0.3, label='Min-Max Range')
    plt.errorbar(years, avg_rainfall, yerr=std_dev, fmt='o', color='r', label='Std Dev')

    plt.title('Annual Precipitation Statistics')
    plt.xlabel('Year')
    plt.ylabel('Rainfall (mm)')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    graph_path = os.path.join(GRAPHS_DIR, f"annual_precipitation_graph_{timestamp}.png")
    plt.savefig(graph_path)
    console.print(f"Graph saved to {graph_path}", style="bold green")
    plt.close()

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
                            all_yearly_data[year] = {'total_rainfall': 0, 'count': 0, 'values': []}
                        all_yearly_data[year]['total_rainfall'] += data['total_rainfall']
                        all_yearly_data[year]['count'] += data['count']
                        all_yearly_data[year]['values'].extend(data['values'])

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