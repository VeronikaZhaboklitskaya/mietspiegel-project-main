from dash import Dash, html, dcc, callback, Output, Input, State
import dash_mantine_components as dmc
import plotly.express as px
import pandas as pd
from dash_iconify import DashIconify
from components.mapview import mapview_layout, register_callbacks_mapview
from components.calculator import calculator_layout, register_callbacks_calculator
from components.trends import trends_layout

app = Dash(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=dmc.styles.ALL,
)


layout = dmc.AppShell(
    [
        dmc.AppShellHeader(
            dmc.Group(
                [
                    DashIconify(icon="twemoji:houses", width=120),
                    html.Div(
                        [
                            dmc.Title("Berlin Mietspiegel Dashboard",
                                      c="white", order=1, mb=12),
                            dmc.Text("Understanding rental prices in Berlin - a tool for newcomers",
                                     c="white", tt="uppercase", size="sm"),
                        ]
                    )
                ],
                h="100%",
                px="md",
            ),
            style={
                "backgroundColor": "#384B70",
                "padding-left": "5%",
            },
        ),
        dmc.AppShellMain(
            dmc.Stack(
                [
                    dmc.Blockquote(
                        children=[
                            dmc.Text("What is the Mietspiegel?", fw=700),
                            dmc.Text("The Mietspiegel (rent index) shows typical rental prices in Berlin based on location, apartment size, and building characteristics. Use this tool to explore rental prices across districts and compare them with actual rental offers."),
                        ],
                        icon=DashIconify
                        (
                            icon="mdi:information",
                            color="#B8001F",
                            width=30,
                        ),
                        color="#B8001F",
                        w="80%",
                        radius=20,
                    ),
                    html.Div(
                        [
                            dmc.Tabs(
                                [
                                    dmc.TabsList(
                                        [
                                            dmc.TabsTab(
                                                "Rent Calculator",
                                                leftSection=DashIconify(
                                                    icon="twemoji:abacus", width=20),
                                                value="calculator",
                                                fz="md",
                                                p="md",
                                            ),
                                            dmc.TabsTab(
                                                "Map View",
                                                leftSection=DashIconify(
                                                    icon="twemoji:round-pushpin", width=20),
                                                value="mapview",
                                                fz="md",
                                                p="md",
                                            ),
                                            dmc.TabsTab(
                                                "Price Trends",
                                                leftSection=DashIconify(
                                                    icon="twemoji:bar-chart", width=20),
                                                value="trends",
                                                fz="md",
                                                p="md",
                                            ),
                                        ]
                                    ),
                                ],
                                id="tabs",
                                variant="default",
                                radius="md",
                                value="calculator",
                                color="#B8001F",
                            ),
                        ]
                    ), 
                    html.Div(id="tabs-content", style={"paddingTop": 10,}),
                ]
            ),
            style={
                "backgroundColor": "white",
                "padding-left": "5%",
            },
        ),
        dmc.AppShellFooter(
                    html.Div(
                        [
                            dmc.Text("Bachelor Thesis Project 2025",
                                     c="white", size="sm", ta="center", m=20),
                        ]
                    ),
            style={
                "backgroundColor": "#507687",
            },
        ),
    ],
    header={
        "height": 160,
    },
    footer={
        "height": 60,
    },
    padding="md",
    id="appshell",
)

app.layout = dmc.MantineProvider(layout)

register_callbacks_mapview(app)
register_callbacks_calculator(app)

@callback(Output("tabs-content", "children"), Input("tabs", "value"))
def render_content(active):
    if active == "mapview":
        return mapview_layout
    elif active == "calculator":
        return calculator_layout
    else:
        return trends_layout


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)


