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


df = pd.read_csv("./data/data.csv", encoding="utf-8", sep=",")
df.columns = df.columns.str.lower().str.replace(" ", "_")
df = replace_mistakes(df)
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
