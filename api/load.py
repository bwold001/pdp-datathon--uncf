"""Load the standalone deployment database using the existing data model loader."""
from pathlib import Path
import subprocess
import sys
from measures.run_measures import DEFAULT_DATABASE

def ensure_data_loaded():
    """Build the default SQLite extract only when it is absent."""
    if not DEFAULT_DATABASE.exists():
        subprocess.run([sys.executable, "-m", "src.loader.load"],
                       cwd=Path(__file__).resolve().parents[1] / "normalized-data-model", check=True)
