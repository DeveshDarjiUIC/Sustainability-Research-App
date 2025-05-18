import pandas as pd
import requests
import getCensusData



def cleaning_income_data (data_income):
    # Drop unnecessary columns
  # data_income = data_income.drop(columns=['NAME', 'S1501_C01_001E', 'S1501_C01_001M'])

    # Rename columns for clarity
  data_income.rename(columns={
        'S1901_C01_012E': 'Median Income',
        'S1901_C01_013E': 'Mean Income'
    }, inplace=True)

  data_income = data_income[[
        'City',
        'Median Income',
        'Mean Income'
    ]]

  return data_income

def get_income_data():
    data_income = getCensusData.get_census_data(
        base_url="https://api.census.gov/data/2023/acs/acs1/subject",
        group_id="S1901"
    )
    data_income = cleaning_income_data(data_income)
    return data_income


# Example usage for income data:
income_df = get_income_data()
print(income_df)