from dash import Dash, html, dcc, callback, Output, Input, State
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from datetime import datetime, timedelta

calculator_layout = dmc.Group(
    [
        html.Div(
            [
                dmc.Title("Check Your Rental Offer", order=5, mb=12),
                dmc.Text("Adress"),
                dmc.TextInput(
                    placeholder="e.g. Torstraße 101",
                    description="Enter the address of a rental, including street name and house number",
                    radius="md",
                    variant="default",
                    mb=30,
                ),
                dmc.Text("Apartment Size (m²)"),
                dmc.Slider(
                    id="slider-callback",
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
                    leftSection=DashIconify(icon="fa:calendar"),
                    leftSectionPointerEvents="none",
                    placeholder="Pick date",
                    minDate=datetime(1800,1,1),
                    maxDate=datetime.now(),
                    value=datetime(1960, 1, 1),
                    w=200,
                    mb=30,
                ), 
                dmc.Text("Offered Rent (€ per month)", mb=12),
                dmc.TextInput(
                    placeholder="e.g. 850",
                    description="Total cold rent (Kaltmiete)",
                    radius="md",
                    variant="default",
                    mb=30,
                ),
                
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
            [
                dmc.Button(
                    "Calculate Comparison",
                    variant="default",
                    color="#384B70",
                    size="md",
                    radius="md",
                    loading=False,
                    disabled=False,
                    leftSection=DashIconify(icon="twemoji:magnifying-glass-tilted-left"),
                )
            ],
            style={
                "height": 550,
                "width": 600,
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