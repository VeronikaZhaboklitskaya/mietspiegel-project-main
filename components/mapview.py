from dash import Dash, html, dcc, callback, Output, Input, State
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from datetime import datetime, timedelta
from dash.exceptions import PreventUpdate
import pandas as pd

location_text = dmc.Stack(
    [
        dmc.Title("Simple residential area", order=4),
        dmc.Text("Simple residential areas usually have little greenery and a below-average image (a low or very low status index in the Social City Monitoring programme). They are often further away from city centres and exposed to above-average environmental noise. Few amenities for daily needs, in conjunction with the above characteristics, can also be indicators of a simple residential area, as can below-average standard land values."),
        dmc.Space(h=8),
        dmc.Title("Medium residential area", order=4),
        dmc.Text("Medium residential areas tend to have average greenery and a mostly average image in terms of the status index of the Social City Monitoring programme. They are often located at an average distance from city centres. Environmental noise pollution is in the medium range. The range of services for daily needs is average. This also applies to standard land values."),
        dmc.Space(h=8),
        dmc.Title("Good residential area", order=4),
        dmc.Text("Good residential areas are usually located close to city centres or sub-centres and the typical influences associated with them. In addition, these areas are usually characterised by a high level of greenery and a good to very good image in terms of the status index of the Social City Monitoring programme. Environmental noise is rare. There are good amenities for everyday needs, and the standard land values are above average."),
    ]
)

mapview_layout = dmc.Group(
    [
        html.Div(
            [
                dmc.Title("Filter Options", order=5, mb=12),
                dmc.Text("Apartment Size (m²) Range"),
                dmc.RangeSlider(
                    id="apartment-size-range-input",
                    value=[50,80],
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
                    minDate=datetime(1800,1,1),
                    maxDate=datetime.now(),
                    w=200,
                    mb=30,
                ), 
                dmc.Group(
                    justify="flex-start",
                    gap="xs",
                    mb=12,
                    children=[
                        dmc.Text("Location Quality"),
                        dmc.Modal(
                            id="modal",
                            size="40%",
                            centered=True,
                            padding=20, 
                            radius=20,
                            children=[dmc.Text(location_text)],
                        ),
                        dmc.ActionIcon(
                            DashIconify(icon="twemoji:red-question-mark", width=20),
                            id="modal-button",
                            variant="outline",
                            color="#384B70",
                            size="md",
                            radius="md",
                        ),]
                ),                
                # dmc.Select(
                #     placeholder="All Categories",
                #     id="location-select",
                #     data=[
                #         {"value": "simple", "label": "Simple"},
                #         {"value": "medium", "label": "Medium"},
                #         {"value": "good", "label": "Good"},
                #     ],
                #     w=200,
                #     mb=30,
                # )
                
            ],
            style={
                "height": 550,
                "width": 400,
                "background": "#FCFAEE", 
                "padding": 20, 
                "border-radius": 20,
                "border": "2px solid #384B70",
            }
        ),
        html.Div(
            
            id="median-rent",
            children=[
                    dmc.Button(
                        "Show Median Rent by District",
                        id="show-median-rent-button",
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
                "height": 550,
                "width": 800,
                "background": "#FCFAEE", 
                "border-radius": 20,
                "border": "2px solid #384B70",
                "display": "flex",
                "justifyContent": "center",
                "alignItems": "center",
            }
        )
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


def register_callbacks_mapview(app):
    @app.callback(
        Output("modal", "opened"),
        Input("modal-button", "n_clicks"),
        State("modal", "opened"),
        prevent_initial_call=True,
    )
    
    def toggle_modal(n_clicks, opened):
        return not opened
    
    @app.callback(
        Output('show-median-rent-button', 'style', allow_duplicate=True),
        Output('body-div', 'children', allow_duplicate=True),
        Input('show-median-rent-button', 'n_clicks'),
        [Input('apartment-size-range-input', 'value'),
         Input('construction-year-range-input', 'value'),
        ],
         prevent_initial_call=True
    )
    def update_output(n_clicks, apartment_size, construction_year):
        if n_clicks is None:
            raise PreventUpdate
        elif apartment_size is None or construction_year is None:
            raise PreventUpdate
        else:
            hidden_style = {"display": "none"}
            #result = show_median_rent_by_district(apartment_size, construction_year,  location_quality)

    @app.callback(
        Output("show-median-rent-button", "style", allow_duplicate=True),
        Output("body-div", "children", allow_duplicate=True),
        Input("show-median-rent-again-button", "n_clicks"),
        prevent_initial_call=True,
    )
    def reset_calculator(n_clicks):
        if not n_clicks:
            raise PreventUpdate

        show_style = {"display": "block"}

        return show_style, None


