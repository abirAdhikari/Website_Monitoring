import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt

import pandas as pd
import numpy as np

df = pd.DataFrame(np.random.randn(50, 4), columns=list('ABCD'))

COLORS = [
    {
        'background': '#fef0d9',
        'text': 'rgb(30, 30, 30)'
    },
    {
        'background': '#fdcc8a',
        'text': 'rgb(30, 30, 30)'
    },
    {
        'background': '#fc8d59',
        'text': 'rgb(30, 30, 30)'
    },
    {
        'background': '#d7301f',
        'text': 'rgb(30, 30, 30)'
    },
]


def is_numeric(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


def cell_style(value, min_value, max_value):
    style = {}
    if is_numeric(value):
        relative_value = (value - min_value) / (max_value - min_value)
        if relative_value <= 0.25:
            style = {
                'backgroundColor': COLORS[0]['background'],
                'color': COLORS[0]['text']
            }
        elif relative_value <= 0.5:
            style = {
                'backgroundColor': COLORS[1]['background'],
                'color': COLORS[1]['text']
            }
        elif relative_value <= 0.75:
            style = {
                'backgroundColor': COLORS[2]['background'],
                'color': COLORS[2]['text']
            }
        elif relative_value <= 1:
            style = {
                'backgroundColor': COLORS[3]['background'],
                'color': COLORS[3]['text']
            }
    return style


def ConditionalTable(dataframe):
    max_value = df.max(numeric_only=True).max()
    min_value = df.min(numeric_only=True).max()
    rows = []
    for i in range(len(dataframe)):
        row = {}
        for col in dataframe.columns:
            value = dataframe.iloc[i][col]
            style = cell_style(value, min_value, max_value)
            row[col] = html.Div(
                value,
                style=dict({
                    'height': '100%'
                }, **style)
            )
        rows.append(row)

    return rows


app = dash.Dash()

app.scripts.config.serve_locally = True
app.css.config.serve_locally = True

app.layout = html.Div([
    dt.DataTable(
        rows=ConditionalTable(df),

        row_selectable=True,
        filterable=True,
        sortable=True,
        selected_row_indices=[],
        id='datatable',
    )
], className='container')

if __name__ == '__main__':
    app.run_server(debug=True, host='127.0.0.1', port=8055)