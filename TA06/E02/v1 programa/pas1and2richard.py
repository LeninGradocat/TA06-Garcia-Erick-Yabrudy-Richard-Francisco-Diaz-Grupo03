import os
from tqdm import tqdm

def detect_delimiter(line):
    """Detects the most frequent delimiter in a line."""
    delimiters = {'\t': line.count('\t'), ',': line.count(','), ' ': line.count(' ')}
    return max(delimiters, key=delimiters.get)

def normalize_delimiter(file_path, delimiter, target_delimiter='\t'):
    """Normalizes delimiters in a file to the target delimiter."""
    with open(file_path, 'r') as file:
        lines = file.readlines()
    normalized_lines = [line.replace(delimiter, target_delimiter) for line in lines]
    with open(file_path, 'w') as file:
        file.writelines(normalized_lines)

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
                with open(os.path.join(root, file), 'r') as f:
                    header = f.readline().strip()
                    delimiter = detect_delimiter(header)
                    columns = len(header.split(delimiter))
                    formats.append((file, delimiter, columns))
    return formats

def validate_file(file_path, expected_columns=34):
    """Validates an entire file."""
    errors = []
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
        for i, line in enumerate(lines[2:], start=3):  # Start from line 3
            valid, error = validate_data_line(line, expected_columns)
            if not valid:
                errors.append(f"Line {i} error: {line.strip()} - {error}")
            else:
                print(f"Line {i} is valid: {line.strip()}")
    return errors

def validate_all_files(directory, log_file_path, expected_columns=34):
    """Validates all files in a directory and logs errors."""
    if not os.path.isdir(directory):
        print(f"Directory not found: {directory}")
        return
    files = [os.path.join(root, file) for root, _, files in os.walk(directory) for file in files if file.endswith(".dat")]

    # Check uniform format across all files
    print("Checking uniformity of formats...")
    formats = check_uniform_format(directory)
    unique_formats = set((fmt[1], fmt[2]) for fmt in formats)
    if len(unique_formats) > 1:
        print("Found inconsistent formats:")
        for fmt in unique_formats:
            print(f"  Delimiter: {fmt[0]}, Columns: {fmt[1]}")

    # Validate individual files
    with open(log_file_path, 'w') as log_file:
        for file_path in tqdm(sorted(files), desc="Validating files"):
            errors = validate_file(file_path, expected_columns)
            if errors:
                print(f"Invalid file format: {file_path}")
                log_file.write(f"Invalid file format: {file_path}\n")
                for error in errors:
                    log_file.write(f"  {error}\n")
    print(f"Validation completed. Check the log file: {log_file_path}")

if __name__ == "__main__":
    dir_path = "/home/richard.yabrudy.7e6/Escriptori/DADES/Richard Yabrudy/TA06-Garcia-Erick-Yabrudy-Richard-Francisco-Diaz-Grupo03/TA06/E01/dades"
    log_file_path = "/home/richard.yabrudy.7e6/Escriptori/DADES/validation_log.txt"
    validate_all_files(dir_path, log_file_path)