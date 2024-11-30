import pandas as pd
import missingno as msno
import matplotlib.pyplot as plt


def unique_column_values(data: pd.DataFrame, columns: list[str]):
    # Варианты
    for column in columns:
        print(f"{column}: {data[column].unique()}")

# print(df.columns)
# unique_column_values(df, ['region', 'device', 'channel', 'payment_type', 'promo_code'])

def initial_data_check(data: pd.DataFrame):
    print(f"Общая информация о дата фрейме {data.info()}")
    print(f"Количество пропусков в процентах{data.isna().sum()}")
    print("Нахождение пропусков в датафрейме")

    msno.matrix(df)
    plt.show()


df = pd.read_csv("../data/data.csv", encoding="utf-8", sep=",")
df.columns = df.columns.str.lower().str.replace(" ", "_")

# print(initial_data_check(df))

# new_df_dub = df[df["user_id"].isin(df["user_id"][df["user_id"].duplicated()])].sort_values("user_id")
# print(new_df_dub[["user_id", "session_date", "revenue"]])
# print(new_df_dub)
# у одинаковых айди с одинаковыми датами совершены покупки на одинаковую сумму, вероятно это скрытые дубликаты
# там, где разные даты - просто разные сессии и такие записи удалять не нужно

# можно заметить, что в повторных сеансах пользователя отсутствуют данные о регионе, девайсе и рекламном канале
# вероятнее всего пользователь совершал повторный сеанс в том же регионе и с того же девайса.
