import os
import sys
from VALIDATION import validate_file
from DATA_PROCESSING import calculate_statistics, calculate_media_annual, display_annual_rainfall

# Configurar ruta del archivo a analizar
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "../E01/data-testing")

def get_file_path(filename):
    """Obtiene la ruta absoluta del archivo dentro del directorio de datos."""
    return os.path.join(DATA_DIR, filename)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python STADISTICS.py <nombre_archivo>")
        sys.exit(1)

    filename = sys.argv[1]
    file_path = get_file_path(filename)

    if not os.path.exists(file_path):
        print(f"Error: El archivo '{filename}' no se encuentra en {DATA_DIR}")
        sys.exit(1)

    # Validar el archivo
    errors, total_values, missing_values, total_rainfall, lines_processed, yearly_data = validate_file(filename)

    if errors:
        print("\n🔴 Errores encontrados en el archivo:")
        for error in errors:
            print(f" - {error}")
    else:
        print("\n✅ Archivo validado exitosamente.")

    # Analizar estadísticas
    statistics = calculate_statistics(yearly_data)
    media_annual = calculate_media_annual(yearly_data)

    # Mostrar resultados
    print("\n📊 Estadísticas Generales:")
    print(f" - Años analizados: {statistics['total_years']}")
    print(f" - Total de precipitación registrada: {statistics['total_rainfall']:.2f} mm")
    print(f" - Promedio anual de precipitación: {statistics['average_rainfall']:.2f} mm")
    print(f" - Año más seco: {statistics['driest_year'][0]} con {statistics['driest_year'][1]['total_rainfall']:.2f} mm")
    print(f" - Año más lluvioso: {statistics['wettest_year'][0]} con {statistics['wettest_year'][1]['total_rainfall']:.2f} mm")

    # Mostrar tabla de precipitación anual
    display_annual_rainfall(media_annual)
from VALIDATION import validate_file
from DATA_PROCESSING import calculate_statistics, calculate_media_annual, display_annual_rainfall

if __name__ == "__main__":
    filename = "../E01/data-testing"

    errors, total_values, missing_values, total_rainfall, lines_processed, yearly_data = validate_file(filename)

    if errors:
        print("Errores encontrados:")
        for error in errors:
            print(error)
    else:
        print("Archivo validado exitosamente.")

    statistics = calculate_statistics(yearly_data)
    media_annual = calculate_media_annual(yearly_data)

    print("Estadísticas Generales:")
    print(statistics)

    display_annual_rainfall(media_annual)
