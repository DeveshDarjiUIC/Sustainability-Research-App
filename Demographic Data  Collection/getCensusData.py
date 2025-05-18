import requests
import pandas as pd

def get_census_data(base_url, group_id):
    """
    Fetches ACS5 data from the Census API for a specified base URL and group ID across predefined cities.

    Args:
        base_url (str): The Census API endpoint URL (e.g., for subject or profile data)
        group_id (str): The Census group ID (e.g., 'DP03' or 'S1501')

    Returns:
        pd.DataFrame: Combined DataFrame containing data for all cities, or None if no data was retrieved.
    """
    cities_geoids = {
              "Algonquin": "1600000US1700685",
        "Arlington Heights": "1600000US1702154",
        "Aurora": "1600000US1703012",
       "Alsip": "1600000US1701010",
        "Bannockburn": "1600000US1703610",
        "Bartlett": "1600000US1704013",
       "Batavia": "1600000US1704078",
        "Beach Park": "1600000US1704303",
        "Belleville": "1600000US1704845",
        "Bensenville": "1600000US1705248",
        "Berwyn": "1600000US1705573",
        "Bloomington": "1600000US1706613",
        "Bolingbrook": "1600000US1707133",
        "Brookfield": "1600000US1708576",
        "Buffalo Grove": "1600000US1709447",
        "Carbondale": "1600000US1711163",
        "Carol Stream": "1600000US1711490",
        "Carpentersville": "1600000US1711358",
        "Champaign": "1600000US1712385",
        "Chicago": "1600000US1714000",
        "Cicero": "1600000US1714351",
        "Countryside": "1600000US1716873",
        "Crystal Lake": "1600000US1717887",
        "Decatur": "1600000US1718919",
        "DeKalb": "1600000US1719214",
        "Deer Park": "1600000US1719083",
       "Decatur": "1600000US1718823",
        "Des Plaines": "1600000US1719642",
        "Downers Grove": "1600000US1720591",
        "Elgin": "1600000US1723074",
        "Elk Grove Village": "1600000US1723256",
        "Elmhurst": "1600000US1723620",
        "Evanston": "1600000US1724582",
        "Glenview": "1600000US1730190",
        "Geneva": "1600000US1728872",
        "Grayslake": "1600000US1731121",
        "Hanover Park": "1600000US1732746",
        "Hoffman Estates": "1600000US1735411",
        "Joliet": "1600000US1738801",
        "La Grange": "1600000US1740767",
        "Lombard": "1600000US1744407",
        "Moline": "1600000US1749867",
        "Mount Prospect": "1600000US1751089",
        "Naperville": "1600000US1751622",
        "Normal": "1600000US1753590",
        "Northbrook": "1600000US1753234",
        "Oak Lawn": "1600000US1754820",
        "Oak Park": "1600000US1754885",
        "Orland Park": "1600000US1756640",
        "Palatine": "1600000US1757225",
        "Park Ridge": "1600000US1757875",
        "Peoria": "1600000US1759000",
        "Plainfield": "1600000US1760287",
        "Quincy": "1600000US1762389",
        "Rock Island": "1600000US1765092",
        "Rockford": "1600000US1765001",
        "Rolling Meadows": "1600000US1765338",
        "Romeoville": "1600000US1765429",
        "Schaumburg": "1600000US1768084",
        "Skokie": "1600000US1770122",
        "Springfield": "1600000US1772000",
        "Streamwood": "1600000US1773157",
        "Tinley Park": "1600000US1775484",
        "Urbana": "1600000US1777007",
        "Waukegan": "1600000US1779293",
        "Wheaton": "1600000US1781048",
        "Wheeling": "1600000US1781087",
        "Wilmette": "1600000US1782075"
    }

    params = {
        "get": f"group({group_id})"
    }

    all_data_frames = []

    for city, geoid in cities_geoids.items():
        print(f"Fetching data for: {city} (GEOID: {geoid})")
        current_params = params.copy()
        current_params["ucgid"] = geoid

        try:
            response = requests.get(base_url, params=current_params)
            response.raise_for_status()

            data = response.json()

            if data and len(data) > 1:
                header = data[0]
                records = data[1:]
                df_city = pd.DataFrame(records, columns=header)
                df_city['City'] = city
                all_data_frames.append(df_city)
                print(f" -> Success.")
            else:
                print(f" -> No data returned for {city}.")

        except requests.exceptions.RequestException as e:
            print(f" -> Error fetching data for {city}: {e}")
        except Exception as e:
            print(f" -> An error occurred processing data for {city}: {e}")

    if all_data_frames:
        final_df = pd.concat(all_data_frames, ignore_index=True)
        cols = ['City'] + [col for col in final_df.columns if col != 'City']
        final_df = final_df[cols]
        return final_df
    else:
        print("No data was successfully retrieved for any city.")
        return None

# Example usage for profile data:
profile_df = get_census_data(
    base_url="https://api.census.gov/data/2023/acs/acs5/profile",
    group_id="DP03"
)

# Example usage for subject data:
# subject_df = get_census_data(
#     base_url="https://api.census.gov/data/2023/acs/acs5/subject",
#     group_id="S1501"
# )

