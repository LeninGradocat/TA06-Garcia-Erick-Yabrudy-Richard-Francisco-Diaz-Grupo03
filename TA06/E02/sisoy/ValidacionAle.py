import os
import pandas as pd
from datetime import datetime


def validate_line(line, id_value, year_range, days_in_month):
    parts = line.strip().split()
    if len(parts) < 3:
        return False, "Line has less than 3 columns"

    # Validate ID
    if parts[0] != id_value:
        return False, "ID mismatch"

    # Validate Year
    year = int(parts[1])
    if year < year_range[0] or year > year_range[1]:
        return False, "Year out of range"

    # Validate Month
    month = int(parts[2])
    if month not in days_in_month:
        return False, "Invalid month"

    # Validate days count for the month, ignoring the last `-999` if present
    expected_days = days_in_month[month]
    actual_days = len(parts) - 3  # Exclude ID, year, and month columns
    if parts[-1] == "-999":
        actual_days -= 1

    if actual_days != expected_days:
        return False, f"Month {month} has {actual_days} days of data instead of {expected_days}"

    return True, ""


def validate_files(directory):
    file_infos = [os.path.join(root, file) for root, _, files in os.walk(directory) for file in files if
                  file.endswith('.dat')]

    if not file_infos:
        print("No .dat files found in the directory.")
        return

    discrepancies = []

    # Generate a unique log file name with the current date and time
    log_file_path = f"inconsistencies_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

    with open(log_file_path, 'w') as log_file:
        for file_path in file_infos:
            try:
                df = pd.read_csv(file_path, delim_whitespace=True, header=None, skiprows=2)
                id_value = df.iloc[0, 0]
                year_range = (2005, 2101)
                days_in_month = {
                    1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30,
                    7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31
                }

                for index, row in df.iterrows():
                    line = " ".join(row.astype(str).values)
                    is_valid, msg = validate_line(line, id_value, year_range, days_in_month)
                    if not is_valid:
                        timestamp = datetime.now().strftime("day_%d.%m.%Y_timer_%H:%M:%S")
                        log_file.write(f"{timestamp} {file_path} {msg} on line {index + 3}\n")
                        discrepancies.append(f"{file_path}: {msg} on line {index + 3}")
            except Exception as e:
                timestamp = datetime.now().strftime("day_%d.%m.%Y_timer_%H:%M:%S")
                log_file.write(f"{timestamp} {file_path} {str(e)}\n")
                discrepancies.append(f"{file_path}: {str(e)}")

    if discrepancies:
        print("\nFormat discrepancies found:")
        for discrepancy in discrepancies:
            print(discrepancy)
        print(f"\nInconsistencies logged in {log_file_path}")
    else:
        print("\nAll files have consistent formats.")


# Directory path
directory_path = '../../E01/dades/'
validate_files(directory_path)