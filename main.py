import numpy
import pandas as pd
import seaborn as sns
import numpy as np
# import missingno as msno
from modules.preload_data import fill_na, fill_errors
from modules.calculations import calculate_normal_time, Calculator
from modules.diagrams import DiagramCreator
from modules.hypotheses import kruskal_test_region, numeric_and_numeric_hypo
from scipy.stats import shapiro
import matplotlib.pyplot as plt
import warnings

warnings.filterwarnings('ignore')


def check_normal(values: pd.Series, alp: float) -> bool:
    return shapiro(values).pvalue > alp


def replace_mistakes(data: pd.DataFrame) -> pd.DataFrame:
    data["region"] = data["region"].replace("Unjted States", "United States")
    data["region"] = data["region"].replace("Frаnce", "France")  # it's NOT the same
    data["region"] = data["region"].replace("Frаncе", "France")  # it's NOT the same
    data["region"] = data["region"].replace("Franсe", "France")  # it's NOT the same

    data["region"] = data["region"].replace("germany", "Germany")
    data["region"] = data["region"].replace("UK", "UК")  # it's NOT the same

    data["channel"] = data["channel"].replace("контексная реклама", "контекстная реклама")
    data["device"] = data["device"].replace("Android", "android")  # idk what name we will use? but i like this
    # maybe there are other mistakes in columns
    # maybe we can use list with for
    # we have 0.86271506 value in promo_code? but it needs to be 0 or 1
    data["promo_code"] = data["promo_code"].replace(0.86271506, 1)

    # print(data["promo_code"].unique())
    return data


def time_of_day(hours: int) -> str:
    if 360 <= (hours * 60) <= 599:  # 06:00 - 09:59
        return "Утро"
    elif 600 <= (hours * 60) <= 1019:  # 10:00 - 16:59
        return "День"
    elif 1020 <= (hours * 60) <= 1319:  # 17:00 - 21:59
        return "Вечер"
    else:
        return "Ночь"


def to_time_columns(data: pd.DataFrame) -> pd.DataFrame:
    data['session_date'] = pd.to_datetime(data['session_date'], format='%Y-%m-%d')  # Приведение к правильному формату
    data['session_start'] = pd.to_datetime(data['session_start'], format='%Y-%m-%d %H:%M:%S')
    data['session_end'] = pd.to_datetime(data['session_end'], format='%Y-%m-%d %H:%M:%S')
    data["time_of_day"] = data["hour_of_day"].apply(time_of_day)
    return data


def fill_all_errors(data: pd.DataFrame) -> pd.DataFrame:
    data = fill_errors(data, "sessiondurationsec", "median")
    data = fill_errors(data, "revenue", "median")
    return data


def plot_corr_with_nans(data: pd.DataFrame, x: str, y: str, payer: str | None = "yes") -> None:
    if payer:
        data = data[data["payer"] == payer]
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(14, 4))
    sns.boxplot(data.dropna(), x=x, y=y, ax=ax1)
    sns.boxplot(fill_na(data.copy(), x, "mode"), x=x, y=y, ax=ax2)
    sns.boxplot(data.fillna({x: "other"}), x=x, y=y, ax=ax3)


def fill_missing_with_dup(data: pd.DataFrame, rows: pd.Series, column: str) -> pd.DataFrame:
    data.loc[rows, column] = data.loc[rows, column].fillna(method="ffill").fillna(method="bfill")
    return data


def fill_missing_data_categorical(data: pd.DataFrame) -> pd.DataFrame:
    user_ids = data["user_id"].unique()
    for user_id in user_ids:
        if len(data[data["user_id"] == user_id]) == 1:
            continue
        rows = data["user_id"].map(lambda x: x == user_id)
        data = fill_missing_with_dup(data, rows, "region")
        data = fill_missing_with_dup(data, rows, "device")
        data = fill_missing_with_dup(data, rows, "channel")
    return data


