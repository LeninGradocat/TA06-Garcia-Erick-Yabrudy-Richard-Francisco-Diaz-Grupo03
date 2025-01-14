import os
import logging
from datetime import datetime

def get_file_info(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        if len(lines) < 2:
            return None

        line1 = lines[0].strip()
        line2 = lines[1].strip().split('\t')

        # Ensure specific_values is set even if line2 has fewer columns
        specific_values = line2[3:8] if len(line2) >= 8 else []

        return {
            'file_path': file_path,
            'line1': line1,
            'specific_values': specific_values,
            'lines': lines
        }

def validate_files(directory):
    file_infos = []
    files_to_validate = []
    errors_found = False

    for root, _, files in os.walk(directory):
        for file in sorted(files):
            if file.endswith('.dat'):
                file_path = os.path.join(root, file)
                files_to_validate.append(file_path)

    if not files_to_validate:
        print("No .dat files found in the directory.")
        return

    reference_line1 = "precip\tMIROC5\tRCP60\tREGRESION\tdecimas\t1"
    reference_specific_values = ['182', 'geo', '2006', '2100', '-1']

    for file_path in files_to_validate:
        file_info = get_file_info(file_path)
        if file_info:
            file_infos.append(file_info)
            if file_info['line1'] != reference_line1:
                if not errors_found:
                    setup_logging()
                    errors_found = True
                error_message = f"Line 1 mismatch in file: {file_info['file_path']} - {file_info['line1']}"
                print(error_message)
                logging.info(f"{error_message} - Line: {file_info['lines'][0].strip()}")
            if file_info['specific_values'] != reference_specific_values:
                if not errors_found:
                    setup_logging()
                    errors_found = True
                error_message = f"Specific values mismatch in file: {file_info['file_path']} - {file_info['specific_values']}"
                print(error_message)
                logging.info(f"{error_message} - Line: {file_info['lines'][1].strip()}")

    print("Validation completed.")

def setup_logging():
    current_time = datetime.now().strftime("%Y%m%d%H%M%S")
    log_filename = f"failures_{current_time}.log"

    # Delete existing log file if it exists
    if os.path.exists(log_filename):
        os.remove(log_filename)

    logging.basicConfig(filename=log_filename, filemode='w', level=logging.INFO, format='%(asctime)s %(message)s')

# Directory path
directory_path = '/home/erick.garcia.7e8/PycharmProjects/TA06-Garcia-Erick-Yabrudy-Richard-Francisco-Diaz-Grupo03'
validate_files(directory_path)