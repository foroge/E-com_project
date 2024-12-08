import pandas as pd
from scipy.stats import kruskal, mannwhitneyu, ttest_ind, f_oneway
from modules.criterions import check_normal


def cheddock_scale(coef: float) -> str:
    result = ""
    if coef > 0.9:
        result = "Корреляция шкал очень высокая"
    elif coef > 0.7:
        result = "Корреляция шкал высокая"
    elif coef > 0.5:
        result = "Корреляция шкал средняя"
    elif coef > 0.3:
        result = "Корреляция шкал слабая"
    elif coef > 0.1:
        result = "Корреляция шкал очень cлабая"
    else:
        result = "Корреляции между шкалами нет"
    return result


def kruskal_test_region(data: pd.DataFrame, h0: str, h1: str, column: str) -> None:
    print(f"Проверка гипотезы: '{h0}'\nс альтернативной гипозетой: '{h1}'")
    grouped_data = data.groupby(["region", column, "session_date"]).agg(
        purchases=("revenue", lambda x: (x > 0).sum())
    ).reset_index()
    print('\u2500' * 10)
    for region in grouped_data["region"].unique():
        region_data = grouped_data[grouped_data["region"] == region]
        print(f"Регион: {region}")

        p_value = kruskal_test(region_data, x=column, y="purchases")
        print(f"Тест Краскела-Уоллиса: p-value = {p_value}")
        if p_value < 0.05:
            print(f"Для региона {region} принимаем альтернативную гипотезу")
        else:
            print(f"Для региона {region} альтернативную гипотезу принимать нельзя")
        print('\u2500' * 10)
    print()


def kruskal_test(data: pd.DataFrame, category: str, quantitative: str, rnd: int = 4) -> float:
    uniq = data[category].unique()
    stat, p = kruskal(*[data[data[category] == uniq[i]][quantitative] for i in range(len(uniq))])
    return round(float(p), rnd)


def anova_test(data: pd.DataFrame, category: str, quantitative: str, rnd: int = 4) -> float:
    uniq = data[category].unique()
    stat, p = kruskal(*[data[data[category] == uniq[i]][quantitative] for i in range(len(uniq))])
    return round(float(p), rnd)


def quantitative_and_categorical(data: pd.DataFrame, category: str, quantitative: str, rnd: int = 4):
    if data[category].unique() > 2:
        return quantitative_and_categorical_3(data, category, quantitative, rnd)
    else:
        return quantitative_and_categorical_2(data[category], data[quantitative], rnd)


def quantitative_and_categorical_2(br: pd.DataFrame, gd: pd.DataFrame, rnd: int = 4):
    if check_normal(br, 0.05) and check_normal(gd, 0.05):
        return float(round(mannwhitneyu(br, gd, alternative="two-sided").pvalue), rnd)
    else:
        return float(round(ttest_ind(br, gd, alternative="two-sided").pvalue, rnd))


def quantitative_and_categorical_3(data: pd.DataFrame, category: str, quantitative: str, rnd: int = 4) -> float:
    if check_normal(data[category], 0.05) and check_normal(data[quantitative], 0.05):
        return anova_test(data, category, quantitative, rnd)
    else:
        return kruskal_test(data, category, quantitative, rnd)
