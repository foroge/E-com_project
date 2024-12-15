import pandas as pd
from scipy.stats import kruskal, mannwhitneyu, ttest_ind, f_oneway, pearsonr, spearmanr, shapiro
from itertools import combinations


# Проверка данных на нормальность распределения по Шапиро-Уилку
def check_normal(values: pd.Series, alp: float) -> bool:
    """
    :param values: pd.Series
    :param alp: Альфа критерий
    :return: bool, нормальность распределения данных по Шапиро-Уилку
    """
    return shapiro(values).pvalue > alp


# Проверка гипотезы о влиянии столбца на среднее количество покупок в де
def check_avg_num_of_purchases(data: pd.DataFrame, h0: str, h1: str, column: str) -> None:
    """
    :param data: pd.DataFrame
    :param h0: Нулевая гипотеза
    :param h1: Альтернативная гипотеза
    :param column: Название столбца, по которому считается среднее количество покупок в день
    :return: None, выводятся результаты и комментарии к ним
    """
    print(f"Проверка гипотезы: '{h0}'\nс альтернативной гипозетой: '{h1}'")
    grouped_data = data.groupby(["region", column, "session_date"]).agg(
        purchases=("revenue", lambda x: (x > 0).sum())
    ).reset_index()
    print('\u2500' * 10)
    for region in grouped_data["region"].unique():
        region_data = grouped_data[grouped_data["region"] == region]
        print(f"Регион: {region}")

        p_value = quantitative_and_categorical(region_data, column, "purchases")
        print(f"P-value = {p_value}")
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
            print(f"Для региона {region} нельзя отвергнуть нулевую гипотезу")

        print('\u2500' * 10)
    print()


# Проверка гипотезы о влиянии столбца на средний чек
def check_avg_revenue_hypotheses(data: pd.DataFrame, h0: str, h1: str, column: str) -> None:
    """
    :param data:
    :param h0: Нулевая гипотеза
    :param h1: Альтернативная гипотеза
    :param column: Название столбца, по которому проверяется гипотеза
    :return: None, выводятся результаты и комментарии к ним
    """
    print(f"Проверка гипотезы: '{h0}'\nс альтернативной гипозетой: '{h1}'")
    print('\u2500' * 10)

    mean_revenue_table = (data.groupby(column, as_index=False)["sum"].mean().rename(columns={"sum": "mean_revenue"}))

    p_value = quantitative_and_categorical(mean_revenue_table, column, "mean_revenue")
    print(f"P-value = {p_value}")
    if p_value < 0.05:
        print(f"Принимаем альтернативную гипотезу: {h1}")
    else:
        print(f"Нельзя отвергнуть нулевую гипотезу: {h0}")
    print('\u2500' * 10)
    print()


# Проверка гипотезы о влиянии совершения покупки на длительность сессии
def duration_of_the_purchase(data: pd.DataFrame, h0: str, h1: str, column: str) -> None:
    """
    :param data:
    :param h0: Нулевая гипотеза
    :param h1: Альтернативная гипотеза
    :param column: Название столбца, по которому проверяется гипотеза
    :return: None, выводятся результаты и комментарии к ним
    """
    print(f"Проверка гипотезы: '{h0}'\nс альтернативной гипозетой: '{h1}'")
    print('\u2500' * 10)

    buyers = data[data[column] == "yes"]["sessiondurationsec"]
    not_buyers = data[data[column] == "no"]["sessiondurationsec"]

    p_value = quantitative_and_categorical_2(buyers, not_buyers, 4)
    print(f"P-value = {p_value}")

    if p_value < 0.05:
        print(f"Принимаем альтернативную гипотезу: {h1}")
    else:
        print(f"Нельзя отвергнуть нулевую гипотезу: {h0}")
    print('\u2500' * 10)
    print()


# Проверка гипотезы о влиянии типа оплаты на длительность сессии
def duration_depends_on_the_payment_type(data: pd.DataFrame, h0: str, h1: str, column: str) -> None:
    """
    :param data: pd.DataFrame
    :param h0: Нулевая гипотеза
    :param h1: Альтернативная гипотеза
    :param column: Название столбца, по которому проверяется гипотеза
    :return:
    """
    print(f"Проверка гипотезы: '{h0}'\nс альтернативной гипозетой: '{h1}'")
    print('\u2500' * 10)

    p_value = quantitative_and_categorical(data[data["payer"] == "yes"], column, "sessiondurationsec", 4)
    print(f"P-value = {p_value}")
    if p_value < 0.05:
        print(f"Принимаем альтернативную гипотезу: {h1}")
    else:
        print(f"Нельзя отвергнуть нулевую гипотезу: {h0}")
    print('\u2500' * 10)
    print()


# Определение p-value по Краскелу-Уоллису
def kruskal_test(columns: list[pd.Series], rnd: int = 4) -> float:
    """
    :param columns: Название столбцов, по которым считается p-value по Краскелу-Уоллису
    :param rnd: До какого знака округление
    :return: P-value
    """
    p = kruskal(*columns).pvalue
    return round(float(p), rnd)


# Определение p-value по ANOVA
def anova_test(columns: list[pd.Series], rnd: int = 4) -> float: # расчет p-value по ANOVA
    """
    :param columns: Название столбцов, по которым считается p-value по ANOVA
    :param rnd: До какого знака округление
    :return: P-value
    """
    p = f_oneway(*columns).pvalue
    return round(float(p), rnd)


