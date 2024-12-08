import pandas as pd
from scipy.stats import kruskal, mannwhitneyu, ttest_ind, f_oneway, pearsonr, spearmanr, shapiro
from itertools import combinations


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


def check_normal(values: pd.Series, alp: float) -> bool:
    return shapiro(values).pvalue > alp


def kruskal_test_region(data: pd.DataFrame, h0: str, h1: str, column: str) -> None:
    print(f"Проверка гипотезы: '{h0}'\nс альтернативной гипозетой: '{h1}'")
    grouped_data = data.groupby(["region", column, "session_date"]).agg(
        purchases=("revenue", lambda x: (x > 0).sum())
    ).reset_index()
    print('\u2500' * 10)
    for region in grouped_data["region"].unique():
        region_data = grouped_data[grouped_data["region"] == region]
        print(f"Регион: {region}")

        p_value = quantitative_and_categorical(region_data, column, "purchases")
        print(f"Тест Краскела-Уоллиса: p-value = {p_value}")
        if p_value < 0.05:
            print(f"Для региона {region} принимаем альтернативную гипотезу")
            print("Проведем попарные сравнения")
            p_c_df = pairwise_comparisons(region_data, column, "purchases")
            result = p_c_df.loc[p_c_df["p-value"] < 0.05]
            print("Записи с p-value < 0.05")
            print(result)
            for i, record in result.iterrows():
                print(f"Среднее количество покупок в день по {record["1 тип"]}: "
                      f"{round(region_data[region_data["channel"] == record["1 тип"]]["purchases"].mean(), 2)}")
                print(f"Среднее количество покупок в день по {record["2 тип"]}: "
                      f"{round(region_data[region_data["channel"] == record["2 тип"]]["purchases"].mean(), 2)}")
        else:
            print(f"Для региона {region} альтернативную гипотезу принимать нельзя")

        print('\u2500' * 10)
    print()


def check_avg_revenue_hypotheses(data: pd.DataFrame, h0: str, h1: str, column: str) -> None:
    print(f"Проверка гипотезы: '{h0}'\nс альтернативной гипозетой: '{h1}'")
    print('\u2500' * 10)

    p_value = quantitative_and_categorical(data, column, "revenue")
    print(f"Тест Краскела-Уоллиса: p-value = {p_value}")
    if p_value < 0.05:
        print(f"Принимаем альтернативную гипотезу: {h1}")
    else:
        print(f"Нельзя отвергнуть нулевую гипотезу: {h0}")
    print('\u2500' * 10)
    print()


def kruskal_test(columns: list[pd.Series], rnd: int = 4) -> float:
    p = kruskal(*columns).pvalue
    return round(float(p), rnd)


def anova_test(columns: list[pd.Series], rnd: int = 4) -> float:
    p = f_oneway(*columns).pvalue
    return round(float(p), rnd)


def quantitative_and_categorical(data: pd.DataFrame, category: str, quantitative: str, rnd: int = 4):
    if len(data[category].unique()) > 2:
        print("Уровней больше 2-х, значит выбираем между ANOVA и Краскела-Уоллиса")
        return quantitative_and_categorical_3(data, category, quantitative, rnd)
    else:
        print("Всего 2 уровня, значит выбираем между Т-критерием Стьюдента и U-крпитерием Манны-Уитни")
        columns = data[category].unique()
        br = data[data[category] == columns[0]][quantitative]
        gd = data[data[category] == columns[1]][quantitative]
        return quantitative_and_categorical_2(br, gd, rnd)


def quantitative_and_categorical_2(br: pd.DataFrame, gd: pd.DataFrame, rnd: int = 4):
    if check_normal(br, 0.05) and check_normal(gd, 0.05):
        print("Распределение нормальное, поэтому выбираем Т-критерий Стьюдента")
        return float(round(ttest_ind(br, gd, alternative="two-sided").pvalue, rnd))
    else:
        print("Распределение ненормальное, поэтому выбираем U-крпитерий Манны-Уитни")
        return float(round(mannwhitneyu(br, gd, alternative="two-sided").pvalue, rnd))


def quantitative_and_categorical_3(data: pd.DataFrame, category: str, quantitative: str, rnd: int = 4) -> float:
    unique = data[category].unique()
    columns = [data[data[category] == column][quantitative] for column in unique]
    if all([check_normal(column, 0.05) for column in columns]):
        print("Распределение нормальное, поэтому выбираем ANOVA")
        return anova_test(columns, rnd)
    else:
        print("Распределение ненормальное, поэтому выбираем Краскела-Уоллиса")
        return kruskal_test(columns, rnd)


def pairwise_comparisons(data: pd.DataFrame, column: str, quantitative: str) -> pd.DataFrame:
    head = ["p-value", "1 тип", "2 тип"]
    result = []
    for combination in combinations(data[column].unique(), 2):
        br = data[data[column] == combination[0]][quantitative]
        gd = data[data[column] == combination[1]][quantitative]
        result.append([quantitative_and_categorical_2(br, gd), combination[0], combination[1]])
    return pd.DataFrame(result, columns=head)


def count_pearson(br: pd.Series, gd: pd.Series, rnd: int = -1) -> str:
    pears = pearsonr(br, gd)
    if rnd >= 0:
        return f"statistics: {float(round(pears.statistic, rnd))}\npvalue: {float(round(pears.pvalue, rnd))}"
    return f"statistics: {float(pears.statistic)}\npvalue: {float(pears.pvalue)}"


def count_spearman(br: pd.Series, gd: pd.Series, rnd: int = -1) -> str:
    spear = spearmanr(br, gd)
    if rnd >= 0:
        return f"statistics: {float(round(spear.statistic, rnd))}\npvalue: {float(round(spear.pvalue, rnd))}"
    return f"statistics: {float(spear.statistic)}\npvalue: {float(spear.pvalue)}"


def numeric_and_numeric(br: pd.Series, gd: pd.Series, rnd: int = 4) -> str:
    if check_normal(br, 0.05) and check_normal(gd, 0.05):
        print(f"Данные распределены нормально, используем корреляцию Пирсона")
        return count_pearson(br, gd, rnd)
    else:
        print(f"Данные распределены ненормально, используем корреляцию Спирмена")
        return count_spearman(br, gd, rnd)


def numeric_and_numeric_hypo(br: pd.Series, gd: pd.Series, h0: str, h1: str):
    print(f"Проверка гипотезы: '{h0}'\nс альтернативной гипозетой: '{h1}'")
    print("Оба столбца количественные")
    print(numeric_and_numeric(br, gd))
