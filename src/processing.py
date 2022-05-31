from types import NoneType
import pandas as pd
from src.rotating_logs import get_rotating_log


#logger = get_rotating_log(filename='preprocessing.log', logger_name='FeatureEngineeringLogger')


class FeatureEngineering:
    def __init__(self, df=None):
        self.df = df
        self.holidays = None
        # self.columns_to_keep = [
        #     'Assortment',
        #     'CompetitionDistance',
        #     'CompetitionOpenSinceMonth',
        #     'CompetitionOpenSinceYear',
        #     'Date',
        #     'DayOfWeek',
        #     'Open',
        #     'Promo',
        #     'Promo2',
        #     'Promo2SinceWeek',
        #     'Promo2SinceYear',
        #     'PromoInterval',
        #     'SchoolHoliday',
        #     'StateHoliday',
        #     'Store',
        #     'StoreType',
        #     'Sales',
        #     'Customers',
        # ]

    def transform(self, df: pd.DataFrame = None):
        if isinstance(df, pd.DataFrame):
            self.df = df.copy()
        assert 'Date' in self.df.columns
        self._set_holidays()
        # self.drop_columns()
        self.generate_columns()
        #logger.info("Feature enginerring completed")

        return self.df

    # def drop_columns(self) -> None:
    #     self.df = self.df[self.columns_to_keep]
    #     #logger.info(
    #         f"Dropped {len(self.columns_to_keep)} columns since they are not in the test data")

    def generate_columns(self) -> None:
        """Adds date related categorical columns to the dataframe"""

        self.create_holiday_distance_cols()
        self.df.loc[:, ['Year']] = self.df['Date'].dt.year
        self.df.loc[:, ['Month']] = self.df['Date'].dt.month
        self.df.loc[:, ['WeekOfYear']] = self.df['Date'].dt.isocalendar().week
        self.df.loc[:, ['is_month_end']] = self.df['Date'].dt.is_month_end
        self.df.loc[:, ['is_month_start']] = self.df['Date'].dt.is_month_start
        self.df.loc[:, ['is_quarter_end']] = self.df['Date'].dt.is_quarter_end
        self.df.loc[:, ['is_quarter_start']] = self.df['Date'].dt.is_quarter_start
        self.df.loc[:, ['is_year_end']] = self.df['Date'].dt.is_year_end
        self.df.loc[:, ['is_year_start']] = self.df['Date'].dt.is_year_start
        #logger.info("9 new columns added to the dataframe")

    def create_holiday_distance_cols(self) -> None:
        self.df.loc[:, ['DistanceToNextHoliday']] = pd.NA
        self.df.loc[:, ['DistanceFromPrevHoliday']] = pd.NA
        unique_dates = self.df.Date.unique()
        for date in unique_dates:
            after_holiday, to_next_holiday = self._get_holiday_distances(date)
            indecies = self.df[self.df['Date'] == date].index
            self.df.loc[indecies, 'DistanceToNextHoliday'] = to_next_holiday
            self.df.loc[indecies, 'DistanceFromPrevHoliday'] = after_holiday
        self.df.loc[:, ['DistanceToNextHoliday']] = self.df['DistanceToNextHoliday'].astype(
            int)
        self.df.loc[:, ['DistanceFromPrevHoliday']] = self.df['DistanceFromPrevHoliday'].astype(
            int)

    def _set_holidays(self) -> None:
        """Filters the holiday dates from a given dateframe"""
        self.holidays = self.df.query(
            "StateHoliday in ['a', 'b', 'c']")['Date'].dt.date.unique()
        self.holidays.sort()

    def _get_holiday_distances(self, date) -> list[int, int]:
        """takes in a date, then tells me it's distance on both dxns for the closest holiday"""
        previous, upcoming = self._get_neighbors(date)

        after_holiday = date - previous

        to_next_holiday = upcoming - date

        return int(after_holiday.days), int(to_next_holiday.days)

    def _get_neighbors(self, date) -> list[pd.to_datetime, pd.to_datetime]:
        """uses a sorted list of dates to get the neighboring 
        dates for a date. 
        """
        date = pd.to_datetime(date)
        original_year = None
        if date.year >= self.holidays[-1].year:
            original_year = date.year
            # Assume the date given is in 2014
            date = pd.to_datetime(f"2014-{date.month}-{date.day}")
        previous, upcoming = None, None
        for i, d in enumerate(self.holidays):
            if d >= date.date():
                previous = pd.to_datetime(self.holidays[i-1])
                upcoming = pd.to_datetime(self.holidays[i])
                if original_year:
                    previous = pd.to_datetime(
                        f"{original_year}-{previous.month}-{previous.day}")
                    upcoming = pd.to_datetime(
                        f"{original_year}-{upcoming.month}-{upcoming.day}")
                return previous, upcoming
