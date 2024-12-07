import pandas as pd


# секунды в секунды, минуты
def calculate_normal_time(sec: int) -> str:
    m, s = sec // 60, sec % 60
    # h, m = m // 60, m % 60
    # d, h = h // 24, h % 24
    return f"Минут: {m}\nСекунд: {s}"


class Calculator:
    def __init__(self, data: pd.DataFrame):
        self.df = data

    def calculate_mean_sum(self, df: pd.DataFrame | None = None, column: str = "", value: str = "") -> (float, float):
        if df is None:
            df = self.df
        if column and value:
            payer_mean = round(df["sum"][(df["payer"] == "yes") | (df[column] == value)].agg("mean"), 2)
            all_mean = round(df["sum"][df[column] == value].agg("mean"), 2)
        else:
            payer_mean = round(df["sum"].agg("mean"), 2)
            all_mean = round(df["sum"][df["payer"] == "yes"].agg("mean"), 2)
        return round(payer_mean, 2), round(all_mean, 2)

    def top_3_mean(self, df: pd.DataFrame | None = None, column: str = "") -> (list, list):
        if df is None:
            df = self.df
        mean_check_payer_column = list()
        mean_check_all_column = list()
        for item in df[column].unique():
            payer_mean, all_mean = self.calculate_mean_sum(df, column, item)
            mean_check_payer_column.append((item, payer_mean))
            mean_check_all_column.append((item, all_mean))

        mean_check_all_column = sorted(mean_check_all_column, key=lambda x: x[1], reverse=True)[:3]
        mean_check_payer_column = sorted(mean_check_payer_column, key=lambda x: x[1], reverse=True)[:3]
        return mean_check_payer_column, mean_check_all_column

    def calculate_mau_by_column(self, df: pd.DataFrame | None = None, column: str | None = None) -> pd.Series:
        if df is None:
            df = self.df
        if column is None:
            return df.groupby(df["session_date"].dt.month)["user_id"].nunique()
        return df.groupby([df["session_date"].dt.month, column])["user_id"].nunique()

    def print_mean_sum_with_and_without_payers(self, df: pd.DataFrame | None = None, print_line: bool = True) -> None:
        if df is None:
            payer_check_mean, all_check_mean = self.calculate_mean_sum()
        else:
            payer_check_mean, all_check_mean = self.calculate_mean_sum(df)
        print(f"Средний чек с учетом неплатящих: {all_check_mean}")
        print(f"Средний чек без учета неплатящих: {payer_check_mean}")
        if print_line:
            print('\u2501' * 50, "\n")

    def print_session_duration_by_column(self, df: pd.DataFrame | None = None, column: str = "", russian_name: str = "",
                                         print_line: bool = True) -> None:
        if df is None:
            df = self.df
        print(f"Продолжительность сессии по {russian_name}\n")
        uniq = df[column].unique()
        for channel in uniq:
            print(f"{russian_name}: {channel}\n"
                  f"Длительность сессии:\n"
                  f" {calculate_normal_time(round(df["sessiondurationsec"][df[column] == channel].agg("mean")))}")
            print('\u2500' * 10)
        if print_line:
            print('\u2501' * 50, "\n")

    def print_top3_sum_by_column(self, df: pd.DataFrame | None = None, column: str = "", payer: bool | None = None,
                                 russian_name: str = "", print_line: bool = True) -> None:
        """
        payer is None -> вывести с учетом платящих и неплатящих
        payer is False -> вывести только с учетом неплатящих
        payer is True -> вывести только с учетом плятящих"""
        if df is None:
            mean_check_payer, mean_check_all = self.top_3_mean(column=column)
        else:
            mean_check_payer, mean_check_all = self.top_3_mean(df=df, column=column)

        if payer is None or payer is False:
            print(f"Топ 3 средний чек с учетом неплатящих по {russian_name}\n")
            for mean in mean_check_all:
                print(f"{russian_name}: {mean[0]}\nсумма чека: {mean[1]}")
                print('\u2500' * 10)
        if payer is None or payer is True:
            print(f"Топ 3 средний чек с учетом платящих по {russian_name}\n")
            for mean in mean_check_payer:
                print(f"{russian_name}: {mean[0]}\nсумма чека: {mean[1]}")
                print('\u2500' * 10)
        if print_line:
            print('\u2501' * 50, "\n")

    def print_mean_purchase_count_by_1_customer(self, df: pd.DataFrame | None = None, print_line: bool = True) -> None:
        if df is None:
            df = self.df
        payers = df[df["payer"] == "yes"]["user_id"].value_counts()
        print(f"Пользователь в среднем совершает {payers.mean()} покупок с учетом только платящих пользователей")
        print(f"Пользователь в среднем совершает {payers.sum() / len(df["user_id"].unique())} "
              f"покупок с учетом всех пользователей")
        if print_line:
            print('\u2501' * 50, "\n")

    def print_top3_mau_column(self, df: pd.DataFrame | None = None, column: str | None = None) -> None:
        print(self.calculate_mau_by_column(df=df, column=column))
        # Я хз, как считать топ-3 и что за него брать


