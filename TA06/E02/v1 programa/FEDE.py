import os

def get_file_info(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        header = lines[0].strip()
        delimiter = None
        if ',' in header:
            delimiter = ','
        elif '\t' in header:
            delimiter = '\t'
        else:
            delimiter = ' '

        columns = header.split(delimiter)
        num_columns = len(columns)

        return {
            'file_path': file_path,
            'delimiter': delimiter,
            'num_columns': num_columns,
            'columns': columns
        }

def validate_files(directory):
    file_infos = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.dat'):
                file_path = os.path.join(root, file)
                file_info = get_file_info(file_path)
                file_infos.append(file_info)
                print(f"Validating file: {file_path}")

    if not file_infos:
        print("No .dat files found in the directory.")
        return

    reference_info = file_infos[0]
    for file_info in file_infos[1:]:
        if file_info['delimiter'] != reference_info['delimiter']:
            print(f"Delimiter mismatch in file: {file_info['file_path']}")
        if file_info['num_columns'] != reference_info['num_columns']:
            print(f"Column count mismatch in file: {file_info['file_path']}")
        if file_info['columns'] != reference_info['columns']:
            print(f"Column names mismatch in file: {file_info['file_path']}")

    print("Validation completed.")

# Directory path
directory_path = '/home/erick.garcia.7e8/PycharmProjects/TA06-Garcia-Erick-Yabrudy-Richard-Francisco-Diaz-Grupo03'
validate_files(directory_path)