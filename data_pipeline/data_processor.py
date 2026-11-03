import logging
import pandas as pd

logger = logging.getLogger(__name__)

def remove_duplicates(df):
    """Remove duplicate rows."""
    before = len(df)
    df = df.drop_duplicates()
    after = len(df)
    logger.debug(f"remove_duplicates: {before} -> {after} rows") #Removed {before - after} duplicate rows. Specifically, 
    return df


def handle_missing(df, axis="rows"):
    """Drop rows or columns containing missing values."""
    
    before_rows, before_cols = df.shape  # (rows_before, cols_before)

    if axis == "rows":
        df = df.dropna(axis=0)
        after_rows = len(df)  # (rows_after, cols_after)
        logger.debug(f"handle_missing: {before_rows} -> {after_rows} rows") #Removed {before_rows - after_rows} rows containing missing values. Specifically, 

    elif axis == "columns":
        df = df.dropna(axis=1)
        after_cols = df.shape[1] # (rows_after, cols_after)
        logger.debug(f"handle_missing: {before_cols} -> {after_cols} columns") #Removed {before_cols - after_cols} columns containing missing values. Specifically, 

    else:
        logger.error(f"Unsupported axis value: {axis}")
        raise ValueError(f"Unsupported axis value: {axis}")
  
    return df


def remove_outliers(df, columns, method, threshold):
    """Remove outliers from the specified numeric columns."""

    # Validate method first — fail fast regardless of columns
    if method not in ("iqr", "zscore"):
        logger.error(f"Unsupported outlier method: {method}")
        raise ValueError(f"Unsupported outlier method: {method}")

    for col in columns:

        # Column must exist
        if col not in df.columns:
            logger.warning(f"Column not found: {col}")
            continue

        # Column must be numeric
        if not pd.api.types.is_numeric_dtype(df[col]):
            logger.warning(f"Column not numeric: {col}")
            continue

        before = len(df)

        if method == "iqr":
            q1 = df[col].quantile(0.25)
            q3 = df[col].quantile(0.75)
            iqr = q3 - q1
            lower = q1 - threshold * iqr
            upper = q3 + threshold * iqr
            df = df[(df[col] >= lower) & (df[col] <= upper)]

        elif method == "zscore":
            mean = df[col].mean()
            std = df[col].std()
            zscores = (df[col] - mean) / std
            df = df[zscores.abs() <= threshold]

        rows_removed = before - len(df)
        logger.debug(f"{col}: method={method}, threshold={threshold}, removed={rows_removed}")

    return df


def process_data(df, config):
    """Apply the processing steps enabled in the configuration."""

    steps = config.get("processing", {})
    
    if steps.get("remove_duplicates", False):
        df = remove_duplicates(df)

    missing_cfg = steps.get("missing", {})
    if missing_cfg.get("enabled", False):
        axis = missing_cfg.get("axis", "rows")
        df = handle_missing(df, axis=axis)

    out_cfg = steps.get("outliers", {})
    if out_cfg.get("enabled", False):
        df = remove_outliers(
            df,
            columns=out_cfg.get("columns", []),
            method=out_cfg.get("method", "iqr"),
            threshold=out_cfg.get("threshold", 1.5),
        )

    return df



def create_cleaning_report(df_before, df_after):
    """Return a dictionary summarizing the cleaning results."""
    report = {
    "rows_before": len(df_before),
    "rows_after": len(df_after),
    "rows_removed": len(df_before) - len(df_after),
    "columns_before": df_before.shape[1],
    "columns_after": df_after.shape[1],
    "columns_removed": df_before.shape[1] - df_after.shape[1],
    }

    return report