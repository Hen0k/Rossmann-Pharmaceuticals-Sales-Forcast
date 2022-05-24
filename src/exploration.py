import pandas as pd
import numpy as np
from src.cleaning import CleanDataFrame


class Analysis:
    @staticmethod
    def get_univariate_analysis(df: pd.DataFrame) -> pd.DataFrame:
        numerical_columns = CleanDataFrame.get_numerical_columns(df)
        numericals = df[numerical_columns]
        descriptions = numericals.describe().transpose()

        modes = {}
        for col in numericals.columns:
            modes[col] = numericals[col].mode()[0]
        descriptions['mode'] = modes.values()

        descriptions['CoV'] = descriptions['std'].values / \
            descriptions['mean'].values
        descriptions['skew'] = numericals.skew()
        descriptions['kurtosis'] = numericals.kurtosis().values
        Q1 = numericals.quantile(0.25)
        Q3 = numericals.quantile(0.75)
        IQR = Q3 - Q1
        descriptions['iqr'] = IQR
        descriptions['missing_counts'] = numericals.isna().sum()

        return descriptions

    @staticmethod
    def get_top_ten(df: pd.DataFrame, column: str, drop_index: bool = True) -> pd.DataFrame:
        df.sort_values(column, ascending=False, inplace=True)
        if drop_index:
            df.reset_index(drop=True, inplace=True)

        return df.head(10)

    @staticmethod
    def get_missing_entries_count(df: pd.DataFrame) -> list[pd.Series, list]:
        cols_missing_val_count = df.isnull().sum()
        cols_missing_val_count = cols_missing_val_count[cols_missing_val_count != 0]
        cols_missing_val = cols_missing_val_count.index.values
        cols_missing_val_count

        return cols_missing_val_count, cols_missing_val
    
    @staticmethod
    def percent_missing(df):
        """
        Print out the percentage of missing entries in a dataframe
        """
        # Calculate total number of cells in dataframe
        totalCells = np.product(df.shape)

        # Count number of missing values per column
        missingCount = df.isnull().sum()

        # Calculate total number of missing values
        totalMissing = missingCount.sum()

        # Calculate percentage of missing values
        print("The dataset contains", round(
            ((totalMissing/totalCells) * 100), 2), "%", "missing values.")

