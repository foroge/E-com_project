import pandas as pd
from scipy.stats import kruskal, mannwhitneyu


def kruskal_test_region(data: pd.DataFrame, column: str) -> None:
    print(f"Оценка влияния {column} на количесво покупок в день")
    influence = 0
    ansver = [['region', 'column', 'значение корреляции', 'р-уровень', 'метод корреляции']]
    grouped_data = data.groupby(["region", column, "session_date"]).agg(
        purchases=("revenue", lambda x: (x > 0).sum())
    ).reset_index()

    for region in grouped_data["region"].unique():
        region_data = grouped_data[grouped_data["region"] == region]
        print(f"Регион: {region}")

        stat, p_value = kruskal_test(region_data, x=column, y="purchases")
        print(f"Тест Краскела-Уоллиса: H-статистика = {stat}, p-value = {p_value}")
        ansver.append(["region", column, float(stat), float(p_value), 'Тест Краскела-Уоллиса'])
        if p_value < 0.05:
            influence += 1
        else:
            influence -= 1
    if influence > 0:
        print("Есть влияние")
    elif influence < 0:
        print("Нет влияния")
    else:
        print("50 на 50 смотреть и думать надо")
    print()


def kruskal_test(data: pd.DataFrame, x: str, y: str) -> tuple:
    uniq = data[x].unique()
    stat, p = kruskal(*[data[data[x] == uniq[i]][y] for i in range(len(uniq))])
    return float(stat), float(p)

