import pandas as pd
import requests
import getCensusData


def cleaning_education_data(data_education):
    # Drop unnecessary columns
    data_education = data_education.drop(columns=['NAME', 'S1501_C01_001E', 'S1501_C01_001M'])

    # Rename columns for clarity
    data_education = data_education.rename(columns={
        'S1501_C02_001E': 'Total Population',
        'S1501_C02_002E': 'Less than high school graduate',
        'S1501_C02_003E': 'High school graduate (includes equivalency)',
        'S1501_C02_004E': 'Some college or associate\'s degree',
        'S1501_C02_005E': 'Bachelor\'s degree',
        'S1501_C02_006E': 'Graduate or professional degree'
    })

    data_education = data_education[[
        'City',
        'Total Population',
        'Less than high school graduate',
        'High school graduate (includes equivalency)',
        'Some college or associate\'s degree',
        'Bachelor\'s degree',
        'Graduate or professional degree'
    ]]

    return data_education

def get_education_data():
    data_education = getCensusData.get_census_data(
        base_url="https://api.census.gov/data/2023/acs/acs1/subject",
        group_id="S1501"
    )

    data_education = cleaning_education_data(data_education)
    return data_education


def main(): 
    data_education = get_education_data()
    print(data_education)

if __name__ == "__main__":
    main()