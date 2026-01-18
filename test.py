import requests
import pandas as pd
from collections import Counter, defaultdict

def get_location_data_by_district(district):
    url = "https://gdi.berlin.de/services/wfs/wohnlagenadr2024"

    cql = f"bezname='{district}'"

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

    features = data.get("features", [])
    if not features:
        return None

    # wol -> Counter(stadtteil)
    result = defaultdict(Counter)

    for feature in features:
        props = feature.get("properties", {})

        wol = props.get("wol")
        stadtteil = props.get("stadtteil")

        if not wol or not stadtteil:
            continue

        result[wol.lower()][stadtteil.lower()] += 1

    # convert defaultdict to normal dict for clean output
    return {wol: dict(counter) for wol, counter in result.items()}

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

def show_median_rent_by_district(apartment_size_range, construction_year_range) -> dict | None:

    try:
        apartment_size = float(str(apartment_size).replace(",", "."))
        construction_year = int(str(construction_year)[:4])
    except (TypeError, ValueError):
        return None

    csv_path = "data/csv_files/2024converted.csv"
    current_mietspiegel_table = pd.read_csv(csv_path)

    if location_quality == "einfach":
        location_quality = "simple"
        current_mietspiegel_table_cropped = current_mietspiegel_table.loc[0:48]
    elif location_quality == "mittel":
        location_quality = "medium"
        current_mietspiegel_table_cropped = current_mietspiegel_table.loc[49:116]
    else:
        location_quality = "good"
        current_mietspiegel_table_cropped = current_mietspiegel_table.loc[117:162]

    for _, row in current_mietspiegel_table_cropped.iterrows():

        raw_year_cell = str(row["Construction year (max)"]).lower()
        construction_year_integer = int(raw_year_cell[:4])

        row_stadtteil = None
        if "west" in raw_year_cell:
            row_stadtteil = "west"
        elif "ost" in raw_year_cell:
            row_stadtteil = "ost"

        if row_stadtteil is not None and row_stadtteil != stadtteil:
            continue

        apartment_size_integer = int(parse_number(row["Living area (max)"]))
        if construction_year <= construction_year_integer and apartment_size <= apartment_size_integer:
            lower = float(str(row["Lower range"]).replace(",", "."))
            mean = float(str(row["Mean value"]).replace(",", "."))
            upper = float(str(row["Upper range"]).replace(",", "."))

            expected_lower = lower * apartment_size
            expected_mean = mean * apartment_size
            expected_upper = upper * apartment_size

            return {
                "location_quality": location_quality,
                "lower_range_per_m2": lower,
                "mean_value_per_m2": mean,
                "upper_range_per_m2": upper,
                "difference_lower": round((offered_rent - expected_lower) / expected_lower * 100, 2),
                "difference_mean": round((offered_rent - expected_mean) / expected_mean * 100, 2),
                "difference_upper": round((offered_rent - expected_upper) / expected_upper * 100, 2),
            }  
 
    return None

print(get_location_data_by_district("Friedrichshain-Kreuzberg"))
#print(compare_to_median_rent("Torstraße", "101", "10119", "77", "1998", "1300"))

csv_path = "data/csv_files/2024converted.csv"
current_mietspiegel_table = pd.read_csv(csv_path)

# print(current_mietspiegel_table.columns)
print(current_mietspiegel_table)


