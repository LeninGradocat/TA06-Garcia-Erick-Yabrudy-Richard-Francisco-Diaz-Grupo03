import os
import time
from tqdm import tqdm
import matplotlib.pyplot as plt
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from colorama import Fore, init

# Initialize Colorama and Rich
init(autoreset=True)
console = Console()

def detect_delimiter(line):
    """Detects the most frequent delimiter in a line."""
    delimiters = {'\t': line.count('\t'), ',': line.count(','), ' ': line.count(' ')}
    return max(delimiters, key=delimiters.get)

def normalize_delimiter(file_path, delimiter, target_delimiter='\t'):
    """Normalizes delimiters in a file to the target delimiter."""
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
        normalized_lines = [line.replace(delimiter, target_delimiter) for line in lines]
        with open(file_path, 'w') as file:
            file.writelines(normalized_lines)
    except Exception as e:
        console.print(Panel(Text(f"Error normalizing delimiters: {str(e)}", justify="center"),
                            title="Error", style="bold red", expand=False))

def validate_header(header):
    """Validates that the header is as expected."""
    expected_header = "precip\tMIROC5\tRCP60\tREGRESION\tdecimas\t1"
    return header.strip() == expected_header

def validate_metadata(metadata):
    """Validates the metadata of the file."""
    parts = metadata.split('\t')
    if len(parts) != 8:
        return False, "Metadata should have 8 columns"
    try:
        float(parts[1])  # Latitude
        float(parts[2])  # Longitude
        int(parts[3])    # Elevation or code
        int(parts[5])    # Start year
        int(parts[6])    # End year
    except ValueError as e:
        return False, str(e)
    return True, None

def validate_data_line(line, expected_columns=34):
    """Validates that each data line has the correct format."""
    parts = line.split()
    if len(parts) != expected_columns:
        return False, f"Expected {expected_columns} columns, found {len(parts)}"
    try:
        int(parts[1])  # Year
        int(parts[2])  # Month
        for value in parts[3:]:
            if value != "-999":
                float(value)
    except ValueError as e:
        return False, str(e)
    return True, None

def check_uniform_format(directory):
    """Checks the uniformity of format across all files."""
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
                    console.print(Panel(Text(f"Error reading file {file}: {str(e)}", justify="center"),
                                        title="Error", style="bold red", expand=False))
    return formats

def calculate_media_annual(yearly_data):
    media_annual = {}
    for year, data in yearly_data.items():
        valid_rainfall = [value for value in data['rainfall'] if value != -999]
        total_rainfall = sum(valid_rainfall)
        count = len(data['rainfall'])  # Include all values in the count
        media_annual[year] = total_rainfall / count if count > 0 else 0
    return media_annual

def validate_file(file_path, expected_columns=34):
    """Validates an entire file and collects statistics."""
    errors = []
    total_values = 0
    missing_values = 0
    total_rainfall = 0
    lines_processed = 0
    yearly_data = {}
    current_year = datetime.now().year

    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
            delimiter = detect_delimiter(lines[0])
            normalize_delimiter(file_path, delimiter)
            lines = [line.replace(delimiter, '\t') for line in lines]
            if not validate_header(lines[0]):
                errors.append(f"Invalid header: {lines[0].strip()}")
            metadata_valid, error = validate_metadata(lines[1])
            if not metadata_valid:
                errors.append(f"Metadata error: {lines[1].strip()} - {error}")
            for i, line in enumerate(lines[2:], start=3):
                parts = line.split()
                year = int(parts[1])
                if year > current_year:
                    continue
                valid, error = validate_data_line(line, expected_columns)
                if not valid:
                    errors.append(f"Line {i} error: {line.strip()} - {error}")
                else:
                    total_values += len(parts[3:])
                    missing_values += parts[3:].count("-999")
                    rainfall = sum(float(value) for value in parts[3:] if value != "-999")
                    total_rainfall += rainfall
                    lines_processed += 1

                    if year not in yearly_data:
                        yearly_data[year] = {'total_rainfall': 0, 'count': 0}
                    yearly_data[year]['total_rainfall'] += rainfall
                    yearly_data[year]['count'] += 1
    except Exception as e:
        errors.append(f"Error processing file {file_path}: {str(e)}")

    return errors, total_values, missing_values, total_rainfall, lines_processed, yearly_data

