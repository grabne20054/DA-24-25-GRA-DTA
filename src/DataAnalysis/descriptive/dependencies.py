from collections import defaultdict
from datetime import datetime
import pandas as pd


def showZeros(growth: defaultdict, cumulative_growth: dict, end: datetime, freq: str, format: str, last_days: int = 0, cumulative: bool = False) -> tuple:
        """
        Fills in the missing dates with zero growth and forward fills the cumulative growth values.

        Args:
            growth (defaultdict): A defaultdict containing the growth data.
            cumulative_growth (dict): A dictionary containing the cumulative growth data.
            end (datetime): The end date for the date range.
            freq (str): The frequency for the date range (e.g., 'D' for daily, 'MS' for monthly start, 'YS' for yearly start).
            format (str): The date format to use for parsing and formatting dates (e.g., "%Y-%m-%d" for daily, "%Y-%m" for monthly, "%Y" for yearly).
            last_days (int, optional): The number of last days to consider for filtering the growth data. Only applicable when growth is calculated by days. Defaults to 0, which means no filtering.

        Returns:
            tuple: A tuple containing the updated growth and cumulative growth dictionaries with missing dates filled in and cumulative growth forward filled.
    
        Raises:
            ValueError: If the date format is invalid or if the end date is before the start date.
            KeyError: If the growth or cumulative growth data is missing for a specific date.
        """

        df_growth = pd.DataFrame.from_dict(growth, orient='index', columns=['growth'])

        df_growth.index = pd.to_datetime(df_growth.index.astype(str), format=format)
        end = pd.to_datetime(end, format=format)

        full_date_range = pd.date_range(start=df_growth.index.min(), end=end, freq=freq)
    
        df_growth_filled = df_growth.reindex(full_date_range, fill_value=0)
        df_growth_filled.index = df_growth_filled.index.strftime(format)
        df_growth_filled.update(df_growth)

        if cumulative:
            df_cumulative_growth = pd.DataFrame.from_dict(cumulative_growth, orient='index', columns=['cumulative_growth'])

            if format == "%Y":
                full_date_range = full_date_range.year
                df_cumulative_growth_filled = df_cumulative_growth.reindex(full_date_range)

                df_cumulative_growth_filled.ffill(inplace=True)
                df_cumulative_growth_filled.fillna(0, inplace=True)
            elif format == "%Y-%m":
                full_date_range = full_date_range.year.astype(str) + '-' + full_date_range.month.astype(str).str.zfill(2)
                df_cumulative_growth_filled = df_cumulative_growth.reindex(full_date_range)

                df_cumulative_growth_filled.ffill(inplace=True)
                df_cumulative_growth_filled.fillna(0, inplace=True)
            else:
                df_cumulative_growth_filled = df_cumulative_growth.reindex(full_date_range)
                df_cumulative_growth_filled.index = df_cumulative_growth_filled.index.strftime(format)
                df_cumulative_growth_filled.update(df_cumulative_growth)
                
                df_cumulative_growth_filled.replace(0, pd.NA, inplace=True)
                df_cumulative_growth_filled.ffill(inplace=True)
                df_cumulative_growth_filled.replace(pd.NA, 0, inplace=True)

                if last_days > 0:
                    cumulative_growth = df_cumulative_growth_filled['cumulative_growth'].iloc[-last_days:].to_dict()
                elif last_days == 0:
                    cumulative_growth = df_cumulative_growth_filled.to_dict()['cumulative_growth']

        if last_days > 0:
            growth = df_growth_filled['growth'].iloc[-last_days:].to_dict()
        elif last_days == 0:
            growth = df_growth_filled.to_dict()['growth']


        return growth, cumulative_growth if cumulative else {}
    
def calculate_percentage_growth(growth: dict) -> dict:
    """
    Calculates the percentage growth in relation to the previous period.

    Args:
        growth (dict): A dictionary containing the growth data.

    Returns:
        dict: A dictionary containing the percentage growth and growth data.
        Example: {
            "2023": [0, 100],
            "2024": [100.0, 200]
        }
    """
    first_item = True
    try:
        percentage_growth = {}
        key_list = list(growth.keys())
        for i in range(len(key_list)):
            key = key_list[i]
            if first_item:
                percentage_growth[key] = 0
                first_item = False
            else:
                previous_key = key_list[i-1]
                if growth[previous_key] == 0:
                    percentage_growth[key] = 0
                else:
                    percentage_growth[key] = round((growth[key] - growth[previous_key]) / growth[previous_key] * 100, 1)
        
        df = pd.DataFrame.from_dict(percentage_growth, orient='index', columns=['percentage_growth'])

        df_growth = pd.DataFrame.from_dict(growth, orient='index', columns=['growth'])

        df_combined = pd.concat([df, df_growth], axis=1)

        result = df_combined.apply(lambda row: [row["percentage_growth"], row["growth"]], axis=1).to_dict()

        return result
    except Exception as e:
        print("Error in _calculate_percentage_growth: ", e)
        return {}
