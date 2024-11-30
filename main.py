import numpy
import pandas as pd
import seaborn as sns
import numpy as np
# import missingno as msno
from modules.preload_data import fill_na, fill_errors
from scipy.stats import shapiro
import matplotlib.pyplot as plt


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


def time_of_day(hour: int, minutes: int) -> str:
    if 360 <= (hour * 60) + minutes <= 599:  # 06:00 - 09:59
        return "Утро"
    elif 600 <= (hour * 60) + minutes <= 1019:  # 10:00 - 16:59
        return "День"
    elif 1020 <= (hour * 60) + minutes <= 1319:  # 17:00 - 21:59
        return "Вечер"
    else:
        return "Ночь"


def new_columns(df: pd.DataFrame) -> pd.DataFrame:
    df['session_date'] = pd.to_datetime(df['session_date'], format='%Y-%m-%d')  # Приведение к правильному формату
    df['session_start'] = pd.to_datetime(df['session_start'], format='%Y-%m-%d %H:%M:%S')  # Приведение к правильному формату
    df['session_end'] = pd.to_datetime(df['session_end'], format='%Y-%m-%d %H:%M:%S')  # Приведение к правильному формату
    df["time_of_day"] = df["session_start"].apply(lambda x: time_of_day(x.hour, x.minute))  # Создание нового столбца и его заполнение
    df["total_cost"] = df.apply(lambda row: row["revenue"] if row["promo_code"] != 1 else row["revenue"] * 0.9, axis=1)
    df["total_cost"] = df["total_cost"].fillna(0)
    return df


df = pd.read_csv("./data/data.csv", encoding="utf-8", sep=",")
df.columns = df.columns.str.lower().str.replace(" ", "_")
df = replace_mistakes(df)
df = new_columns(df)
df = fill_errors(df, "revenue", "median")
df["revenue"] = df["revenue"].fillna(0)
df["bought"] = df["revenue"].map(lambda x: "yes" if x != 0 else "no")
print(df.head())

# fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(11, 4))
# sns.scatterplot(df[df["bought"] == "yes"].dropna(), x="region", y="sessiondurationsec", ax=ax1)
# sns.scatterplot(fill_na(df[df["bought"] == "yes"], "region", "mode"), x="region", y="sessiondurationsec", ax=ax2)
# sns.scatterplot(df.fillna({"region": "other"}), x="region", y="sessiondurationsec", ax=ax3)
#
# plt.show()


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
sns.set()
