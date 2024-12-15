import numpy
import pandas as pd
import seaborn as sns
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.preprocessing import OneHotEncoder
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error, mean_absolute_percentage_error
# import missingno as msno
from modules.preload_data import fill_na, fill_errors
from modules.calculations import calculate_normal_time, Calculator
from modules.diagrams import DiagramCreator
from modules.hypotheses import kruskal_test_region, check_avg_revenue_hypotheses
from scipy.stats import shapiro, kruskal
from modules.hypotheses import kruskal_test_region, numeric_and_numeric_hypo
from modules.hypotheses import duration_of_the_purchase
from modules.hypotheses import duration_depends_on_the_payment_type
from modules.hypotheses import duration_depends_on_the_pay_or_no
from modules.criterions import MetricModel
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
    data["region"] = data["region"].replace("UК", "UK")  # it's NOT the same

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
    data = fill_errors(data, "sessiondurationsec", "median", fill_only="up")
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
    """
    Заполняет пропуски в данных, когда у пользователя есть две записи,
    потому что в одной из них точно будут пропущены колнки region, device и channel
    """
    user_ids = data["user_id"].unique()
    for user_id in user_ids:
        if len(data[data["user_id"] == user_id]) == 1:
            continue
        rows = data["user_id"].map(lambda x: x == user_id)
        data = fill_missing_with_dup(data, rows, "region")
        data = fill_missing_with_dup(data, rows, "device")
        data = fill_missing_with_dup(data, rows, "channel")
    return data


def fit_transform(train: pd.DataFrame, test: pd.DataFrame, _ohe: OneHotEncoder, column: str = "") -> \
        (pd.DataFrame, pd.DataFrame):
    """
    Кодирует нужные категориальные колонки с помощью OneHotEncoder

    :param train: train selection
    :param test: test selection
    :param _ohe: instance of OneHotEncoder class
    :param column: column for encoding
    :return: tuple of two dataframes with train and test selection which column was encoded
    """

    train_new = pd.DataFrame(_ohe.fit_transform(train[[column]]),
                             columns=_ohe.categories_, index=train.index)  # получаем закодированную версию колонки
    train_other_cols = train.drop(columns=column)  # получаем остальные колнки
    train = pd.concat([train_new, train_other_cols], axis=1)  # соединение новых значений и старых

    # аналогично
    test_new = pd.DataFrame(_ohe.fit_transform(test[[column]]), columns=_ohe.categories_, index=test.index)
    test_other_cols = test.drop(columns=column)
    test = pd.concat([test_new, test_other_cols], axis=1)
    train.columns = list(map(lambda x: x[0] if isinstance(x, tuple) else x, train.columns))
    test.columns = list(map(lambda x: x[0] if isinstance(x, tuple) else x, test.columns))
    # _x_train[column] = _ohe.fit_transform(_x_train[[column]])
    # _x_test[column] = _ohe.fit_transform(_x_test[[column]])
    return train, test


def print_metrics_model(fact: pd.DataFrame, predict: np.ndarray) -> None:
    print(f"R2 = {round(r2_score(fact, predict), 4)}")
    print(f"MAPE = {round(mean_absolute_percentage_error(fact, predict) * 100, -18)}")
    print(f"MAE = {round(mean_absolute_error(fact, predict))}")
    print(f"RMSE = {round(mean_squared_error(fact, predict) ** 0.5)}")


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
# из социальных сетей будет выше, чем у пользователей, пришедших от рекламы блогеров

# check_avg_revenue_hypotheses(df, "Cредний чек одинаков в зависимости от региона",
#                              "Cредний чек отличается в зависимости от региона",
#                              'region')
# check_avg_revenue_hypotheses(df, "Cредний чек одинаков в зависимости от рекламного канала",
#                              "Cредний чек отличается в зависимости от рекламного канала",
#                              'channel')
# check_avg_revenue_hypotheses(df, "Cредний чек одинаков в зависимости от времени суток",
#                              "Cредний чек отличается в зависимости от времени суток",
#                              'time_of_day')
# duration_depends_on_the_payment_type(df, "Длительность сессии одинакова у пользователей с разными типами оплаты",
#                                      "Длительность сессии различается у пользователей с разными типами оплаты",
#                                      "payment_type")
# duration_depends_on_the_pay_or_no(df, "Длительность сессии одинакова у платящих и не платящих пользователей",
#                                   "Длительность сессии различается у платящих и не платящих пользователей",
#                                   "payer")
# print(df.T)
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
# diagrams.hist_of_payers_count_by_column(column="payment_type", russian_name="типу оплаты")
# diagrams.hist_of_payers_by_time()

