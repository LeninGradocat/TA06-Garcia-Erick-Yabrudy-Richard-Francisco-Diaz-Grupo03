from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()

def generate_summary(total_errors, lines_processed, total_values, missing_values, yearly_data):
    missing_percentage = (missing_values / total_values * 100) if total_values else 0
    summary_text = Text(f"Validation completed.\n"
                        f"Errors found: {total_errors:,}\n"
                        f"Lines processed: {lines_processed:,}\n"
                        f"Total values processed: {total_values:,}\n"
                        f"Missing values (-999) found: {missing_values:,}\n"
                        f"Percentage of missing values: {missing_percentage:.2f}%\n\n"
                        f"Annual Precipitation Averages:\n", justify="center", style="green")

    for year, data in sorted(yearly_data.items()):
        average_rainfall = data['total_rainfall'] / data['count'] if data['count'] else 0
        summary_text.append(f"Year {year}: {average_rainfall:.2f} mm\n", style="bold green")

    console.print(Panel(summary_text, border_style="bold cyan", title="Summary", expand=False))