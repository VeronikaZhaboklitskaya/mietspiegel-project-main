from dash import Dash, html, dcc, callback, Output, Input, State
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from datetime import datetime, timedelta
from dash.exceptions import PreventUpdate
import pandas as pd
import requests
from collections import Counter, defaultdict
from functools import lru_cache
import logging

logging.basicConfig(
    level=logging.INFO,  # THIS is why info() was hidden
    format="%(asctime)s [%(levelname)s] %(message)s",
)

pricebydistrict_layout = dmc.Group(
    [
        html.Div(
            [
                dmc.Title("Filter Options", order=5, mb=12),
                dmc.Text("Apartment Size (m²) Range"),
                dmc.RangeSlider(
                    id="apartment-size-range-input",
                    value=[50, 80],
                    max=120,
                    color="#384B70",
                    size="lg",
                    marks=[
                        {"value": 20, "label": "20"},
                        {"value": 50, "label": "50"},
                        {"value": 80, "label": "80"},
                        {"value": 120, "label": "120+"},
                    ],
                    mt=30,
                    mb=40,
                ),
                dmc.Text("Construction Year Range", mb=12),
                dmc.YearPickerInput(
                    id="construction-year-range-input",
                    type="range",
                    leftSection=DashIconify(icon="fa:calendar"),
                    placeholder="Pick dates range",
                    minDate=datetime(1800, 1, 1),
                    maxDate=datetime(2022, 1, 1),
                    w=200,
                    mb=30,
                ),
            ],
            style={
                "height": 700,
                "width": 400,
                "background": "#FCFAEE",
                "padding": 20,
                "border-radius": 20,
                "border": "2px solid #384B70",
            },
        ),
       html.Div(
            id="median-rent",
            children=[
                html.Div(
                    style={"position": "relative"},
                    children=[
                        dmc.LoadingOverlay(
                            id="loading-overlay",
                            visible=False,
                            zIndex=1000,
                        ),
                        dmc.Button(
                            "Show Median Rent by District",
                            id="show-median-rent-button",
                            variant="default",
                            color="#384B70",
                            size="md",
                            radius="md",
                            leftSection=DashIconify(
                                icon="twemoji:magnifying-glass-tilted-left"
                            ),
                        ),
                        html.Div(id="body-div"),
                    ],
                ),
            ],
            style={
                "height": 700,
                "width": 1300,
                "background": "#FCFAEE",
                "border-radius": 20,
                "border": "2px solid #384B70",
                "display": "flex",
                "justifyContent": "center",
                "alignItems": "center",
            },
        ),
    ]
)

BERLIN_DISTRICTS = [
    "Charlottenburg-Wilmersdorf",
    "Friedrichshain-Kreuzberg",
    "Lichtenberg",
    "Marzahn-Hellersdorf",
    "Mitte",
    "Neukölln",
    "Pankow",
    "Reinickendorf",
    "Spandau",
    "Steglitz-Zehlendorf",
    "Tempelhof-Schöneberg",
    "Treptow-Köpenick",
]


@lru_cache(maxsize=15)
def get_location_data_by_district(district):
    logging.info(f"========= FETCHING DISTRICT {district} ===================")
    url = "https://gdi.berlin.de/services/wfs/wohnlagenadr2024"

    cql = f"bezname='{district}'"

    params = {
        "SERVICE": "WFS",
        "REQUEST": "GetFeature",
        "VERSION": "1.1.0",
        "TYPENAME": "wohnlagenadr2024:wohnlagenadr2024",
        "OUTPUTFORMAT": "json",
        "cql_filter": cql,
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
        df["Construction year (max)"].astype(str).str[:4].astype(int)
    )

    df["Living area (max)"] = (
        df["Living area (max)"]
        .astype(str)
        .str.replace(",", ".")
        .str.replace("\xa0", "")
        .astype(float)
    )

    # Filter rows by lower bounds first
    df = (
        df[
            (df["Construction year (max)"] >= year_min)
            & (df["Living area (max)"] >= area_min)
        ]
        .sort_values(["Construction year (max)", "Living area (max)"])
        .reset_index()
    )

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

    subset_simple = filter_with_grouped_upper_bound(
        table_cropped_simple, year_range, size_range
    )
    subset_medium = filter_with_grouped_upper_bound(
        table_cropped_medium, year_range, size_range
    )
    subset_good = filter_with_grouped_upper_bound(
        table_cropped_good, year_range, size_range
    )

    simple_average_mean = get_average_mean_from_subset(subset_simple)
    medium_average_mean = get_average_mean_from_subset(subset_medium)
    good_average_mean = get_average_mean_from_subset(subset_good)

    return {
        "einfach": simple_average_mean,
        "mittel": medium_average_mean,
        "gut": good_average_mean,
    }


