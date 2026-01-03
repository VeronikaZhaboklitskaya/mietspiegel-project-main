import requests
import pandas as pd

def get_location_quality(street, house_number, postcode):
    url = "https://gdi.berlin.de/services/wfs/wohnlagenadr2024"

    # Build the CQL filter
    cql = f"strasse='{street}' AND hnr='{house_number}' AND plz='{postcode}'"

    params = {
        "SERVICE": "WFS",
        "REQUEST": "GetFeature",
        "VERSION": "1.1.0",
        "TYPENAME": "wohnlagenadr2024:wohnlagenadr2024",
        "OUTPUTFORMAT": "json",
        "cql_filter": cql
    }

    response = requests.get(url, params=params)

    data = response.json()

    if not data["features"]:
        return None
    
    props = data["features"][0]["properties"]

    return {
        "wohnlage": props["wol"],
        "stadtteil": props["stadtteil"]
    }

def compare_to_median_rent(street, house_number, postcode, apartment_size, construction_year,  offered_rent) -> float:
    
    location_quality = get_location_quality(street, house_number, postcode)

    if location_quality is None:
        return None

    csv_path = "data/csv_files/2024converted.csv"
    current_mietspiegel_table = pd.read_csv(csv_path)

    if location_quality == "einfach":
        current_mietspiegel_table_cropped = current_mietspiegel_table.loc[0:48]
    elif location_quality == "mittel":
        current_mietspiegel_table_cropped = current_mietspiegel_table.loc[49:116]
    else:
        current_mietspiegel_table_cropped = current_mietspiegel_table.loc[117:162]

    for index, row in current_mietspiegel_table_cropped.iterrows():
        if construction_year <= row["Construction year (max)"] and apartment_size <= row["Living area (max)"]:
            print(index,row)
            break


    return current_mietspiegel_table_cropped

print(get_location_quality("Torstraße", "101", "10119"))
print(compare_to_median_rent("Torstraße", "101", "10119", "77", "1998", "1300"))

csv_path = "data/csv_files/2024converted.csv"
# current_mietspiegel_table = pd.read_csv(csv_path)

# print(current_mietspiegel_table.columns)
# print(current_mietspiegel_table)


