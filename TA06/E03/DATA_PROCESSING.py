import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "../E01/data-testing")

def get_file_path(filename):
    """Obtiene la ruta absoluta del archivo dentro del directorio de datos."""
    return os.path.join(DATA_DIR, filename)

def detect_delimiter(line):
    """Detecta el delimitador más frecuente en una línea."""
    delimiters = {'\t': line.count('\t'), ',': line.count(','), ' ': line.count(' ')}
    return max(delimiters, key=delimiters.get)

def normalize_delimiter(file_path, delimiter, target_delimiter='\t'):
    """Normaliza delimitadores en un archivo."""
    from rich.console import Console
    from rich.panel import Panel

    console = Console()

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