import os
import pandas as pd
from tqdm import tqdm
from datetime import datetime
import warnings
from multiprocessing import Pool


def detect_delimiter(line):
    delimiters = {'\t': line.count('\t'), ',': line.count(','), ' ': line.count(' ')}
    return max(delimiters, key=delimiters.get)

def normalize_delimiter(file_path, delimiter, target_delimiter='\t'):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    normalized_lines = [line.replace(delimiter, target_delimiter) for line in lines]
    with open(file_path, 'w') as file:
        file.writelines(normalized_lines)

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
                            timestamp = datetime.now().strftime("day_%d.%m.%Y_timer_%H:%M:%S")
                            discrepancies.append(f"{timestamp} {file_path} {msg} on line {index + 3}")
            for warning in w:
                discrepancies.append(f"{warning.message}")
    except Exception as e:
        timestamp = datetime.now().strftime("day_%d.%m.%Y_timer_%H:%M:%S")
        discrepancies.append(f"{timestamp} {file_path} {str(e)}")

    return discrepancies, lines_with_minus_999

def validate_files(directory):
    file_infos = [os.path.join(root, file) for root, _, files in os.walk(directory) for file in files if file.endswith('.dat')]

    if not file_infos:
        print("No .dat files found in the directory.")
        return

    current_time = datetime.now().strftime("%Y%m%d%H%M%S")
    log_file_path = f"../../E02/v1 programa/validation_log_{current_time}.log"
    error_log_path = f"../../E02/v1 programa/error_log_{current_time}.log"

    num_processes = 2  # Increase the number of processes
    with Pool(num_processes) as pool:
        results = list(tqdm(pool.imap(process_file, file_infos), total=len(file_infos), desc="Validating files", leave=False))

    discrepancies = []
    lines_with_minus_999 = 0
    for result in results:
        discrepancies.extend(result[0])
        lines_with_minus_999 += result[1]

    with open(log_file_path, 'w') as log_file:
        if not discrepancies:
            log_file.write("NO ERROR\n")
        else:
            for discrepancy in discrepancies:
                log_file.write(f"{discrepancy}\n")
        log_file.write(f"Lines with -999: {lines_with_minus_999}\n")

    if discrepancies:
        print("\nFormat discrepancies found. Check the log file for details.")
    else:
        print("\nAll files have consistent formats.")

directory_path = '../../E01/dades/'
validate_files(directory_path)