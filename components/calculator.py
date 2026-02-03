from dash import Dash, html, dcc, callback, Output, Input
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from datetime import datetime, timedelta
from dash.exceptions import PreventUpdate
import requests
import pandas as pd

calculator_layout = dmc.Group(
    [
        html.Div(
            [
                dmc.Title("Check Your Rental Offer", order=5, mb=12),
                dmc.Text("Adress"),
                dmc.TextInput(
                    id="street-input",
                    placeholder="e.g. Torstraße",
                    description="Enter the address of a rental, including street name, house number and postcode",
                    radius="md",
                    variant="default",
                    required=True,
                    mb=10,
                ),
                dmc.TextInput(
                    id="house-input",
                    placeholder="e.g. 101",
                    radius="md",
                    variant="default",
                    required=True,
                    mb=10,
                ),
                dmc.TextInput(
                    id="postcode-input",
                    placeholder="e.g. 10119",
                    radius="md",
                    variant="default",
                    required=True,
                    mb=30,
                ),
                dmc.Text("Apartment Size (m²)"),
                dmc.Slider(
                    id="slider-apartment-size",
                    value=50,
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
                dmc.Text("Construction Year", mb=12),
                dmc.YearPickerInput(
                    id="construction-year-input",
                    leftSection=DashIconify(icon="fa:calendar"),
                    leftSectionPointerEvents="none",
                    minDate=datetime(1800, 1, 1),
                    maxDate=datetime(2022, 1, 1),
                    value=datetime(1960, 1, 1),
                    w=200,
                    mb=30,
                ),
                dmc.Text("Offered Rent (€ per month)", mb=12),
                dmc.TextInput(
                    id="offered-rent-input",
                    placeholder="e.g. 850",
                    description="Total cold rent (Kaltmiete)",
                    radius="md",
                    variant="default",
                    required=True,
                    mb=30,
                ),
            ],
            style={
                "height": 620,
                "width": 400,
                "background": "#FCFAEE",
                "padding": 20,
                "border-radius": 20,
                "border": "2px solid #384B70",
            },
        ),
        html.Div(
            id="calculator-container",
            children=[
                dmc.Button(
                    "Calculate Comparison",
                    id="calculate-comparison-button",
                    variant="default",
                    color="#384B70",
                    size="md",
                    radius="md",
                    loading=False,
                    disabled=False,
                    leftSection=DashIconify(
                        icon="twemoji:magnifying-glass-tilted-left"
                    ),
                ),
                html.Div(id="body-div"),
            ],
            style={
                "height": 620,
                "width": 500,
                "background": "#FCFAEE",
                "border-radius": 20,
                "display": "flex",
                "flexDirection": "column",
                "justifyContent": "center",
                "alignItems": "center",
                "border": "2px solid #384B70",
                "padding": "20px",
            },
        ),
    ]
)


def compare_to_mean_rent(
    street, house_number, postcode, apartment_size, construction_year, offered_rent
) -> dict | None:

    try:
        offered_rent = float(str(offered_rent).replace(",", "."))
        apartment_size = float(str(apartment_size).replace(",", "."))
        construction_year = int(str(construction_year)[:4])
    except (TypeError, ValueError):
        return None

    location_data = get_location_data(street, house_number, postcode)

    if location_data is None:
        return None

    location_quality = location_data["wol"]
    stadtteil = location_data["stadtteil"].lower()


    if location_quality is None:
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
        if (
            construction_year <= construction_year_integer
            and apartment_size <= apartment_size_integer
        ):
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
                "difference_lower": round(
                    (offered_rent - expected_lower) / expected_lower * 100, 2
                ),
                "difference_mean": round(
                    (offered_rent - expected_mean) / expected_mean * 100, 2
                ),
                "difference_upper": round(
                    (offered_rent - expected_upper) / expected_upper * 100, 2
                ),
            }

    return None


def parse_number(s):
    if s is None:
        return 0.0
    s = str(s).replace("\xa0", "")
    s = s.replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return 0.0


def get_location_data(street, house_number, postcode):
    url = "https://gdi.berlin.de/services/wfs/wohnlagenadr2024"

    formatted_house_number = house_number.zfill(3)

    cql = f"strasse='{street}' AND hnr='{formatted_house_number}' AND plz='{postcode}'"

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

    if not data["features"]:
        return None
    feature = data["features"][0]

    properties = feature["properties"]
    wol = properties.get("wol")
    stadtteil = properties.get("stadtteil")   

    if wol is None or stadtteil is None:
        return None

    return {"wol": wol, "stadtteil": stadtteil.lower()}


def register_callbacks_calculator(app):

    @app.callback(
        Output("calculate-comparison-button", "style", allow_duplicate=True),
        Output("body-div", "children", allow_duplicate=True),
        Input("calculate-comparison-button", "n_clicks"),
        [
            Input("street-input", "value"),
            Input("house-input", "value"),
            Input("postcode-input", "value"),
            Input("slider-apartment-size", "value"),
            Input("construction-year-input", "value"),
            Input("offered-rent-input", "value"),
        ],
        prevent_initial_call=True,
    )
    def update_output(
        n_clicks,
        street,
        house_number,
        postcode,
        apartment_size,
        construction_year,
        offered_rent,
    ):
        if n_clicks is None:
            raise PreventUpdate
        elif (
            street is None
            or house_number is None
            or postcode is None
            or apartment_size is None
            or construction_year is None
            or offered_rent is None
        ):
            raise PreventUpdate
        else:
            hidden_style = {"display": "none"}
            result = compare_to_mean_rent(
                street,
                house_number,
                postcode,
                apartment_size,
                construction_year,
                offered_rent,
            )

            difference_mean = result["difference_mean"]

            if difference_mean > 0:
                headline = f"{difference_mean}% more expensive than average"
            elif difference_mean < 0:
                headline = f"{abs(difference_mean)}% cheaper than average"
            else:
                headline = "Exactly the average rent"

            return hidden_style, html.Div(
                [
                    html.H3(f"Location quality: {result['location_quality']}"),
                    html.H3(headline),
                    html.Hr(),
                    html.P(
                        f"Lower range: {result['lower_range_per_m2']} €/m² "
                        f"({result['difference_lower']}%)"
                    ),
                    html.P(
                        f"Mean value: {result['mean_value_per_m2']} €/m² "
                        f"({result['difference_mean']}%)"
                    ),
                    html.P(
                        f"Upper range: {result['upper_range_per_m2']} €/m² "
                        f"({result['difference_upper']}%)"
                    ),
                    html.Hr(),
                    dmc.Button(
                        "Calculate comparison again",
                        id="calculate-again-button",
                        variant="default",
                        color="#384B70",
                        size="md",
                        radius="md",
                        mt=20,
                    ),
                ]
            )

    @app.callback(
        Output("calculate-comparison-button", "style", allow_duplicate=True),
        Output("body-div", "children", allow_duplicate=True),
        Input("calculate-again-button", "n_clicks"),
        prevent_initial_call=True,
    )
    def reset_calculator(n_clicks):
        if not n_clicks:
            raise PreventUpdate

        show_style = {"display": "block"}

        return show_style, None
    
    @app.callback(
    Output("calculate-comparison-button", "n_clicks", allow_duplicate=True),
    Input("calculate-again-button", "n_clicks"),
    prevent_initial_call=True,
)
    def reset_calculate_button(n_clicks_again):
        if not n_clicks_again:
            raise PreventUpdate

        return None 
