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


def replace_mistakes(df: pd.DataFrame) -> pd.DataFrame:
    df["region"] = df["region"].replace("Unjted States", "United States")
    df["region"] = df["region"].replace("Frаnce", "France")  # it's NOT the same
    df["region"] = df["region"].replace("Frаncе", "France")  # it's NOT the same
    df["region"] = df["region"].replace("Franсe", "France")  # it's NOT the same

    df["region"] = df["region"].replace("germany", "Germany")
    df["region"] = df["region"].replace("UK", "UК")  # it's NOT the same

    df["channel"] = df["channel"].replace("контексная реклама", "контекстная реклама")
    df["device"] = df["device"].replace("Android", "android")  # idk what name we will use? but i like this
    # maybe there are other mistakes in columns
    # maybe we can use list with for
    # we have 0.86271506 value in promo_code? but it needs to be 0 or 1
    df["promo_code"] = df["promo_code"].replace(0.86271506, 1)

    # print(df["promo_code"].unique())
    return df


def time_of_day(hours: int) -> str:
    if 360 <= (hours * 60) <= 599:  # 06:00 - 09:59
        return "Утро"
    elif 600 <= (hours * 60) <= 1019:  # 10:00 - 16:59
        return "День"
    elif 1020 <= (hours * 60) <= 1319:  # 17:00 - 21:59
        return "Вечер"
    else:
        return "Ночь"


def to_time_columns(df: pd.DataFrame) -> pd.DataFrame:
    df['session_date'] = pd.to_datetime(df['session_date'], format='%Y-%m-%d')  # Приведение к правильному формату
    df['session_start'] = pd.to_datetime(df['session_start'], format='%Y-%m-%d %H:%M:%S')
    df['session_end'] = pd.to_datetime(df['session_end'], format='%Y-%m-%d %H:%M:%S')
    df["time_of_day"] = df["hour_of_day"].apply(time_of_day)
    return df


def fill_all_errors(df: pd.DataFrame) -> pd.DataFrame:
    df = fill_errors(df, "sessiondurationsec", "median")
    df = fill_errors(df, "revenue", "median")
    return df


def plot_corr_with_nans(df: pd.DataFrame, x: str, y: str, payer: str | None = "yes") -> None:
    if payer:
        df = df[df["payer"] == payer]
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(14, 4))
    sns.boxplot(df.dropna(), x=x, y=y, ax=ax1)
    sns.boxplot(fill_na(df.copy(), x, "mode"), x=x, y=y, ax=ax2)
    sns.boxplot(df.fillna({x: "other"}), x=x, y=y, ax=ax3)


def kruskal_test(df: pd.DataFrame, x: str, y: str) -> tuple:
    uniq = df[x].unique()
    stat, p = kruskal(*[df[df[x] == uniq[i]][y] for i in range(len(uniq))])
    return float(stat), float(p)


def fill_missing_with_dup(df: pd.DataFrame, rows: pd.Series, column: str) -> pd.DataFrame:
        df.loc[rows, column] = df.loc[rows, column].fillna(method="ffill").fillna(method="bfill")
        return df


def fill_missing_data_categorical(df: pd.DataFrame) -> pd.DataFrame:
    user_ids = df["user_id"].unique()
    for user_id in user_ids:
        rows = df["user_id"].map(lambda x: x == user_id)
        if len(df[df["user_id"] == user_id]) == 1:
            continue
        df = fill_missing_with_dup(df, rows, "region")
        df = fill_missing_with_dup(df, rows, "device")
        df = fill_missing_with_dup(df, rows, "channel")
    return df


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
print(new_df_dub)  # [["user_id", "session_date", "revenue"]])

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


# сolumns = df.columns
# for col in сolumns:
#     try:
#         print(col, check_normal(df[col], alp=0.05))
#     except:
#         ...
# data not normal(( -> fill


# mode, because the data is categorical
# df["region"] = fill_na(df, "region", "mode")

plt.show()
# sns.set()
