import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


class DiagramCreator:
    def __init__(self, df: pd.DataFrame):
        self.df = df

    def pie_of_payers_by_column(self, df: pd.DataFrame | None = None, column: str = "") -> None:
        if df is None:
            df = self.df
        groups = df[column].unique()
        fig, axs = plt.subplots(1, len(groups), figsize=(len(groups) * 2.5, 4))
        for i in range(len(axs)):
            val = df[df[column] == groups[i]]["payer"]
            axs[i].pie(val.value_counts(), labels=val.unique(), autopct='%1.0f%%')
            axs[i].set_title(groups[i])
        plt.show()
