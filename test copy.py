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

def filter_with_grouped_upper_bound(df, year_range, area_range):
    year_min, year_max = year_range
    area_min, area_max = area_range

    df["Construction year (max)"] = (
        df["Construction year (max)"]
        .astype(str)
        .str[:4]
        .astype(int)
    )

    df["Living area (max)"] = (
        df["Living area (max)"]
        .astype(str)
        .str.replace(",", ".")
        .str.replace("\xa0", "") 
        .astype(float)
    )

     # Filter rows by lower bounds first
    df = df[
        (df["Construction year (max)"] >= year_min) &
        (df["Living area (max)"] >= area_min)
    ].sort_values(["Construction year (max)", "Living area (max)"]).reset_index()

    selected_rows = []
    year_limit = None
    area_limit = None

    for _, row in df.iterrows():
        year = row["Construction year (max)"]
        area = row["Living area (max)"]

        if area < area_max:
            area_limit = None

        if year_limit is not None and year > year_limit:
            break

        if area_limit is not None and area > area_max:
            continue

        if area >= area_max and area_limit is None:
            area_limit = area
            selected_rows.append(row)
            continue

        if year >= year_max and year_limit is None:
            year_limit = year
            selected_rows.append(row)
            continue

        selected_rows.append(row)

    return df.loc[[r.name for r in selected_rows]]

def get_average_mean_by_quality(year_range, size_range):
    csv_path = "data/csv_files/2024converted.csv"
    current_mietspiegel_table = pd.read_csv(csv_path)
    
    table_cropped_simple = current_mietspiegel_table.loc[0:48]
    table_cropped_medium = current_mietspiegel_table.loc[49:116]
    table_cropped_good = current_mietspiegel_table.loc[117:162]

    subset_simple = filter_with_grouped_upper_bound(table_cropped_simple, year_range, size_range)
    subset_medium = filter_with_grouped_upper_bound(table_cropped_medium, year_range, size_range)
    subset_good = filter_with_grouped_upper_bound(table_cropped_good, year_range, size_range)

    simple_average_mean = get_average_mean_from_subset(subset_simple)
    medium_average_mean = get_average_mean_from_subset(subset_medium)
    good_average_mean = get_average_mean_from_subset(subset_good)

    return {"einfach": simple_average_mean, "mittel": medium_average_mean, "gut": good_average_mean}

BERLIN_DISTRICTS = [
    "Charlottenburg-Wilmersdorf",
    "Friedrichshain-Kreuzberg",
    "Lichtenberg",
    "Marzahn-Hellersdorf",
    "Mitte",
    "Neukölln",
    "Pankow",
    # "Reinickendorf",
    # "Spandau",
    # "Steglitz-Zehlendorf",
    # "Tempelhof-Schöneberg",
    # "Treptow-Köpenick",
]


def get_average_mean_by_district(year_range, size_range):

    average_mean_by_quality = get_average_mean_by_quality(year_range, size_range) # {'einfach': n1, 'mittel': n2, 'gut': n3}
    average_mean_values_by_district = {}

    for district in BERLIN_DISTRICTS:
        count_by_distr = get_location_data_by_district(district) # {'einfach': { 'west': c1, 'ost': c2 }, 'mittel': ....}

        count_simple = count_by_distr.get("einfach", {}).get("west", 0) + count_by_distr.get("einfach", {}).get("ost", 0)
        count_medium = count_by_distr.get("mittel", {}).get("west", 0) + count_by_distr.get("mittel", {}).get("ost", 0)
        count_good = count_by_distr.get("gut", {}).get("west", 0) + count_by_distr.get("gut", {}).get("ost", 0)
        count_all = count_simple + count_medium + count_good

        average_mean_value_for_district = round((count_simple * average_mean_by_quality["einfach"] + count_medium * average_mean_by_quality["mittel"] + count_good * average_mean_by_quality["gut"]) / count_all, 2)

        average_mean_values_by_district[district] = average_mean_value_for_district

    return average_mean_values_by_district


def get_average_mean_from_subset(df):

    sum = 0
    for _, row in df.iterrows():
        
        mean_value = float(str(row["Mean value"]).replace(",", "."))

        sum += mean_value

    result = round(sum / df.shape[0], 2)

    return result

#print(get_location_data_by_district("Friedrichshain-Kreuzberg"))

#csv_path = "data/csv_files/2024converted.csv"
#current_mietspiegel_table = pd.read_csv(csv_path)

# print(current_mietspiegel_table.columns)
#print(current_mietspiegel_table)

print(get_average_mean_by_district([1910, 1918], [40,50]))


