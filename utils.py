from pandas import DataFrame


def exclude_owid_values(dataframe: DataFrame, column_name: str) -> DataFrame:
    """Return modified dataframe without values with OWID_ prefix in `column_name`"""
    return dataframe[~dataframe[column_name].astype(str).str.startswith('OWID_')]
