import pandas as pd
from scipy.stats import kruskal, mannwhitneyu


def device_purchases_by_region(data: pd.DataFrame) -> None:
    grouped_data = data.groupby(["region", "device", "session_date"]).agg(
        purchases=("revenue", lambda x: (x > 0).sum())
    ).reset_index()

    for region in grouped_data["region"].unique():
        region_data = grouped_data[grouped_data["region"] == region]
        print(f"Регион: {region}")

        stat, p_value = kruskal_test(region_data, x="device", y="purchases")
        print(f"Тест Краскела-Уоллиса: H-статистика = {stat}, p-value = {p_value}")
        if p_value < 0.05:
            print("Результат: Тип устройства влияет на количество покупок в день.")
        else:
            print("Результат: Нет доказательств, что тип устройства влияет на количество покупок в день.")


def kruskal_test(data: pd.DataFrame, x: str, y: str) -> tuple:
    uniq = data[x].unique()
    stat, p = kruskal(*[data[data[x] == uniq[i]][y] for i in range(len(uniq))])
    return float(stat), float(p)

