import pandas as pd
import numpy as np
from sklearn.metrics import r2_score, mean_absolute_percentage_error, mean_absolute_error, mean_squared_error
from scipy.stats import mannwhitneyu, shapiro, ttest_ind, chi2_contingency, pearsonr, spearmanr


class MetricModel:
    def __init__(self, fact, prediction):
        self.fact = fact
        self.prediction = prediction

    def r2(self, n: int = 2):
        return np.round(r2_score(self.fact, self.prediction), n)

    def mape(self, n: int = 2):
        return np.round(mean_absolute_percentage_error(self.fact, self.prediction) * 100, n)

    def mae(self, n: int = 2):
        return np.round(mean_absolute_error(self.fact, self.prediction), n)

    def mse(self, n: int = 2):
        return np.round(mean_squared_error(self.fact, self.prediction), n)

    def pmse(self, n: int = 2):
        return np.round(mean_squared_error(self.fact, self.prediction) ** 0.5, n)


def count_mannwhitneyu_p(br: pd.DataFrame, gd: pd.DataFrame, rnd: int = -1) -> float:
    if rnd >= 0:
        return float(round(mannwhitneyu(br, gd, alternative="two-sided").pvalue, rnd))
    return float(mannwhitneyu(br, gd, alternative="two-sided").pvalue)


def check_normal(values: pd.Series, alp: float) -> bool:
    return shapiro(values).pvalue > alp


def count_sthudent(br: pd.DataFrame, gd: pd.DataFrame, rnd: int = -1) -> float:
    if rnd >= 0:
        return float(round(ttest_ind(br, gd, alternative="two-sided").pvalue, rnd))
    return float(ttest_ind(br, gd, alternative="two-sided").pvalue)


def count_chi2_p(br: pd.DataFrame, gd: pd.DataFrame, rnd: int = -1) -> float:
    crosstab = pd.crosstab(br, gd)
    if rnd >= 0:
        return float(round(chi2_contingency(crosstab).pvalue, rnd))
    return float(chi2_contingency(crosstab).pvalue)


def count_pearson_p(br: pd.DataFrame, gd: pd.DataFrame, rnd: int = -1) -> float:
    if rnd >= 0:
        return float(round(pearsonr(br, gd).pvalue, rnd))
    return float(pearsonr(br, gd).pvalue)


def count_spearman(br: pd.Series, gd: pd.Series, rnd: int = -1) -> str:
    spear = spearmanr(br, gd)
    if rnd >= 0:
        return f"statistics: {float(round(spear.statistic, rnd))}\npvalue: {float(round(spear.pvalue, rnd))}"
    return f"statistics: {float(spear.statistic)}\npvalue: {float(spear.pvalue)}"


def all_var(df: pd.DataFrame, group: str, value: str):
    mean = df[value].mean()
    mean_group = df.groupby(group)[value].mean()
    size_group = df.groupby(group)[value].size()
    return sum(size_group * (mean_group - mean) ** 2)


def group_var(df: pd.DataFrame, group: str, value: str):
    mean_group = df.groupby(group)[value].mean()
    df["var"] = (df[value] - df[group].map(mean_group)) ** 2
    return df["var"].sum()


def calc_eta(df: pd.DataFrame, group: str, value: str):
    group_disp = group_var(df, group, value)
    all_disp = all_var(df, group, value)
    print(f"group: {group_disp}\nall_disp: {all_disp}")
    return round((all_disp / (group_disp + all_disp)) ** 0.5, 4)


def cramers_stat(df: pd.DataFrame, groups: tuple[str, str], round_zn=0):
    matrix = pd.crosstab(df[groups[0]], df[groups[1]]).to_numpy()
    n = matrix.sum()
    chi2 = chi2_contingency(matrix).statistic
    return round((chi2 / (n * (min(matrix.shape) - 1))) ** 0.5, round_zn)