import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


def to_string_month(month: int) -> str:
    months = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль", "Август", "Сентябрь", "Октябрь",
              "Ноябрь", "Декабрь"]
    return months[month - 1]


def to_string_day(day: int) -> str:
    days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
    return days[day - 1]


class DiagramCreator:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()

    def pie_of_payers_by_column(self, df: pd.DataFrame | None = None, column: str = "") -> None:
        if df is None:
            df = self.df
        df["payer"] = df["payer"].map(lambda x: "купил" if x == "yes" else "не купил")
        groups = df[column].unique()
        fig, axs = plt.subplots(1, len(groups), figsize=(len(groups) * 2.5, 4))
        for i in range(len(axs)):
            val = df[df[column] == groups[i]]["payer"].value_counts()
            axs[i].pie(val, labels=val.index, autopct='%1.0f%%')
            axs[i].set_title(groups[i])
        plt.show()

    def hist_of_column_by_payer(self, df: pd.DataFrame | None = None, column: str = "") -> None:
        if df is None:
            df = self.df
        sea = sns.FacetGrid(df, col="payer", height=4, aspect=1.5)
        sea.map(sns.histplot, column)
        sea.set_xticklabels(rotation=-15)
        axes = sea.axes.flatten()
        axes[0].set_title("Платящие")
        axes[1].set_title("Неплатящие")
        plt.show()

    def hist_of_payers_count_by_column(self, df: pd.DataFrame | None = None, column: str = "", russian_name: str = "")\
            -> None:
        if df is None:
            df = self.df
        sns.histplot(df[df["payer"] == "yes"], x=column)
        plt.xticks(rotation=15)
        plt.suptitle(f"Количество покупок по {russian_name}")
        plt.show()

    def hist_of_payers_by_time(self, df: pd.DataFrame | None = None) -> None:
        if df is None:
            df = self.df

        fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(11, 4))

        months = df[df["payer"] == "yes"]["session_date"].dt.month.value_counts().reset_index()
        months["month"] = months["session_date"].map(to_string_month)
        months = months.sort_values("session_date")[["month", "count"]]
        sns.barplot(months, x="month", y="count", ax=ax1)
        ax1.tick_params(axis='x', rotation=20)
        ax1.set_title("по месяцам")

        days = df[df["payer"] == "yes"]["day"].value_counts().reset_index()
        days["days"] = days["day"].map(to_string_day)
        days = days.sort_values("day")[["days", "count"]]
        sns.barplot(days, x="days", y="count", ax=ax2)
        ax2.set_title("по дням недели")

        time = df[df["payer"] == "yes"]["time_of_day"].value_counts()
        sns.barplot(time, ax=ax3)
        ax3.set_title("по времени суток")
        plt.suptitle("Количество покупок")
        plt.show()
