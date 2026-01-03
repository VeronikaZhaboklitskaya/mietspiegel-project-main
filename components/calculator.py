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
                    minDate=datetime(1800,1,1),
                    maxDate=datetime.now(),
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
                "height": 600,
                "width": 400,
                "background": "#FCFAEE", 
                "padding": 20, 
                "border-radius": 20,
                "border": "2px solid #384B70",
            }
        ),
        html.Div(
            [
                dmc.Button(
                    "Calculate Comparison",
                    id="calculate-comparison-button",
                    variant="default",
                    color="#384B70",
                    size="md",
                    radius="md",
                    loading=False,
                    disabled=False,
                    leftSection=DashIconify(icon="twemoji:magnifying-glass-tilted-left"),
                ),
                html.Div(id='body-div'),
            ],
            style={
                "height": 600,
                "width": 500,
                "background": "#FCFAEE", 
                "border-radius": 20,
                "display": "flex",
                "justifyContent": "center",
                "alignItems": "center",
                "border": "2px solid #384B70",
            }
        )
    ]
)

def compare_to_median_rent(street, house_number, postcode, apartment_size, construction_year,  offered_rent) -> float:
    
    location_quality = get_location_quality(street, house_number, postcode)
    if isinstance(construction_year, str):
        construction_year = int(construction_year[:4])

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
        construction_year_integer = int(str(row["Construction year (max)"])[:4])
        apartment_size_integer = int(float(str(row["Living area (max)"]).replace(",", ".")))
        if construction_year <= construction_year_integer and apartment_size <= apartment_size_integer:
           print(index,row)
           break      
 
    return location_quality

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

    return data["features"][0]["properties"]["wol"]

def register_callbacks_calculator(app):

    @app.callback(
        Output('calculate-comparison-button', 'style'),
        Output('body-div', 'children'),
        Input('calculate-comparison-button', 'n_clicks'),
        [Input('street-input', 'value'),
         Input('house-input', 'value'),
         Input('postcode-input', 'value'),
         Input('slider-apartment-size', 'value'),
         Input('construction-year-input', 'value'),
         Input('offered-rent-input', 'value')]
    )
    def update_output(n_clicks, street, house_number, postcode, apartment_size, construction_year,  offered_rent):
        if n_clicks is None:
            raise PreventUpdate
        elif street is None or house_number is None or postcode is None or apartment_size is None or construction_year is None or offered_rent is None:
            raise PreventUpdate
        else:
            hidden_style = {"display": "none"}
            result = compare_to_median_rent(street, house_number, postcode, apartment_size, construction_year,  offered_rent)
            return hidden_style, result