"""def calculations(data: pd.DataFrame) -> None:
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

    payer_check_mean, all_check_mean = calculate_mean_sum(data)
    print(f"Средний чек с учетом неплатящих: {all_check_mean}")
    print(f"Средний чек без учета неплатящих: {payer_check_mean}")

    print('\u2501' * 50)

    print("Продолжительность сессии по рекламному каналу\n")
    for channel in channels:
        print(f"Рекламной канал: {channel}\n"
              f"Длительность сессии:\n"
              f" {calculate_normal_time(round(data["sessiondurationsec"][data["channel"] == channel].agg("mean")))}")
        print('\u2500' * 10)

    print('\u2501' * 50)

    print("Продолжительность сессии по девайсу\n")
    for device in devices:
        print(f"Девайс: {device}\n"
              f"Длительность сессии:\n"
              f" {calculate_normal_time(round(data["sessiondurationsec"][data["device"] == device].agg("mean")))}")
        print('\u2500' * 10)

    print('\u2501' * 50)

    mean_check_payer_devices, mean_check_all_devices = top_3_mean(data, "device")
    print("Топ 3 средний чек с учетом неплатящих по девайсу\n")
    for mean_device in mean_check_all_devices:
        print(f"Девайс: {mean_device[0]}\nсумма чека: {mean_device[1]}")
        print('\u2500' * 10)

    print("Топ 3 средний чек с учетом платящих по девайсу\n")
    for mean_device in mean_check_payer_devices:
        print(f"Девайс: {mean_device[0]}\nсумма чека: {mean_device[1]}")
        print('\u2500' * 10)

    print('\u2501' * 50)

    mean_check_payer_channel, mean_check_all_channel = top_3_mean(data, "channel")
    print("Топ 3 средний чек с учетом неплатящих по каналу рекламы\n")
    for mean_channel in mean_check_all_channel:
        print(f"Рекламный канал: {mean_channel[0]}\nсумма чека: {mean_channel[1]}")
        print('\u2500' * 10)

    print("Топ 3 средний чек с учетом платящих по каналу рекламы\n")
    for mean_channel in mean_check_payer_channel:
        print(f"Рекламный канал: {mean_channel[0]}\nсумма чека: {mean_channel[1]}")
        print('\u2500' * 10)

    print('\u2501' * 50)

    mean_check_payer_region, mean_check_all_region = top_3_mean(data, "region")
    print("Топ 3 средний чек с учетом неплатящих по региону\n")
    for mean_region in mean_check_all_region:
        print(f"Регион: {mean_region[0]}\nсумма чека: {mean_region[1]}")
        print('\u2500' * 10)

    print("Топ 3 средний чек с учетом платящих по региону\n")
    for mean_region in mean_check_payer_region:
        print(f"Регион: {mean_region[0]}\nсумма чека: {mean_region[1]}")
        print('\u2500' * 10)

    print('\u2501' * 50)

    # не доделал
    print("Топ 3 месяца по регионам")
    months_payer = []
    months_all = []
    for month in data["month"].unique():
        mean_payer = data["sum"][(data["payer"] == "yes") | (data["month"] == month)].agg("mean")
        months_payer.append((month, mean_payer))

        mean_all = data["sum"][data["month"] == month].agg("mean")
        months_all.append((month, mean_all))
    months_payer = sorted(months_payer, key=lambda x: x[1])[:3]
    months_all = sorted(months_all, key=lambda x: x[1])[:3]
    for month in months_all:
        new_df = data[(data["payer"] == "yes") | (data["month"] == month)]
        mean_check_payer_region, mean_check_all_region = top_3_mean(new_df, "region")
        print(f"Топ 3 средний чек с учетом неплатящих по региону в месяце {month}\n")
        for mean_region in mean_check_all_region:
            print(f"Регион: {mean_region[0]}\nсумма чека: {mean_region[1]}")
            print('\u2500' * 10)

        print(f"Топ 3 средний чек с учетом платящих по региону в месяце {month}\n")
        for mean_region in mean_check_payer_region:
            print(f"Регион: {mean_region[0]}\nсумма чека: {mean_region[1]}")
            print('\u2500' * 10)
        # print(f"Топ 3 региона в месяце {top_3_mean(new_df, "region")}")"""