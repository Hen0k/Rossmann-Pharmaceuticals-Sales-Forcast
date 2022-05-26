import pandas as pd
from src.rotating_logs import get_rotating_log


logger = get_rotating_log(
    filename='preprocessing.log', logger_name='PreProcessorLogger')


class PreProcess:
    def __init__(self, df):
        self.df = df
        assert 'Date' in self.df.columns
        self.holidays = None

    def generate_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Adds date related categorical columns to the dataframe"""
        
        self.df = self.create_holiday_distance_cols(self.df)
        self.df['Year'] = self.df['Date'].dt.year
        self.df['Month'] = self.df['Date'].dt.month
        self.df['WeekOfYear'] = self.df['Date'].dt.isocalendar().week
        self.df['is_month_end'] = self.df['Date'].dt.is_month_end
        self.df['is_month_start'] = self.df['Date'].dt.is_month_start
        self.df['is_quarter_end'] = self.df['Date'].dt.is_quarter_end
        self.df['is_quarter_start'] = self.df['Date'].dt.is_quarter_start
        self.df['is_year_end'] = self.df['Date'].dt.is_year_end
        self.df['is_year_start'] = self.df['Date'].dt.is_year_start
        logger.info("9 new columns added to the dataframe")
        return df
        

    def create_holiday_distance_cols(self, df: pd.DataFrame) -> None:
        self.df['DistanceToNextHoliay'] = pd.NA
        self.df['DistanceFromPrevHoliay'] = pd.NA
        unique_dates = self.df.Date.unique()
        for date in unique_dates:
            after_holiday, to_next_holiday = self._get_holiday_distances(date)
            indecies = self.df[self.df['Date'] == date].index
            self.df.loc[indecies, 'DistanceToNextHoliay'] = to_next_holiday
            self.df.loc[indecies, 'DistanceFromPrevHoliay'] = after_holiday
        self.df['DistanceToNextHoliay'] = self.df['DistanceToNextHoliay'].astype(
            int)
        self.df['DistanceFromPrevHoliay'] = self.df['DistanceFromPrevHoliay'].astype(
            int)

    def _get_holidays(self):
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
