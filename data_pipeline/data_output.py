import logging
from pathlib import Path


logger = logging.getLogger(__name__)


def save_data(df, filepath):
    """Save a DataFrame as a CSV file."""
#     Requirements:

# * Use `pathlib` to work with the output path.
    path = Path(filepath)
    
# * Create the output directory if it does not exist.
#     * Hint: Path(filepath).parent.mkdir(parents=True, exist_ok=True) 
    path.parent.mkdir(parents=True, exist_ok=True)
# * Save the DataFrame as CSV without the index.
    df.to_csv(path, index=False)
# * Log the number of rows saved and the output path at the `DEBUG` level.
    logger.debug(f"Saved {len(df)} rows to {path}")

# * Return the output path.
    return path