# plt.show()


# h0 = "Средняя продолжительность сессии одинакова у платящих и неплатящих пользователей"
# h1 = "Средняя продолжительность сессии не совпадает у платящих и неплатящих пользователей"
# numeric_and_numeric_hypo(df["sessiondurationsec"], df["sum"], h0, h1)
# print("коэффициент корреляции ниже 0.3, так что по шкале Чеддока можно сказать, что корреляция отсутствует")
# print("т.к. p-value больше 0.05, альтернативную гипотезу принимать нельзя")


# selling_columns_cat = ["region", "channel"]
# selling_columns_num = []
# x_train, x_test, y_train, y_test = train_test_split(df[selling_columns_cat + selling_columns_num],
#                                                     df["sum"], test_size=0.15, random_state=0)
# x_train_orig = x_train.copy()
# x_test_orig = x_test.copy()
# # print(x_train.drop(columns="region").tail())
#
# ohe = OneHotEncoder(sparse_output=False, handle_unknown="ignore")  # drop="first"
# for i in selling_columns_cat:
#     x_train, x_test = fit_transform(x_train, x_test, ohe, i)
#
# # y_train = ohe.fit_transform(y_train.to_frame())
# # y_test = ohe.fit_transform(y_test.to_frame())
#
# lin_reg = LinearRegression()
# lin_reg.fit(x_train, y_train)
# prediction = lin_reg.predict(x_test)
#
# print(f"Были выбраны шкалы {", ".join(selling_columns_cat)}, {", ".join(selling_columns_num)}, "
#       f"потому что они должны влиять на суммы продаж\n")

# print("Метрики модели")
# print_metrics_model(y_test, prediction)
# print("\u2500" * 10)

# prediction = pd.concat([x_test_orig.reset_index(drop=True), pd.DataFrame(prediction)], axis=1)
# prediction[0] = prediction[0].astype(int)

# print("Первые 5 значений предсказания для тестовой выборки:")
# print(prediction.head().rename({0: "revenue"}, axis=1))
# print("\u2500" * 10)

# print("Максимальные значения дохода для групп в предсказании:")
# print(prediction.groupby(selling_columns_cat + selling_columns_num).agg("max")
#       .sort_values(0).rename({0: "max_revenue"}, axis=1))
# print("\u2500" * 10)

# for i in selling_columns_cat + selling_columns_num:
#     sns.scatterplot(x=x_train_orig[i], y=y_train)
#     plt.xticks(rotation=-15)
#     plt.suptitle("Распределение сумм покупок по фактору")
#     plt.show()
#
# for i in selling_columns_cat:
#     sns.barplot(x=x_train_orig[i], y=y_train)
#     plt.xticks(rotation=-15)
#     plt.suptitle("Суммы покупок по фактору")
#     plt.show()
# for i in selling_columns_num:
#     sns.histplot(x=x_train_orig[i], y=y_train)
#     plt.xticks(rotation=-15)
#     plt.show()


# print()
# print(df.groupby(["region", "channel"])["sum"].agg("mean").sort_values())
# print()
# print(pd.concat([x_test_orig.reset_index(drop=True),
#                  y_test.reset_index()], axis=1).groupby(["region", "channel"])["sum"].agg("max").sort_values())
# print()
# print(pd.concat([x_train_orig.reset_index(drop=True),
#                  y_train.reset_index()], axis=1).groupby(["region", "channel"])["sum"].agg("max").sort_values())

# print(prediction[prediction["channel"] == "социальные сети"][0].value_counts())
# max_of_predict = prediction.max().to_frame().T[0].values[0]
# print(prediction[prediction[0] == max_of_predict])
# print(prediction[prediction[0] == 1704])
# print_metrics_model(y_train, lin_reg.predict(x_train))
# print_metrics_model(y_test, prediction)
# print("\u2501" * 50)

# print("Log reg")
# log_reg = LogisticRegression(solver="liblinear", random_state=0)
# log_reg.fit(x_train, y_train)
# log_prediction = log_reg.predict(x_test)
# print(log_prediction)
# print_metrics_model(y_train, lin_reg.predict(y_train))
# print_metrics_model(y_test, log_prediction)

