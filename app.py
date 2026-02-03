from dash import Dash, html, dcc, callback, Output, Input, State
import dash_mantine_components as dmc
import plotly.express as px
import pandas as pd
from dash_iconify import DashIconify
from components.pricebydistrict import (
    pricebydistrict_layout,
    register_callbacks_mapview,
)
from components.calculator import calculator_layout, register_callbacks_calculator

app = Dash(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=dmc.styles.ALL,
)

location_text = dmc.Stack(
    [
        dmc.Title("Simple residential location quality", order=4),
        dmc.Text(
            "Areas typically feature limited greenery and below-average image (a low or very low status index in the Social City Monitoring programme). They are often located further from city centres and exposed to above-average environmental noise. Few amenities for daily needs can also be indicators of a simple residential area in conjunction with the above-mentioned characteristics, as can below-average standard land values."
        ),
        dmc.Space(h=8),
        dmc.Title("Medium residential location quality", order=4),
        dmc.Text(
            "These areas tend to have average greenery and a mostly average image in terms of the Social City Monitoring status index. They are often located at an average distance from city centres. Environmental noise pollution is in the medium range. The range of amenities for daily needs is average. This also applies to standard land values."
        ),
        dmc.Space(h=8),
        dmc.Title("Good residential location quality", order=4),
        dmc.Text(
            "These areas are usually located close to city centres or sub-centres and the associated typical influences. In addition, the location is usually characterised by a high level of greenery and a good to very good image in terms of the status index of the Social City Monitoring programme. Environmental noise is rare. The supply of everyday necessities is good, and the standard land values are above average."
        ),
    ]
)


layout = dmc.AppShell(
    [
        dmc.AppShellHeader(
            dmc.Group(
                [
                    DashIconify(icon="twemoji:houses", width=120),
                    html.Div(
                        [
                            dmc.Title(
                                "Berlin Mietspiegel Dashboard",
                                c="white",
                                order=1,
                                mb=12,
                            ),
                            dmc.Text(
                                "Understanding rental prices in Berlin - a tool for newcomers",
                                c="white",
                                tt="uppercase",
                                size="sm",
                            ),
                        ]
                    ),
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
                            dmc.Text(
                                "The Mietspiegel (rent index) shows typical rental prices in Berlin based on location quality, apartment size, and building characteristics. Use this tool to explore rental prices across districts and compare them with actual rental offers."
                            ),
                            dmc.Group(
                                justify="flex-start",
                                gap="xs",
                                mt="lg",
                                mb=12,
                                children=[
                                    dmc.Text("What is location quality"),
                                    dmc.Modal(
                                        id="modal",
                                        size="40%",
                                        centered=True,
                                        padding=30,
                                        radius=20,
                                        children=[dmc.Text(location_text)],
                                    ),
                                    dmc.ActionIcon(
                                        DashIconify(
                                            icon="twemoji:red-question-mark", width=20
                                        ),
                                        id="modal-button",
                                        variant="outline",
                                        color="#384B70",
                                        size="md",
                                        radius="md",
                                    ),
                                ],
                            ),
                        ],
                        icon=DashIconify(
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
                                                    icon="twemoji:abacus", width=20
                                                ),
                                                value="calculator",
                                                fz="md",
                                                p="md",
                                            ),
                                            dmc.TabsTab(
                                                "Price by district",
                                                leftSection=DashIconify(
                                                    icon="twemoji:round-pushpin",
                                                    width=20,
                                                ),
                                                value="pricebydistrict",
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
                    html.Div(
                        id="tabs-content",
                        style={
                            "paddingTop": 10,
                        },
                    ),
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
                    dmc.Text(
                        "Bachelor Thesis Project 2026",
                        c="white",
                        size="sm",
                        ta="center",
                        m=10,
                    ),
                ]
            ),
            style={
                "backgroundColor": "#507687",
            },
        ),
    ],
    header={
        "height": 140,
    },
    footer={
        "height": 40,
    },
    padding="sm",
    id="appshell",
)

app.layout = dmc.MantineProvider(layout)

register_callbacks_mapview(app)
register_callbacks_calculator(app)



@callback(
    Output("modal", "opened"),
    Input("modal-button", "n_clicks"),
    State("modal", "opened"),
    prevent_initial_call=True,
)
def toggle_modal(n_clicks, opened):
    return not opened


@callback(Output("tabs-content", "children"), Input("tabs", "value"))
def render_content(active):
    if active == "pricebydistrict":
        return pricebydistrict_layout
    else:
        return calculator_layout



if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)