df = pd.read_csv("./data/data.csv", encoding="utf-8", sep=",")
df.columns = df.columns.str.lower().str.replace(" ", "_")
df = replace_mistakes(df)
df = to_time_columns(df)
df = fill_all_errors(df)
df["promo_code"] = df["promo_code"].fillna(0)
df["revenue"] = df["revenue"].fillna(0)
df["payer"] = df["revenue"].map(lambda x: "yes" if x != 0 else "no")
df["sum"] = df["revenue"] * (1 - df["promo_code"] / 10)
df = df.drop_duplicates(subset=["user_id", "session_start", "session_end"])
df = fill_missing_data_categorical(df)
new_df_dub = df[df["user_id"].isin(df["user_id"][df["user_id"].duplicated()])].sort_values("user_id")
# print(new_df_dub)  # [["user_id", "session_date", "revenue"]])
for col in ['region', 'device', 'channel']:
    df = fill_na(df, column=col, method='mode')

# kruskal_test_region(df, "Среднее количество покупок в день одинаково со всеми устройствами",
#                     "Среднее количество покупок в день различается в зависимости от типа устройства",
#                     'device')
# # Различий между средним количеством покупок в день одинаково независимо от типа устройства во всех регионах
# kruskal_test_region(df, "Среднее количество покупок в день одинаково в зависимости от типа рекламного канала",
#                     "Среднее количество покупок в день различается в зависимости от типа рекламного канала",
#                     'channel')
# Между средним количеством покупок в регионе United States есть различия, в зависимости от типа рекламного канала
# После проведения попарных сравнений можно заметить, что среднее количество покупок в день у пользователей, пришедших
# из социальных сете будет выше, чем у пользователей, пришедших от рекламы блогеров
# print(df[df["region"].isnull()])
# print(df.isna().sum())
# for column in list(df):
#     print(df[column].value_counts())

# print(df.head(30))
# sns.histplot(df["sessiondurationsec"])
# df = df[df.duplicated() is True]
# print((df.isna().sum() / len(df)).round(4) * 100)

# columns = df.columns[-4:]
# print(df[columns].isna().corr())

# the user did not make a purchase
# for col in columns:
#     df[col].fillna("не совершал", inplace=True)
# BUT we shouldn't fill it with strings (it is number type)


# mode, because the data is categorical
# df["region"] = fill_na(df, "region", "mode")

# sns.set()


# Расчеты
# calculator = Calculator(df)
# calculator.print_mean_sum_with_and_without_payers()
# calculator.print_session_duration_by_column(column="channel", russian_name="Рекламный канал")
# calculator.print_session_duration_by_column(column="device", russian_name="Девайс")
# calculator.print_top3_sum_by_column(column="device", russian_name="Девайс")
# calculator.print_top3_sum_by_column(column="channel", russian_name="Рекламный канал")
# calculator.print_top3_sum_by_column(column="region", russian_name="Регион")
# calculator.print_mean_purchase_count_by_1_customer()
# calculator.print_top3_months_mean_sum_by_column(column="region", russian_name="регионам")
# calculator.print_top3_mau_column(column="channel", russian_name="рекламным каналам")
# calculator.print_summary_table()

# Графики
# diagrams = DiagramCreator(df)
# diagrams.pie_of_payers_by_column(column="region")
# diagrams.pie_of_payers_by_column(column="channel")
# diagrams.pie_of_payers_by_column(column="device")
# diagrams.hist_of_column_by_payer(column="region")
# diagrams.hist_of_column_by_payer(column="device")
# diagrams.hist_of_column_by_payer(column="channel")
# diagrams.hist_of_payers_count_by_column(column="payment_type")
# diagrams.hist_of_payers_by_time()

# plt.show()


h0 = "Средняя продолжительность сессии одинакова у платящих и неплатящих пользователей"
h1 = "Средняя продолжительность сессии не совпадает у платящих и неплатящих пользователей"
numeric_and_numeric_hypo(df["sessiondurationsec"], df["sum"], h0, h1)
print("коэффициент корреляции ниже 0.3, так что по шкале Чеддока можно сказать, что корреляция отсутствует")
print("т.к. p-value больше 0.05, альтернативную гипотезу принимать нельзя")