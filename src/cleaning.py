import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler, StandardScaler, Normalizer


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
    def fix_datatypes(df: pd.DataFrame, column: str = None, to_type: type = None) -> pd.DataFrame:
        """
        Takes in the tellco dataframe an casts columns to proper data types.
        Start and End -> from string to datetime.
        Bearer Id, IMSI, MSISDN, IMEI -> From number to string
        """
        datetime_columns = ['Start',
                            'End', ]
        string_columns = [
            'IMSI',
            'MSISDN/Number',
            'IMEI',
            'Bearer Id'
        ]
        df_columns = df.columns
        for col in string_columns:
            if col in df_columns:
                df[col] = df[col].astype(str)
        for col in datetime_columns:
            if col in df_columns:
                df[col] = pd.to_datetime(df[col])
        if column and to_type:
            df[column] = df[column].astype(to_type)

        return df


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

        return df

    @staticmethod
    def remove_null_row(df: pd.DataFrame, columns: str) -> pd.DataFrame:
        for column in columns:
            df = df[~ df[column].isna()]

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
    def drop_unresponsive(df: pd.DataFrame) -> pd.DataFrame:
        """
        This drops rows where users didn't repond to the questioneer.
        Meaning, rows where both yes and no columns have 0
        """
        df = df.query("yes==1 | no==1")

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
    def merge_response_columns(df: pd.DataFrame) -> pd.DataFrame:
        """
        This merges the one-hot-encoded target columns into
        a single column named response, and drop the yes and no columns
        """
        df['response'] = [1] * df.shape[0]
        df.loc[df['no'] == 1, 'response'] = 0

        return df

    @staticmethod
    def convert_to_brands(df: pd.DataFrame) -> pd.DataFrame:
        """
        This converts the device model column in to 
        `known` and `generic` brands. It then removes
        the device_make column.
        """
        known_brands = ['samsung', 'htc', 'nokia',
                        'moto', 'lg', 'oneplus',
                        'iphone', 'xiaomi', 'huawei',
                        'pixel']
        makers = ["generic"]*df.shape[0]
        for idx, make in enumerate(df['device_make'].values):
            for brand in known_brands:
                if brand in make.lower():
                    makers[idx] = "known brand"
                    break
        df['brand'] = makers

        return df

    def run_pipeline(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        This runs a series of cleaner methods on the df passed to it. 
        """
        df = self.drop_duplicates(df)
        df = self.drop_unresponsive(df)
        df = self.date_to_day(df)
        df = self.convert_to_brands(df)
        df = self.merge_response_columns(df)
        df = self.drop_columns(df)
        df.reset_index(drop=True, inplace=True)

        return df
