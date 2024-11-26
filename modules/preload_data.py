import pandas as pd


def fill_na(data: pd.DataFrame | pd.Series, column: str, method: str, group: list[str] = None):
    """
    :param data: pd.DataFrame
    :param column: name of the column to fill
    :param method: ["drop", "median", "back", "mean", "mode", "interpolate"]
    :param group: list of column names
    :return:
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

