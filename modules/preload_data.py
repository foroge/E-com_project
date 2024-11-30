import pandas as pd


def fill_na(data: pd.DataFrame | pd.Series, column: str, method: str, group: list[str] = None):
    """
    :param data: pd.DataFrame
    :param column: name of the column to fill
    :param method: ["drop", "median", "back", "mean", "mode", "interpolate"]
    :param group: list of column names
    :return: modified data
    """
    match method:
        case "mean" | "median":
            data[column].fillna(data.groupby(group)[column].transform(method), inplace=True)
        case "mode":
            data[column].fillna(data.groupby(group)[column].transform(lambda x: x.mode()[0]), inplace=True)
        case "back":
            data[column] = data[column].bfill()
        case "interpolate":
            data[column] = data[column].interpolate()
        case "drop":
            data[column].dropna(inplace=True)
        case _:
            raise ValueError(f"method {method} not found")
    return data


def fill_errors(df: pd.DataFrame, columns: str | list[str], fill_with: str, err_range: float = 3) -> pd.DataFrame:
    """
    :param df: pd.DataFrame
    :param columns: list of column names
    :param fill_with: ["drop", "median", "mean", "mode"]
    :param err_range: 3 for strong mistakes, 1.5 for usual mistakes
    :return: modified data
    """
    if isinstance(columns, str):
        columns = [columns]
    for col in columns:
        err_max = df[col].quantile(0.75) + err_range * (df[col].quantile(0.75) - df[col].quantile(0.25))
        err_min = df[col].quantile(0.25) - err_range * (df[col].quantile(0.75) - df[col].quantile(0.25))
        match fill_with:
            case "median":
                med = df[col].median()
            case "mean":
                med = df[col].mean()
            case "mode":
                med = df[col].mode()
            case "drop":
                df[col] = df[err_max > df[col] > err_min][col]
                continue
            case _:
                raise ValueError(f"unable to fill column {col} with {fill_with}")
        df[col] = df[col].map(lambda x: med if x >= err_max or x <= err_min else x)
    return df