def calculate_statistics(yearly_data):
    """Calculates statistics from yearly data, excluding future years."""
    current_year = datetime.now().year
    filtered_data = {year: data for year, data in yearly_data.items() if year <= current_year}

    if not filtered_data:
        return {
            'total_years': 0,
            'total_rainfall': 0,
            'average_rainfall': 0,
            'driest_year': (None, 0),
            'wettest_year': (None, 0),
            'annual_change_rate': []
        }

    total_years = len(filtered_data)
    total_rainfall = sum(data['total_rainfall'] for data in filtered_data.values())
    average_rainfall = total_rainfall / total_years if total_years else 0
    yearly_rainfall = {year: data['total_rainfall'] for year, data in filtered_data.items()}
    sorted_years = sorted(yearly_rainfall.items(), key=lambda x: x[1])
    driest_year = sorted_years[0] if sorted_years else (None, 0)
    wettest_year = sorted_years[-1] if sorted_years else (None, 0)
    all_years = range(min(filtered_data.keys()), max(filtered_data.keys()) + 1)
    filled_data = {year: filtered_data.get(year, {'total_rainfall': 0, 'count': 0}) for year in all_years}
    annual_change_rate = [
        (year, ((filled_data[year]['total_rainfall'] - filled_data[year - 1]['total_rainfall']) /
                filled_data[year - 1]['total_rainfall']) * 100)
        for year in all_years if year > min(all_years) and filled_data[year - 1]['total_rainfall'] != 0
    ]
    return {
        'total_years': total_years,
        'total_rainfall': total_rainfall,
        'average_rainfall': average_rainfall,
        'driest_year': driest_year,
        'wettest_year': wettest_year,
        'annual_change_rate': annual_change_rate
    }

def validate_all_files(directory, log_file_path, expected_columns=34):
    """Validates all files in a directory and logs errors."""
    if not os.path.isdir(directory):
        console.print(Panel(Text(f"Directory not found: {directory}", justify="center"),
                            title="Error", style="bold red", expand=False))
        return
    files = [os.path.join(root, file) for root, _, files in os.walk(directory) for file in files if file.endswith(".dat")]

    # Check uniform format across all files
    formats = check_uniform_format(directory)
    unique_formats = set((fmt[1], fmt[2]) for fmt in formats)
    if len(unique_formats) > 1:
        console.print(Panel(Text("Found inconsistent formats:", justify="center"),
                            title="Warning", style="bold yellow", expand=False))
        for fmt in unique_formats:
            console.print(f"  Delimiter: {fmt[0]}, Columns: {fmt[1]}")

    # Validate individual files
    total_errors = 0
    total_values = 0
    missing_values = 0
    total_rainfall = 0
    lines_processed = 0
    yearly_data = {}

    try:
        with open(log_file_path, 'w') as log_file:
            desc = f"{Fore.GREEN}Validating files"
            with tqdm(total=len(files), desc=desc,
                      bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed} < {remaining}, {rate_fmt}]") as pbar:
                for file_path in sorted(files):
                    errors, file_total_values, file_missing_values, file_total_rainfall, file_lines_processed, file_yearly_data = validate_file(file_path, expected_columns)
                    total_errors += len(errors)
                    total_values += file_total_values
                    missing_values += file_missing_values
                    total_rainfall += file_total_rainfall
                    lines_processed += file_lines_processed
                    for year, data in file_yearly_data.items():
                        if year not in yearly_data:
                            yearly_data[year] = {'total_rainfall': 0, 'count': 0}
                        yearly_data[year]['total_rainfall'] += data['total_rainfall']
                        yearly_data[year]['count'] += data['count']
                    if errors:
                        log_file.write(f"Invalid file format: {file_path}\n")
                        for error in errors:
                            log_file.write(f"  {error}\n")
                    pbar.update(1)
                    time.sleep(0.001)  # Reduced sleep time for better performance
    except Exception as e:
        console.print(Panel(Text(f"Error writing to log file: {str(e)}", justify="center"),
                            title="Error", style="bold red", expand=False))

    missing_percentage = (missing_values / total_values * 100) if total_values else 0
    stats = calculate_statistics(yearly_data)
    summarized_change_rate = stats['annual_change_rate']
    media_annual = calculate_media_annual(yearly_data)

    console.print(Panel(Text(f"Validation completed.\n"
                             f"Errors found: {total_errors:,}\n"
                             f"Lines processed: {lines_processed:,}\n"
                             f"Total values processed: {total_values:,}\n"
                             f"Missing values (-999) found: {missing_values:,}\n"
                             f"Percentage of missing values: {missing_percentage:.2f}%\n"
                             f"Total rainfall: {total_rainfall:,.2f}\n"
                             f"Average annual rainfall: {stats['average_rainfall']:,.2f} mm\n"
                             f"Driest year: {stats['driest_year'][0]} with {stats['driest_year'][1]:,.2f} mm\n"
                             f"Wettest year: {stats['wettest_year'][0]} with {stats['wettest_year'][1]:,.2f} mm\n",
                             justify="center"), title="Summary", style="bold green", expand=False))

if __name__ == "__main__":
    dir_path = "../../E01/data-testing/"
    log_file_path = "../validation_log.txt"
    validate_all_files(dir_path, log_file_path)