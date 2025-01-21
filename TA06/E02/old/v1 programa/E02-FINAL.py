import os
import pandas as pd
from tqdm import tqdm
from datetime import datetime
import warnings
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from colorama import Fore, init
import time

# Initialize colorama and rich console
init(autoreset=True)
console = Console()

def detect_delimiter(line):
    delimiters = {'\t': line.count('\t'), ',': line.count(','), ' ': line.count(' ')}
    return max(delimiters, key=delimiters.get)

def normalize_delimiter(file_path, delimiter, target_delimiter='\t'):
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

def is_leap_year(year):
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

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

def process_file(file_path):
    discrepancies = []
    lines_with_minus_999 = 0
    total_values = 0
    missing_values = 0
    total_rainfall = 0.0
    lines_processed = 0

    try:
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            df = pd.read_csv(file_path, sep='\s+', header=None, skiprows=2, chunksize=1000)
            for chunk in df:
                id_value = chunk.iloc[0, 0]
                year_range = (2005, 2101)
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
                            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            discrepancies.append(f"{file_path} {timestamp} Line {index + 3} error: {line} - {msg}")
                    else:
                        parts = line.split()
                        total_values += len(parts[3:])
                        missing_values += parts[3:].count("-999")
                        total_rainfall += sum(float(value) for value in parts[3:] if value != "-999")
                        lines_processed += 1
            for warning in w:
                discrepancies.append(f"{warning.message}")
    except Exception as e:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        discrepancies.append(f"{file_path} {timestamp} {str(e)}")

    return discrepancies, lines_with_minus_999, total_values, missing_values, total_rainfall, lines_processed

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
                    console.print(Panel(Text(f"Error reading file {file}: {str(e)}", justify="center"),
                                        title="Error", style="bold red", expand=False))
    return formats

def validate_files(directory):
    file_infos = [os.path.join(root, file) for root, _, files in os.walk(directory) for file in files if file.endswith('.dat')]

    if not file_infos:
        console.print(Panel(Text("No .dat files found in the directory.", justify="center"),
                            title="Error", style="bold red", expand=False))
        return

    current_time = datetime.now().strftime("%Y%m%d%H%M%S")
    log_file_path = f"../../E02/v1 programa/validation_log_{current_time}.log"
    error_log_path = f"../../E02/v1 programa/error_log_{current_time}.log"

    formats = check_uniform_format(directory)
    unique_formats = set((fmt[1], fmt[2]) for fmt in formats)
    if len(unique_formats) > 1:
        console.print(Panel(Text("Found inconsistent formats:", justify="center"),
                            title="Warning", style="bold yellow", expand=False))
        for fmt in unique_formats:
            console.print(f"  Delimiter: {fmt[0]}, Columns: {fmt[1]}")

    discrepancies = []
    lines_with_minus_999 = 0
    total_errors = 0
    total_values = 0
    missing_values = 0
    total_rainfall = 0.0
    lines_processed = 0

    try:
        with open(log_file_path, 'w') as log_file:
            desc = f"{Fore.GREEN}Validating files"
            with tqdm(total=len(file_infos), desc=desc,
                      bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed} < {remaining}, {rate_fmt}]") as pbar:
                for file_path in sorted(file_infos):
                    result = process_file(file_path)
                    discrepancies.extend(result[0])
                    lines_with_minus_999 += result[1]
                    total_values += result[2]
                    missing_values += result[3]
                    total_rainfall += result[4]
                    lines_processed += result[5]
                    total_errors += len(result[0])
                    if result[0]:
                        log_file.write(f"Invalid file format: {file_path}\n")
                        for error in result[0]:
                            log_file.write(f"  {error}\n")
                    pbar.update(1)
                    time.sleep(0.001)  # Reduced sleep time for better performance
    except Exception as e:
        console.print(Panel(Text(f"Error writing to log file: {str(e)}", justify="center"),
                            title="Error", style="bold red", expand=False))

    missing_percentage = (missing_values / total_values * 100) if total_values else 0
    console.print(Panel(Text(f"Validation completed.\n"
                             f"Errors found: {total_errors:,}\n"
                             f"Lines processed: {lines_processed:,}\n"
                             f"Total values processed: {total_values:,}\n"
                             f"Missing values (-999) found: {missing_values:,}\n"
                             f"Percentage of missing values: {missing_percentage:.2f}%\n"
                             f"Total rainfall: {total_rainfall:,.2f}",
                             justify="center"), title="Summary", style="bold green", expand=False))

    if discrepancies:
        console.print(Panel(Text("Format discrepancies found. Check the log file for details.", justify="center"),
                            title="Warning", style="bold yellow", expand=False))
    else:
        console.print(Panel(Text("All files have consistent formats.", justify="center"),
                            title="Success", style="bold green", expand=False))

directory_path = '../../../E01/data/'
validate_files(directory_path)