# Расчет p-value для категориального и количественного столбцов
def quantitative_and_categorical(data: pd.DataFrame, category: str, quantitative: str, rnd: int = 4) -> float:
    """
    :param data: pd.DataFrame
    :param category: Название категориального столбца
    :param quantitative: Название количественного столбца
    :param rnd: До какого знака округление
    :return: p-value по нужному критерию (функция отправляет данные дальше, для выбора нужного метода)
    """
    if len(data[category].unique()) > 2:
        print("Уровней больше 2-х, значит выбираем между ANOVA и Краскела-Уоллиса")
        return quantitative_and_categorical_3(data, category, quantitative, rnd)
    else:
        print("Всего 2 уровня, значит выбираем между Т-критерием Стьюдента и U-критерием Манны-Уитни")
        columns = data[category].unique()
        br = data[data[category] == columns[0]][quantitative]
        gd = data[data[category] == columns[1]][quantitative]
        return quantitative_and_categorical_2(br, gd, rnd)


# Расчет p-value для столбцов с 2-мя уровнями
def quantitative_and_categorical_2(br: pd.DataFrame, gd: pd.DataFrame, rnd: int = 4):
    """
        :param data: pd.DataFrame
        :param category: Название категориального столбца
        :param quantitative: Название количественного столбца
        :param rnd: До какого знака округление
        :return: p-value по нужному критерию
    """
    if check_normal(br, 0.05) and check_normal(gd, 0.05):
        print("Распределение нормальное, поэтому выбираем Т-критерий Стьюдента")
        return float(round(ttest_ind(br, gd, alternative="two-sided").pvalue, rnd))
    else:
        print("Распределение ненормальное, поэтому выбираем U-крпитерий Манны-Уитни")
        return float(round(mannwhitneyu(br, gd, alternative="two-sided").pvalue, rnd))


# Расчет p-value для столбцов с более чем 2-мя уровнями
def quantitative_and_categorical_3(data: pd.DataFrame, category: str, quantitative: str, rnd: int = 4) -> float:
    """
        :param data: pd.DataFrame
        :param category: Название категориального столбца
        :param quantitative: Название количественного столбца
        :param rnd: До какого знака округление
        :return: p-value по нужному критерию
    """
    unique = data[category].unique()
    columns = [data[data[category] == column][quantitative] for column in unique]
    if all([check_normal(column, 0.05) for column in columns]):
        print("Распределение нормальное, поэтому выбираем ANOVA")
        return anova_test(columns, rnd)
    else:
        print("Распределение ненормальное, поэтому выбираем Краскела-Уоллиса")
        return kruskal_test(columns, rnd)


# Попарное сравнение двух столбцов
def pairwise_comparisons(data: pd.DataFrame, column: str, quantitative: str) -> pd.DataFrame:
    """
    :param data: pd.DataFrame
    :param column: Категориальный столбец
    :param quantitative: Количественный столбец
    :return: Датафрейм, с результатами проведенных попарных сравнений
    """
    head = ["p-value", "1 тип", "2 тип"]
    result = []
    for combination in combinations(data[column].unique(), 2):
        br = data[data[column] == combination[0]][quantitative]
        gd = data[data[column] == combination[1]][quantitative]
        result.append([quantitative_and_categorical_2(br, gd), combination[0], combination[1]])
    return pd.DataFrame(result, columns=head)


# Рассчет корреляции Пирсона
def count_pearson(br: pd.Series, gd: pd.Series, rnd: int = -1) -> str:
    """
    :param br: Данные для расчета корреляции
    :param gd: Данные для расчета корреляции
    :param rnd: До какого знака округление
    :return: str, коэффициент корреляции и p-value
    """
    pears = pearsonr(br, gd)
    if rnd >= 0:
        return f"statistics: {float(round(pears.statistic, rnd))}\npvalue: {float(round(pears.pvalue, rnd))}"
    return f"statistics: {float(pears.statistic)}\npvalue: {float(pears.pvalue)}"


# Рассчет корреляции Спирмена
def count_spearman(br: pd.Series, gd: pd.Series, rnd: int = -1) -> str:
    """
    :param br: Данные для расчета корреляции
    :param gd: Данные для расчета корреляции
    :param rnd: До какого знака округление
    :return: str, коэффициент корреляции и p-value
    """
    spear = spearmanr(br, gd)
    if rnd >= 0:
        return f"statistics: {float(round(spear.statistic, rnd))}\npvalue: {float(round(spear.pvalue, rnd))}"
    return f"statistics: {float(spear.statistic)}\npvalue: {float(spear.pvalue)}"


# Определение нужного метода для рассчета корреляции и её расчет
def numeric_and_numeric(br: pd.Series, gd: pd.Series, rnd: int = 4) -> str:
    """
    :param br: Данные для расчета корреляции
    :param gd: Данные для расчета корреляции
    :param rnd: До какого знака округление
    :return: str, коэффициент корреляции и p-value (по нужному методу)
    """
    if check_normal(br, 0.05) and check_normal(gd, 0.05):
        print(f"Данные распределены нормально, используем корреляцию Пирсона")
        return count_pearson(br, gd, rnd)
    else:
        print(f"Данные распределены ненормально, используем корреляцию Спирмена")
        return count_spearman(br, gd, rnd)


# Проверка гипотезы о влиянии продолжительности сессии на платежеспособность
def numeric_and_numeric_hypo(br: pd.Series, gd: pd.Series, h0: str, h1: str):
    """
    :param br: Данные для рассчета корреляции
    :param gd: Данные для рассчета корреляции
    :param h0: Нулевая гипотеза
    :param h1: Альтернативная гипотеза
    :return: None, выводятся данные по корреляции столбцов
    """
    print(f"Проверка гипотезы: '{h0}'\nс альтернативной гипозетой: '{h1}'")
    print("Оба столбца количественные")
    print(numeric_and_numeric(br, gd))
