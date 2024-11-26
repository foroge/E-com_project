import pandas as pd
import seaborn as sns
import numpy as np
# import missingno as msno
from modules.preload_data import fill_na
from scipy.stats import shapiro


def check_normal(values: pd.Series, alp: float) -> bool:
    return shapiro(values).pvalue > alp


df = pd.read_csv("./data/data.csv", encoding="utf-8", sep=",")
df.columns = df.columns.str.lower().str.replace(" ", "_")

# print((df.isna().sum() / len(df)).round(4) * 100)

columns = df.columns[-4:]
# print(df[columns].isna().corr())
# the user did not make a purchase
for col in columns:
    df[col].fillna("не совершал", inplace=True)


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
