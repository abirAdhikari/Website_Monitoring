# Author: AADHIKARI - 06/09/2018 - first cut
# AADHIKARI - 06/13/2018 - Added 1) URL column for quick validation 2) Added 'Show Only Lowest' optional
# AADHIKARI - 06/14/2018 - Added 1) Hooked up Refresh, made other other option change serializable in jason
# AADHIKARI - 06/15/2018 - Added 1) Hooked up date based query
 
import os 
import sys 
'''
import pkg_resources
pkg_resources.require("dash==0.19.0")
pkg_resources.require("dash-core-components==0.16.0rc1")
pkg_resources.require("dash-html-components==0.9.0rc1")
pkg_resources.require("dash-renderer==0.13.0rc2")
pkg_resources.require("dash-table-experiments==0.6.0rc1")
'''

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt

import json
import pandas as pd
import numpy as np
import plotly
import logging
import sqlite3
from datetime import datetime, timedelta, date
from collections import defaultdict
import uuid
from pdfgenerator import PdfGenerator

sys.path.append('.')
from competitivedata import CompetitiveData

app = dash.Dash()

global_session_dict = defaultdict(str)

app.scripts.config.serve_locally = True
# app.css.config.serve_locally = True

def price_monitor_layout():
    
    session_id = str(uuid.uuid4())
    
    return html.Div([
        html.H1(children='Gozo Hawkeye App',
                style={
                    'textAlign': 'center', 'color' : 'orange'
                }
            ),
            html.Div(children=
                [
                    html.H6('Date Filter'),
                    dcc.DatePickerRange(
                        id='input_date_range',
                        min_date_allowed=date.today() + timedelta(1),
                        max_date_allowed=date.today() + timedelta(30),
                        initial_visible_month=date.today() + timedelta(5),
                        start_date=date.today() - timedelta(90),
                        end_date=date.today() + timedelta(7)
                    ),                  
                ], style={'width': '20%', 'height': '100%', 'display': 'inline-block'}
            ),
            html.Div(children=
                [
                    html.H6('Show Data Types'), 
                    dcc.RadioItems(
                        id='data_type',
                        options=[{'label': i, 'value': i} for i in ['Show All', 'Show Only Lowest']],
                        value='Show Only Lowest',
                        labelStyle={'display': 'inline-block'}
                    ),
                ], style={'width': '60%', 'height': '100%', 'display': 'inline-block'}
            ),
            html.Div(children=
                [   
                    html.Div(
                            html.Button('Save Report', 
                                id='save-report'
                            ),
                            style={'align': 'center', 'color' : 'blue', 'display': 'inline-block'}
                    ),
                    html.Label('Save Report (Inside .\spiders\data folder)'),
                ], style={'width': '10%', 'height': '100%', 'display': 'inline-block'}
            ),
            html.Div(children=
                [   
                    html.Div(
                        html.Button('Refresh', 
                            id='refresh-button'
                        ),
                        style={'align': 'center', 'color' : 'blue', 'display': 'inline-block'}
                    ),
                    html.Label('Hit refresh after making selections'),
                ], style={'width': '10%', 'height': '100%', 'display': 'inline-block'}
            ),
            html.Div(children=[
                    dt.DataTable(
                        #rows=DF_COMPETITION.to_dict('records'),
                        rows=[{}],
                        # optional - sets the order of columns
                        # columns=sorted(DF_COMPETITION.columns),

                        row_selectable=True,
                        filterable=True,
                        sortable=True,
                        min_height=600,
                        #min_width=1500,
                        column_widths=[20],
                        #selected_row_indices=[],
                        id='competition-datatable',
                    ), 
                    html.Div(id='selected-indexes'),
                ],
                style={'align': 'right', 'width': '100%', 'height': '100%', 'resizable': 'True'}
            ),
            
            html.Div(id='intermediate-value-generate-report', style={'display': 'none'}),
            html.Div(id='intermediate-value-refresh', style={'display': 'none'}),
            html.Div(session_id, id='session-id', style={'display': 'none'}),
        ]
    )
    
app.layout = price_monitor_layout()

