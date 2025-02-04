import os
import pandas as pd
import numpy as np
from tqdm import tqdm
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import warnings

# Suprimir todas las advertencias
warnings.filterwarnings("ignore")

def is_leap_year(year):
    """Determina si un año es bisiesto."""
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

def detect_delimiter(line):
    delimiters = {'\t': line.count('\t'), ',': line.count(','), ' ': line.count(' ')}
    return max(delimiters, key=delimiters.get)

def validate_header(header):
    expected_header = "precip\tMIROC5\tRCP60\tREGRESION\tdecimas\t1"
    return header.strip() == expected_header

def validate_metadata(metadata):
    parts = metadata.split('\t')
    if len(parts) != 8:
        return False, "Metadata should have 8 columns"
    try:
        float(parts[1])
        float(parts[2])
        int(parts[3])
        int(parts[5])
        int(parts[6])
    except ValueError as e:
        return False, str(e)
    return True, None

def validate_line(line, id_value, year_range, days_in_month):
    parts = line.strip().split()
    if len(parts) < 3:
        return False, "Line has less than 3 columns"

    if parts[0] != id_value:
        return False, "ID mismatch"

    year = int(parts[1])
    if year < year_range[0] or year > year_range[1]:
        return False, "Year out of range"

    month = int(parts[2])
    if month not in days_in_month:
        return False, "Invalid month"

    if month == 2:
        expected_days = 29 if is_leap_year(year) else 28
    else:
        expected_days = days_in_month[month]

    actual_days = len(parts) - 3
    if parts[-1] == "-999":
        actual_days -= 1

    if actual_days != expected_days:
        return False, f"Month {month} has {actual_days} days of data instead of {expected_days}"

    return True, ""

def process_file(file_path, year_range):
    discrepancies = set()  # Use a set to avoid duplicate messages
    lines_with_minus_999 = 0
    try:
        df = pd.read_csv(file_path, sep='\s+', header=None, skiprows=2, chunksize=1000)
        for chunk in df:
            id_value = chunk.iloc[0, 0]
            days_in_month = {
                1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30,
                7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31
            }

            for index, row in chunk.iterrows():
                line = " ".join(row.astype(str).values)
                is_valid, msg = validate_line(line, id_value, year_range, days_in_month)
                if not is_valid:
                    if line.strip().endswith("-999"):
                        lines_with_minus_999 += 1
                    else:
                        discrepancies.add(f"{file_path} {msg} on line {index + 3}")
    except Exception as e:
        discrepancies.add(f"{file_path} {str(e)}")

    return discrepancies, lines_with_minus_999

def check_uniform_format(directory):
    formats = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".dat"):
                try:
                    with open(os.path.join(root, file), 'r') as f:
                        header = f.readline().strip()
                        delimiter = detect_delimiter(header)
                        columns = len(header.split(delimiter))
                        formats.append((file, delimiter, columns))
                except Exception as e:
                    pass
    return formats

def validate_files(directory, year_range):
    file_infos = [os.path.join(root, file) for root, _, files in os.walk(directory) for file in files if file.endswith('.dat')]

    if not file_infos:
        print("No .dat files found in the directory.")
        return

    formats = check_uniform_format(directory)
    unique_formats = set((fmt[1], fmt[2]) for fmt in formats)
    if len(unique_formats) > 1:
        print("Found inconsistent formats:")
        for fmt in unique_formats:
            print(f"  Delimiter: {fmt[0]}, Columns: {fmt[1]}")

    discrepancies = set()  # Use a set to avoid duplicate messages
    lines_with_minus_999 = 0
    total_errors = 0
    all_data = []

    for file_path in tqdm(file_infos, desc="Validating files", leave=False):
        result = process_file(file_path, year_range)
        discrepancies.update(result[0])
        lines_with_minus_999 += result[1]
        total_errors += len(result[0])

        df = pd.read_csv(file_path, sep='\s+', header=None, skiprows=2)
        all_data.append(df)

    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
        analyze_and_plot(combined_df, year_range)

    missing_percentage = (lines_with_minus_999 / sum(df.size for df in all_data) * 100) if all_data else 0
    print(f"Validation completed.\n"
          f"Errors found: {total_errors:,}\n"
          f"Lines with -999: {lines_with_minus_999:,}\n"
          f"Percentage of missing values: {missing_percentage:.2f}%\n")

    if discrepancies:
        print("\nFormat discrepancies found:")
        # Omitir la impresión de los detalles de discrepancias
    else:
        print("\nAll files have consistent formats.")

def analyze_and_plot(df, year_range):
    metadata = df.iloc[:, :3]
    daily_values = df.iloc[:, 3:]

    # Contar los valores -999
    count_minus_999 = (daily_values == -999).sum().sum()
    print(f"Cantidad de valores -999: {count_minus_999}")

    # Reemplazar -999 con NaN para el cálculo del promedio
    daily_values_replaced = daily_values.replace(-999, np.nan)

    # Calcular la media diaria por fila, excluyendo valores NaN
    df['average_rainfall'] = daily_values_replaced.mean(axis=1, skipna=True)
    df['year'] = metadata.iloc[:, 1]
    df['month'] = metadata.iloc[:, 2]

    # Filtrar el rango de años
    df = df[(df['year'] >= year_range[0]) & (df['year'] <= year_range[1])]

    # Calcular promedios anuales
    annual_averages = df.groupby('year')['average_rainfall'].mean().reset_index()

    # Redondear los valores de precipitación a dos decimales
    annual_averages['average_rainfall'] = annual_averages['average_rainfall'].round(2)

    # Imprimir promedio anual de precipitación
    print("Promedio de precipitación anual (mm):")
    for index, row in annual_averages.iterrows():
        print(f"{int(row['year'])}: {row['average_rainfall']} mm")

    # Obtener la fecha y hora actual para nombres de archivo
    current_time = datetime.now().strftime("%Y%m%d%H%M%S")

    # Gráfico de tendencia anual de precipitación (medias anuales)
    plt.figure(figsize=(12, 6))
    plt.plot(annual_averages['year'], annual_averages['average_rainfall'], marker='o', linestyle='-')
    plt.title('Promedio de Precipitación Anual')
    plt.xlabel('Año')
    plt.ylabel('Promedio de Precipitación (mm)')
    plt.grid(True)
    plt.savefig(f'average_precipitation_trend_{current_time}.png')
    plt.close()

    # Gráfico de caja (variación estacional por mes)
    plt.figure(figsize=(10, 6))
    sns.boxplot(x='month', y='average_rainfall', data=df)
    plt.title('Variación Estacional de Precipitación (Promedio Diario)')
    plt.xlabel('Mes')
    plt.ylabel('Promedio de Precipitación (mm)')
    plt.grid(True)
    plt.savefig(f'seasonal_variation_average_{current_time}.png')
    plt.close()

    print("Gráficos generados exitosamente.")

if __name__ == "__main__":
    # Ruta relativa al directorio de datos
    base_path = os.path.dirname(os.path.abspath(__file__))
    relative_data_path = os.path.join(base_path, '../E01/data')

    # Definir el rango de años
    year_range = (2006, 2025)

    validate_files(relative_data_path, year_range)
