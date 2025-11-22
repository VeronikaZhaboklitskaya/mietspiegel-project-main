from dash import Dash, html, dcc, callback, Output, Input, State
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from datetime import datetime, timedelta

trends_layout = dmc.Group(
    [
        html.Div(
            [
                dmc.Title("Rental Price Development (2003-2024)", order=5, mb=12),
                
            ],
            style={
                "height": 550,
                "width": 1000,
                "padding": 20, 
                "background": "#FCFAEE", 
                "border-radius": 20,
                "border": "2px solid #384B70",
            }
        )
    ]
)