COLORS_MIN = {
        'background': '#FDCC8A',
        'text': 'rgb(30, 30, 30)'
    }

COLORS_MAX = {
        'background': '#90EE90',
        'text': 'rgb(30, 30, 30)'
    }

def is_numeric(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


def cell_color_min():
    style = {
                'backgroundColor': COLORS_MIN['background'],
                'color': COLORS_MIN['text']
            }
    return style

def cell_color_max():
    style = {
                'backgroundColor': COLORS_MAX['background'],
                'color': COLORS_MAX['text']
            }
    return style
    
def make_hyperlinks(value):
    # this doesn't work for now
    #return html.Div(html.A('Verify', href=value), style = {'background': '##FDFEFE', 'text': 'rgb(30, 30, 30)'})
    #return html.A('Verify', href=value)
    return value
    
def ConditionalTable(df):
    min_indices = df.groupby(['Pickup Date', 'From City', 'To City', 'Normalized Cab Type'])['Total Price'].idxmin
    min_df = df.loc[min_indices]
    max_indices = df.groupby(['Pickup Date', 'From City', 'To City', 'Normalized Cab Type'])['Total Price'].idxmax
    max_df = df.loc[max_indices]
    
    min_indices_list = min_df.index.values
    max_indices_list = max_df.index.values
    
    #print ("min_indices", min_indices_list)
    #print ("max_indices", max_indices_list)
    
    rows = []
    for i in range(len(df)):
        row = {}
        style = {}
        if i in min_indices_list:
            style = cell_color_min()
        elif i in max_indices_list:
            style = cell_color_max()
        
        for col in df.columns:
            value = df.iloc[i][col]
            if col == 'URL' and value != None:
                row[col] = make_hyperlinks(value)
            else:
                row[col] = html.Div(
                    value,
                    style=dict({
                        'width': '100%'
                    }, **style)
                )
        rows.append(row)
    #print (rows)
    print ("Length of rows ", len(rows))
    return rows

    
def cell_style(value):
    style = {
        'backgroundColor': COLORS[0]['background'],
        'color': COLORS[0]['text']
    }
    return style

def HyperlinkedTable(dataframe):
    rows = []
    for i in range(len(dataframe)):
        row = {}
        for col in dataframe.columns:
            value = dataframe.iloc[i][col]
            if col == 'URL' and value != None:
                row[col] = make_hyperlinks(value)
            else:
                row[col] = value            
        rows.append(row)
    return rows


@app.callback(
    dash.dependencies.Output('intermediate-value-refresh', 'children'),
    [
        dash.dependencies.Input('session-id', 'children'),
        dash.dependencies.Input('input_date_range', 'start_date'),
        dash.dependencies.Input('input_date_range', 'end_date'),
        dash.dependencies.Input('data_type', 'value'),
    ])
def update_controls(
                    in_session_id,                    
                    in_start_date,
                    in_end_date,
                    in_data_type
                    ):
    _controls_to_json = json.dumps(
        {
            'start_date'                : in_start_date,
            'end_date'                  : in_end_date, 
            'data_type'                 : in_data_type
        }
    )
    print('RunUI::.update_controls(): _json_data[%s] = %s' % (in_session_id, _controls_to_json))
    logging.log(logging.INFO, 'RunUI::.update_controls(): _json_data[%s] = %s' % (in_session_id, _controls_to_json))
    global_session_dict[in_session_id] = _controls_to_json
    return _controls_to_json

@app.callback(
    dash.dependencies.Output('intermediate-value-generate-report', 'children'),
    [
        dash.dependencies.Input('session-id', 'children'),
        dash.dependencies.Input('save-report', 'n_clicks'),
    ]
)
def generate_report(in_session_id, n_clicks):

    logging.log(logging.INFO, "RunUI::generate_report(): Enter")    
    _json_data = global_session_dict[in_session_id]
    if _json_data == None or _json_data == '':
        logging.log(logging.INFO, "RunUI::generate_report(): controls date not initialized")
        return
        
    print(_json_data)
    _json_to_controls=json.loads(_json_data)    
    in_start_date = _json_to_controls["start_date"]
    in_end_date = _json_to_controls["end_date"]
    in_data_type = _json_to_controls["data_type"]
    
    cd = CompetitiveData()
    if in_data_type == 'Show All':
        df = cd.refresh_from_database(in_start_date, in_end_date)
        logging.log(logging.INFO, "RunUI::generate_report(): Show All")     
    else:
        df = cd.get_lowest_price_per_route(in_start_date, in_end_date)
        logging.log(logging.INFO, "RunUI::generate_report(): Show Only Lowest")
    
    if len(df) == 0:
        rows=[{}]
        return rows
        
    df.drop(['Pax Count', 'Base Price','URL',#'Markup Price',
                                'Cab Name',
                                'Poll Priority',
                                'URL'],   axis = 1, inplace = True)
    try:
        st = datetime.date(datetime.strptime(in_start_date, "%Y-%m-%d")).strftime("%Y_%m_%d")
        et = datetime.date(datetime.strptime(in_end_date, "%Y-%m-%d")).strftime("%Y_%m_%d")
        nt = datetime.date(datetime.now()).strftime("%Y_%m_%d_%H_%M_%S")
        report_file = ''
        if in_data_type == 'Show All':
            report_file = str('Report_All_From_' + str(st) + '_To_'+ str(et) + '_AT_'+ str(nt))
        else:
            report_file = str('Report_Lowest_From_' + str(st) + '_To_'+ str(et) + '_AT_'+ str(nt))
        report_file.replace('-', '_')
        report_file.replace(':', '_')
        report_file.replace(' ', '_')
        report_file = os.getcwd() + '\\spiders\\data\\' + report_file
        report_file_html = report_file+'.html'
        report_file_pdf = report_file+'.pdf'
        print(report_file_html, report_file_pdf)
        df.to_html(report_file_html)
        
        print_pdf = False
        if print_pdf == True:
            pdfGen = PdfGenerator()
            print('PdfGenerator Initialized')
            pdfGen.convert_it(report_file_html, report_file_pdf)
            print('Generating PDF file %s' % report_file_pdf)
            
    except Exception as ex:
        print(ex)
    logging.log(logging.INFO, "RunUI::generate_report(): Exit")
    return df.to_dict('records')

    
@app.callback(
    dash.dependencies.Output('competition-datatable', 'rows'),
    [
        dash.dependencies.Input('session-id', 'children'),
        dash.dependencies.Input('refresh-button', 'n_clicks'),
    ]
)
def update_from_database(in_session_id, n_clicks):

    logging.log(logging.INFO, "RunUI::update_from_database(): Enter")   
    _json_data = global_session_dict[in_session_id]
    if _json_data == None or _json_data == '':
        logging.log(logging.INFO, "RunUI::update_from_database(): controls date not initialized")
        return
        
    print(_json_data)
    _json_to_controls=json.loads(_json_data)    
    in_start_date = _json_to_controls["start_date"]
    in_end_date = _json_to_controls["end_date"]
    in_data_type = _json_to_controls["data_type"]
    
    cd = CompetitiveData()
    if in_data_type == 'Show All':
        df = cd.refresh_from_database(in_start_date, in_end_date)
        logging.log(logging.INFO, "RunUI::update_from_database(): Show All")
    else:
        df = cd.get_lowest_price_per_route(in_start_date, in_end_date)
        logging.log(logging.INFO, "RunUI::update_from_database(): Show Only Lowest")
    if len(df) == 0:
        rows=[{}]
        return rows
    df['URL'] = df['URL'].apply(make_hyperlinks)
    logging.log(logging.INFO, "RunUI::update_from_database(): Exit")
    return df.to_dict('records')
    
    #to enable color coding, this works with 
    #return ConditionalTable(df)

    # to enable hyper link on URL column
    #return HyperlinkedTable(df)

app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
    #'external_url': 'https://codepen.io/chriddyp/pen/dZVMbK.css'
})

if __name__ == '__main__':
    app.run_server(debug=True, host='192.168.1.9', port=8050)