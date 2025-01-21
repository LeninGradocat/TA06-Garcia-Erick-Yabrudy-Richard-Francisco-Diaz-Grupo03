import os
import pandas as pd
from tqdm import tqdm
from datetime import datetime
import warnings
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from colorama import Fore, init
from concurrent.futures import ProcessPoolExecutor

# Initialize colorama and rich console
init(autoreset=True)
console = Console()

class FileValidator:
    def __init__(self, fill_missing=False):
        self.fill_missing = fill_missing

    def detect_delimiter(self, line):
        delimiters = {'\t': line.count('\t'), ',': line.count(','), ' ': line.count(' ')}
        return max(delimiters, key=delimiters.get)

    def normalize_delimiter(self, file_path, delimiter, target_delimiter='\t'):
        try:
            with open(file_path, 'r') as file:
                lines = file.readlines()
            normalized_lines = [line.replace(delimiter, target_delimiter) for line in lines]
            with open(file_path, 'w') as file:
                file.writelines(normalized_lines)
        except (IOError, OSError) as e:
            console.print(Panel(Text(f"File error: {str(e)}", justify="center"),
                                title="Error", style="bold red", expand=False))
        except Exception as e:
            console.print(Panel(Text(f"Unexpected error: {str(e)}", justify="center"),
                                title="Error", style="bold red", expand=False))

    def validate_header(self, header):
        expected_header = "precip\tMIROC5\tRCP60\tREGRESION\tdecimas\t1"
        return header.strip() == expected_header

    def validate_metadata(self, metadata):
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

    def is_leap_year(self, year):
        return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

def validate_line(self, line, id_value, year_range, days_in_month):
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
        expected_days = 29 if self.is_leap_year(year) else 28
    else:
        expected_days = days_in_month[month]

    actual_days = len(parts) - 3
    if parts[-1] == "-999":
        actual_days -= 1

    if actual_days != expected_days:
        if self.fill_missing:
            parts.extend(["-999"] * (expected_days - actual_days))
            line = "\t".join(parts)
            return True, line
        else:
            return False, f"Month {month} has {actual_days} days of data instead of {expected_days}"

    return True, line

    def process_file(self, file_path):
        discrepancies = []
        lines_with_minus_999 = 0
        total_values = 0
        missing_values = 0
        total_rainfall = 0.0
        lines_processed = 0
        corrected_lines = []


        try:
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                with open(file_path, 'r') as file:
                    lines = file.readlines()
                id_value = lines[2].split()[0]
                year_range = (2005, 2101)
                days_in_month = {1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}

                for line in lines[2:]:
                    valid, result = self.validate_line(line, id_value, year_range, days_in_month)
                    if valid:
                        corrected_lines.append(result)
                    else:
                        discrepancies.append(result)
                for warning in w:
                    discrepancies.append(f"{warning.message}")

            if self.fill_missing and corrected_lines:
                with open(file_path, 'w') as file:
                    file.writelines(lines[:2] + corrected_lines)
        except (pd.errors.ParserError, pd.errors.EmptyDataError) as e:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            discrepancies.append(f"{file_path} {timestamp} Pandas error: {str(e)}")
        except Exception as e:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            discrepancies.append(f"{file_path} {timestamp} Unexpected error: {str(e)}")

        return discrepancies, lines_with_minus_999, total_values, missing_values, total_rainfall, lines_processed

    def check_uniform_format(self, directory):
        formats = []
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(".dat"):
                    try:
                        with open(os.path.join(root, file), 'r') as f:
                            header = f.readline().strip()
                            delimiter = self.detect_delimiter(header)
                            columns = len(header.split(delimiter))
                            formats.append((file, delimiter, columns))
                    except (IOError, OSError) as e:
                        console.print(Panel(Text(f"File error: {str(e)}", justify="center"),
                                            title="Error", style="bold red", expand=False))
                    except Exception as e:
                        console.print(Panel(Text(f"Unexpected error: {str(e)}", justify="center"),
                                            title="Error", style="bold red", expand=False))
        return formats

    def validate_files(self, directory):
        file_infos = [os.path.join(root, file) for root, _, files in os.walk(directory) for file in files if file.endswith('.dat')]

        if not file_infos:
            console.print(Panel(Text("No .dat files found in the directory.", justify="center"),
                                title="Error", style="bold red", expand=False))
            return

        current_time = datetime.now().strftime("%Y%m%d%H%M%S")
        log_file_path = f"../../E02/v1 programa/validation_log_{current_time}.log"
        error_log_path = f"../../E02/v1 programa/error_log_{current_time}.log"

        formats = self.check_uniform_format(directory)
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
                    with ProcessPoolExecutor() as executor:
                        future_to_file = {executor.submit(self.process_file, file_path): file_path for file_path in sorted(file_infos)}
                        for future in tqdm(future_to_file, total=len(file_infos), desc=desc, leave=False):
                            try:
                                result = future.result()
                                discrepancies.extend(result[0])
                                lines_with_minus_999 += result[1]
                                total_values += result[2]
                                missing_values += result[3]
                                total_rainfall += result[4]
                                lines_processed += result[5]
                                total_errors += len(result[0])
                                if result[0]:
                                    log_file.write(f"Invalid file format: {future_to_file[future]}\n")
                                    for error in result[0]:
                                        log_file.write(f"  {error}\n")
                            except Exception as e:
                                console.print(Panel(Text(f"Error processing file {future_to_file[future]}: {str(e)}", justify="center"),
                                                    title="Error", style="bold red", expand=False))
                            pbar.update(1)
        except (IOError, OSError) as e:
            console.print(Panel(Text(f"Error writing to log file: {str(e)}", justify="center"),
                                title="Error", style="bold red", expand=False))
        except Exception as e:
            console.print(Panel(Text(f"Unexpected error: {str(e)}", justify="center"),
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

        if self.fill_missing and discrepancies:
            user_input = input("Do you want to regenerate the files with corrections? (yes/no): ")
            if user_input.lower() == 'yes':
                for file_path in file_infos:
                    self.process_file(file_path)

directory_path = '../../E01/dades-prove/'
validator = FileValidator(fill_missing=True)
validator.validate_files(directory_path)