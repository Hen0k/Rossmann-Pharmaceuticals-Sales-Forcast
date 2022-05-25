from calendar import c
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler, StandardScaler, Normalizer
from src.rotating_logs import get_rotating_log


logger = get_rotating_log(filename='data_cleaner.log', logger_name='CleanDataFrameLogger')

class CleanDataFrame:

    @staticmethod
    def get_numerical_columns(df: pd.DataFrame) -> list:
        numerical_columns = df.select_dtypes(include='number').columns.tolist()
        return numerical_columns

    @staticmethod
    def get_categorical_columns(df: pd.DataFrame) -> list:
        categorical_columns = df.select_dtypes(
            include=['object']).columns.tolist()
        return categorical_columns


    @staticmethod
    def get_mct(series: pd.Series, measure: str):
        """
        get mean, median or mode depending on measure
        """
        measure = measure.lower()
        if measure == "mean":
            return series.mean()
        elif measure == "median":
            return series.median()
        elif measure == "mode":
            return series.mode()[0]
        elif measure == 'zero':
            return 0

    @staticmethod
    def replace_missing(df: pd.DataFrame, columns: str, method: str=None, replace_with: any=None) -> pd.DataFrame:

        for column in columns:
            nulls = df[column].isnull()
            indecies = [i for i, v in zip(nulls.index, nulls.values) if v]
            if not replace_with:
                replace_with = CleanDataFrame.get_mct(df[column], method)
            df.loc[indecies, column] = replace_with
            logger.info(f"Replacing missing values in column: {column} with method: {method}")

        return df


    @staticmethod
    def normal_scale(self, df: pd.DataFrame) -> pd.DataFrame:
        scaller = StandardScaler()
        scalled = pd.DataFrame(scaller.fit_transform(
            df[self.get_numerical_columns(df)]))
        scalled.columns = self.get_numerical_columns(df)

        return scalled

    @staticmethod
    def minmax_scale(df: pd.DataFrame) -> pd.DataFrame:
        scaller = MinMaxScaler()
        scalled = pd.DataFrame(
            scaller.fit_transform(
                df[self.get_numerical_columns(df)]),
            columns=self.get_numerical_columns(df)
        )

        return scalled

    @staticmethod
    def normalize(df: pd.DataFrame) -> pd.DataFrame:
        normalizer = Normalizer()
        normalized = pd.DataFrame(
            normalizer.fit_transform(
                df[self.get_numerical_columns(df)]),
            columns=self.get_numerical_columns(df)
        )

        return normalized

    @staticmethod
    def drop_duplicates(df: pd.DataFrame) -> pd.DataFrame:
        """
        This checkes if there are any duplicated entries for a user
        And remove the duplicated rows
        """
        df = df.drop_duplicates(subset='auction_id')

        return df

    @staticmethod
    def date_to_day(df: pd.DataFrame) -> pd.DataFrame:
        """
        This converts the date column into the day of the week
        """
        df['day_of_week'] = pd.to_datetime(df['date']).dt.day_name().values

        return df

    @staticmethod
    def drop_columns(df: pd.DataFrame, columns: list = None) -> pd.DataFrame:
        """
        Drops columns that are not essesntial for modeling
        """
        if not columns:
            columns = ['auction_id', 'date', 'yes', 'no', 'device_make']
        df.drop(columns=columns, inplace=True)

        return df
    
    @staticmethod
    def convert_type(df: pd.DataFrame, columns: list, to_type: type) -> pd.DataFrame:
        """Converts columns data types according to the `to_type` parameter
        """
        df[columns] = df[columns].astype(to_type)

        return df


    def run_pipeline(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        This runs a series of cleaner methods on the df passed to it. 
        """
        df = self.drop_duplicates(df)
        df = self.date_to_day(df)
        df = self.drop_columns(df)
        df.reset_index(drop=True, inplace=True)

        return df
