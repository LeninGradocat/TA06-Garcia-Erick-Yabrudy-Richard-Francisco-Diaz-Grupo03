from datetime import datetime
from rich.console import Console
from rich.table import Table

# Initialize Rich console
console = Console()


def calculate_media_annual(yearly_data):
    """Calculates the annual average rainfall."""
    media_annual = {}
    for year, data in yearly_data.items():
        if data['count'] > 0:  # Avoid division by zero
            media_annual[year] = data['total_rainfall'] / data['count']
        else:
            media_annual[year] = 0
    return media_annual


def calculate_statistics(yearly_data):
    """Calculates statistics from yearly data."""
    current_year = datetime.now().year
    filtered_data = {year: data for year, data in yearly_data.items() if year <= current_year}

    if not filtered_data:
        return {
            'total_years': 0,
            'total_rainfall': 0,
            'average_rainfall': 0,
            'driest_year': (None, 0),
            'wettest_year': (None, 0),
        }

    total_years = len(filtered_data)
    total_rainfall = sum(data['total_rainfall'] for data in filtered_data.values())
    average_rainfall = total_rainfall / total_years if total_years else 0
    yearly_rainfall = {year: data['total_rainfall'] for year, data in filtered_data.items()}
    sorted_years = sorted(yearly_rainfall.items(), key=lambda x: x[1])
    driest_year = sorted_years[0] if sorted_years else (None, 0)
    wettest_year = sorted_years[-1] if sorted_years else (None, 0)

    return {
        'total_years': total_years,
        'total_rainfall': total_rainfall,
        'average_rainfall': average_rainfall,
        'driest_year': driest_year,
        'wettest_year': wettest_year,
    }


def display_annual_rainfall(media_annual):
    """Displays the annual average rainfall."""
    table = Table(title="Annual Average Rainfall")

    table.add_column("Year", justify="right", style="cyan", no_wrap=True)
    table.add_column("Average Rainfall (mm)", justify="right", style="magenta")

    for year, rainfall in sorted(media_annual.items()):
        table.add_row(str(year), f"{rainfall:.2f}")

    console.print(table)
