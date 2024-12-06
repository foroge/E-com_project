import numpy
import pandas as pd
import seaborn as sns
import numpy as np
# import missingno as msno
from modules.preload_data import fill_na, fill_errors
from scipy.stats import shapiro, kruskal
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


def kruskal_test(data: pd.DataFrame, x: str, y: str) -> tuple:
    uniq = data[x].unique()
    stat, p = kruskal(*[data[data[x] == uniq[i]][y] for i in range(len(uniq))])
    return float(stat), float(p)


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


# секунды в секунды, минуты
def calculate_normal_time(sec: int) -> str:
    m, s = sec // 60, sec % 60
    # h, m = m // 60, m % 60
    # d, h = h // 24, h % 24
    return f"Минут: {m}\nСекунд: {s}"


def calculations(data: pd.DataFrame) -> None:
    devices = data["device"].unique()
    channels = data["channel"].unique()

    def calculate_mean_sum(dfr: pd.DataFrame, column: str = "", value: str = ""):
        if column and value:
            payer_mean = round(dfr["sum"][(dfr["payer"] == "yes") | (dfr[column] == value)].agg("mean"), 2)
            all_mean = round(dfr["sum"][dfr[column] == value].agg("mean"), 2)
        else:
            payer_mean = round(dfr["sum"].agg("mean"), 2)
            all_mean = round(dfr["sum"][dfr["payer"] == "yes"].agg("mean"), 2)
        return round(payer_mean, 2), round(all_mean, 2)


    def top_3_mean(dfr: pd.DataFrame, column: str) -> (list, list):
        mean_check_payer_column = list()
        mean_check_all_column = list()
        for item in dfr[column].unique():
            payer_mean, all_mean = calculate_mean_sum(dfr, column, item)
            mean_check_payer_column.append((item, payer_mean))
            mean_check_all_column.append((item, all_mean))

        mean_check_all_column = sorted(mean_check_all_column, key=lambda x: x[1], reverse=True)[:3]
        mean_check_payer_column = sorted(mean_check_payer_column, key=lambda x: x[1], reverse=True)[:3]
        return mean_check_payer_column, mean_check_all_column


    payer_check_mean, all_check_mean = calculate_mean_sum(df)
    print(f"Средний чек с учетом неплатящих: {all_check_mean}")
    print(f"Средний чек без учета неплатящих: {payer_check_mean}")

    print('\u2501' * 50)

    print("Продолжительность сессии по рекламному каналу\n")
    for channel in channels:
        print(f"Рекламной канал: {channel}\n"
              f"Длительность сессии:\n {calculate_normal_time(round(data["sessiondurationsec"][data["channel"] == channel].agg("mean")))}")
        print('\u2500' * 10)

    print('\u2501' * 50)

    print("Продолжительность сессии по девайсу\n")
    for device in devices:
        print(f"Девайс: {device}\n"
              f"Длительность сессии:\n {calculate_normal_time(round(data["sessiondurationsec"][data["device"] == device].agg("mean")))}")
        print('\u2500' * 10)

    print('\u2501' * 50)

    mean_check_payer_devices, mean_check_all_devices = top_3_mean(df, "device")
    print("Топ 3 средний чек с учетом неплатящих по девайсу\n")
    for mean_device in mean_check_all_devices:
        print(f"Девайс: {mean_device[0]}\nсумма чека: {mean_device[1]}")
        print('\u2500' * 10)

    print("Топ 3 средний чек с учетом платящих по девайсу\n")
    for mean_device in mean_check_payer_devices:
        print(f"Девайс: {mean_device[0]}\nсумма чека: {mean_device[1]}")
        print('\u2500' * 10)

    print('\u2501' * 50)

    mean_check_payer_channel, mean_check_all_channel = top_3_mean(df, "channel")
    print("Топ 3 средний чек с учетом неплатящих по каналу рекламы\n")
    for mean_channel in mean_check_all_channel:
        print(f"Рекламный канал: {mean_channel[0]}\nсумма чека: {mean_channel[1]}")
        print('\u2500' * 10)

    print("Топ 3 средний чек с учетом платящих по каналу рекламы\n")
    for mean_channel in mean_check_payer_channel:
        print(f"Рекламный канал: {mean_channel[0]}\nсумма чека: {mean_channel[1]}")
        print('\u2500' * 10)

    print('\u2501' * 50)

    mean_check_payer_region, mean_check_all_region = top_3_mean(df, "region")
    print("Топ 3 средний чек с учетом неплатящих по региону\n")
    for mean_region in mean_check_all_region:
        print(f"Регион: {mean_region[0]}\nсумма чека: {mean_region[1]}")
        print('\u2500' * 10)

    print("Топ 3 средний чек с учетом платящих по региону\n")
    for mean_region in mean_check_payer_region:
        print(f"Регион: {mean_region[0]}\nсумма чека: {mean_region[1]}")
        print('\u2500' * 10)



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

plt.show()
# sns.set()


# Рассчеты
calculations(df)