def get_average_mean_by_district(year_range, size_range):

    average_mean_by_quality = get_average_mean_by_quality(
        year_range, size_range
    )  # {'einfach': n1, 'mittel': n2, 'gut': n3}
    average_mean_values_by_district = {}

    for district in BERLIN_DISTRICTS:
        count_by_distr = get_location_data_by_district(
            district
        )  # {'einfach': { 'west': c1, 'ost': c2 }, 'mittel': ....}

        count_simple = count_by_distr.get("einfach", {}).get(
            "west", 0
        ) + count_by_distr.get("einfach", {}).get("ost", 0)
        count_medium = count_by_distr.get("mittel", {}).get(
            "west", 0
        ) + count_by_distr.get("mittel", {}).get("ost", 0)
        count_good = count_by_distr.get("gut", {}).get("west", 0) + count_by_distr.get(
            "gut", {}
        ).get("ost", 0)
        count_all = count_simple + count_medium + count_good

        average_mean_value_for_district = round(
            (
                count_simple * average_mean_by_quality["einfach"]
                + count_medium * average_mean_by_quality["mittel"]
                + count_good * average_mean_by_quality["gut"]
            )
            / count_all,
            2,
        )

        average_mean_values_by_district[district] = average_mean_value_for_district

    return average_mean_values_by_district


def build_district_quality_array():
    result_array = []

    for district in BERLIN_DISTRICTS:
        data = get_location_data_by_district(district)

        if not data:
            continue

        district_entry = {
            "district": district,
            "simple": sum_quality(data, "einfach"),
            "medium": sum_quality(data, "mittel"),
            "good": sum_quality(data, "gut"),
        }

        result_array.append(district_entry)

    return result_array


def get_average_mean_from_subset(df):

    sum = 0
    for _, row in df.iterrows():

        mean_value = float(str(row["Mean value"]).replace(",", "."))

        sum += mean_value

    result = round(sum / df.shape[0], 2)

    return result


def parse_year_range(date_range):
    try:
        start_year = int(str(date_range[0])[:4])
        end_year = int(str(date_range[1])[:4])

        return [start_year, end_year]
    except (TypeError, ValueError, IndexError):
        return None


def parse_size_range(size_range):
    try:
        start_size = int(str(size_range[0]))
        end_size = int(str(size_range[1]))

        return [start_size, end_size]
    except (TypeError, ValueError, IndexError):
        return None


def sum_quality(data, quality):
    return sum(data.get(quality, {}).values())


def register_callbacks_mapview(app):

    @app.callback(
    Output("loading-overlay", "visible", allow_duplicate=True),
    Input("show-median-rent-button", "n_clicks"),
    prevent_initial_call=True,
)
    def show_loading(n_clicks):
        return True
    
    @app.callback(
        Output("loading-overlay", "visible", allow_duplicate=True),
        Output("show-median-rent-button", "style", allow_duplicate=True),
        Output("body-div", "children", allow_duplicate=True),
        Input("show-median-rent-button", "n_clicks"),
        [
            Input("apartment-size-range-input", "value"),
            Input("construction-year-range-input", "value"),
        ],
        prevent_initial_call=True,
    )
    def update_output(n_clicks, apartment_size_range, construction_year_range):
        if n_clicks is None:
            raise PreventUpdate
        elif any(x is None for x in apartment_size_range) is None or any(x is None for x in construction_year_range):
            raise PreventUpdate
        else:
            hidden_style = {"display": "none"}
            parsed_year_range = parse_year_range(construction_year_range)
            parsed_size_range = parse_size_range(apartment_size_range)

            data_price = [
                {"district": k, "average price": v}
                for k, v in get_average_mean_by_district(
                    parsed_year_range, parsed_size_range
                ).items()
            ]

            data_location_quality_count = build_district_quality_array()

        return False, hidden_style, html.Div(
            [
                dmc.Group(
                    [
                        html.H3(f"Average Rent Price by District (€/m²)"),
                        html.H3(f"Location Quality by District"),
                    ],
                    justify="space-between",
                ),
                dmc.Group(
                    [
                        dmc.BarChart(
                            h=600,
                            w=500,
                            orientation="vertical",
                            data=data_price,
                            dataKey="district",
                            series=[{"name": "average price", "color": "#384B70"}],
                        ),
                        dmc.BarChart(
                            h=600,
                            w=500,
                            orientation="vertical",
                            type="stacked",
                            data=data_location_quality_count,
                            dataKey="district",
                            series=[
                                {"name": "simple", "color": "#B8001F"},
                                {"name": "medium", "color": "#b86b00"},
                                {"name": "good", "color": "#1fb800"},
                            ],
                            style={"paddingLeft": "100px"},
                        ),
                    ],
                ),
                
            ]
        )

   