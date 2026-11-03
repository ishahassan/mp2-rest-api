import logging
import pandas as pd


logger = logging.getLogger(__name__)


def validate_dataframe(df, required_columns, numeric_columns):
    """Validate the DataFrame and return valid data.

    required_columns: a list of column names that must exist.
    numeric_columns: a list of column names whose values should be numeric.
    """
    #  Check that every name in `required_columns` exists in the DataFrame.
    #* Log an `ERROR` and raise `ValueError` if a required column is missing.

    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        logger.error(f"Missing required columns: {missing_columns}")
        raise ValueError(f"Missing required columns: {missing_columns}")

    rows_before = len(df)

    for col in numeric_columns:
        invalid_rows = []
        for i, value in df[col].items():
            if pd.notna(value):
                try:
                    float(value)
                except ValueError:
                    # TODO: Log a warning and record this row's index.
                    logger.warning(f"Invalid value in {col}: {value}")
                    invalid_rows.append(i)
        
        # TODO: Remove the invalid rows.
        if invalid_rows:
            df = df.drop(index=invalid_rows)


        #convert to a numeric data type
        df[col] = pd.to_numeric(df[col])

#         * Log the number of valid and removed rows at the `DEBUG` level.
    logger.debug(f"Validation: {rows_before} -> {len(df)} rows") #Validating '{col}': removed {len(invalid_rows)} invalid rows

# * Return the validated DataFrame.
    return df
