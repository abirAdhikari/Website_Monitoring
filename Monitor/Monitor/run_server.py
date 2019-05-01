import dash
import dash_core_components as dcc
import dash_html_components as html
from datetime import datetime, timedelta, date
import plotly
import plotly.graph_objs as go

import json
import logging
from logging.handlers import RotatingFileHandler
from collections import defaultdict
import uuid



# our libraries
#import run_all
from hawkeyeutils import *

#Define Dash App
app=dash.Dash()

global_session_dict = defaultdict(str)

app.layout = html.Div([
    html.H1(children='Gozo Hawkeye Server',
                style={
                    'textAlign': 'center', 'color' : 'orange'
                }
    ),
    dcc.Interval(id='interval-component', interval=15000, n_intervals=0),
                    
    # Start - High Priority Div        
    html.Div([
        html.H3('High Priority Scraper',
            style={
                    'textAlign': 'left', 'color' : 'red'
                }
        ),
        html.Div(children=
            [   
                html.Div(
                    html.Button('Start', 
                        id='hp-start-button'
                    ),
                    style={'width': '49%', 'height': '100%', 'align': 'left', 'color' : 'blue', 'display': 'inline-block'}
                ),
                html.Div(
                    html.Button('Stop', 
                        id='hp-stop-button'
                    ),
                    style={'width': '49%', 'height': '100%', 'align': 'center', 'color' : 'blue', 'display': 'inline-block'}
                )               
            ]
        ),
        html.Div(children=
            [
                html.Div(children=
                    [
                        html.H5('Poll Dates', style={'textAlign': 'left', 'color' : 'blue'}),
                        dcc.DatePickerRange(
                            id='hp-poll-dates',
                            min_date_allowed=date.today(),
                            max_date_allowed=date.today() + timedelta(90),
                            initial_visible_month=date.today() + timedelta(5),
                            start_date=date.today()  + timedelta(5),
                            end_date=date.today() + timedelta(7)
                        ),
                    ], style={'display': 'inline-block', 'width': '100%'}
                ),
            ]
        ),
        html.Div(children=
            [
                html.Div(children=
                    [
                        html.H5('Spiders Per Batch', style={'textAlign': 'left', 'color' : 'blue'}),
                        dcc.Dropdown(
                            id='hp-batch-size',
                            options=[{'label': i, 'value': i} for i in ['10', '50', '75', '100', '200', '300', '500']],
                            value='10',                      
                        ),                        
                    ], style={'display': 'inline-block', 'width': '24%'}
                ),
                html.Div(children=
                    [
                        html.H5('Poll Frequency', style={'textAlign': 'left', 'color' : 'blue'}),
                        dcc.Dropdown(
                            id='hp-poll-frequency',
                            options=[{'label': i, 'value': i} for i in ['10 minutes', '15 minutes', '30 minutes', '60 minutes', '2 hours', '3 hours', '5 hours', '8 hours', '24 hours']],
                            value='10 minutes',                       
                        ),                        
                    ], style={'display': 'inline-block', 'width': '24%'}
                )
            ]
        ),
        html.H5('Days To Poll', style={'textAlign': 'left', 'width': '49%', 'color' : 'blue'}),
        dcc.Checklist(
            id='hp-select-days',
            options=[{'label': i, 'value': i} for i in ['Mon', 'Tue', 'Wed', 'Thur', 'Fri', 'Sat', 'Sun',]],
            values=['Mon', 'Tue', 'Wed', 'Thur', 'Fri', 'Sat', 'Sun',],
        ),
        html.H5('Vendors to Poll', style={'textAlign': 'left', 'width': '49%', 'color' : 'blue'}),
        dcc.Checklist(
            id='hp-select-vendors',
            options=[{'label': i, 'value': i} for i in ['MakeMyTrip', 'AhaTaxis', 'Wiwigo', 'Onewaycab', 'MyTaxiIndia','GetMeCab','HippoCabs',]],
            #values=['MakeMyTrip', 'AhaTaxis', 'Wiwigo', 'Onewaycab', 'MyTaxiIndia','GetMeCab','HippoCabs',],
            values=['HippoCabs',],
        ),
        html.Button('Refresh', id='hp-refresh-stats',
            style={
                'align': 'center', 'color' : 'blue', 'display': 'inline-block'
            }
        ),
        dcc.Graph(
            id='hp-graph'
        ),
        html.Div(id='hp-intermediate-value', style={'display': 'none'}),
        html.Div(id='hp-intermediate-start', style={'display': 'none'}),
        html.Div(id='hp-intermediate-stop', style={'display': 'none'}),
        html.Div('HIGH_PRIORITY', id='hp-session-id', style={'display': 'none'}),
        ],
        style={'width': '33%', 'display': 'inline-block'}
    ),
    # End - High Priority Div
    
    # Start - Moderate Priority Div
    html.Div([
        html.H3('Moderate Priority Scraper',
            style={
                    'textAlign': 'left', 'color' : 'red'
                }
        ),
        html.Div(children=
            [   
                html.Div(
                    html.Button('Start', 
                        id='mp-start-button'
                    ),
                    style={'width': '49%', 'height': '100%', 'align': 'left', 'color' : 'blue', 'display': 'inline-block'}
                ),
                html.Div(
                    html.Button('Stop', 
                        id='mp-stop-button'
                    ),
                    style={'width': '49%', 'height': '100%', 'align': 'center', 'color' : 'blue', 'display': 'inline-block'}
                )               
            ]
        ),
        html.Div(children=
            [
                html.Div(children=
                    [
                        html.H5('Poll Dates', style={'textAlign': 'left', 'width': '49%', 'color' : 'blue'}),
                        dcc.DatePickerRange(
                            id='mp-poll-dates',
                            min_date_allowed=date.today(),
                            max_date_allowed=date.today() + timedelta(90),
                            initial_visible_month=date.today() + timedelta(5),
                            start_date=date.today(),
                            end_date=date.today() + timedelta(14)
                        ),
                    ], style={'display': 'inline-block', 'width': '100%'}
                ),
            ]
        ),
        html.Div(children=
            [
                html.Div(children=
                    [
                        html.H5('Spiders Per Batch', style={'textAlign': 'left', 'color' : 'blue'}),
                        dcc.Dropdown(
                            id='mp-batch-size',
                            options=[{'label': i, 'value': i} for i in ['10', '50', '75', '100', '200', '300', '500']],
                            value='10',                      
                        ),                        
                    ], style={'display': 'inline-block', 'width': '24%'}
                ),
                html.Div(children=
                    [
                        html.H5('Poll Frequency', style={'textAlign': 'left', 'color' : 'blue'}),
                        dcc.Dropdown(
                            id='mp-poll-frequency',
                            options=[{'label': i, 'value': i} for i in [ '10 minutes', '15 minutes', '30 minutes', '60 minutes', '2 hours', '3 hours', '5 hours', '8 hours', '24 hours']],
                            value='15 minutes',                       
                        ),                        
                    ], style={'display': 'inline-block', 'width': '24%'}
                )
            ]
        ),
        html.H5('Days To Poll', style={'textAlign': 'left', 'width': '49%', 'color' : 'blue'}),
        dcc.Checklist(
            id='mp-select-days',
            options=[{'label': i, 'value': i} for i in ['Mon', 'Tue', 'Wed', 'Thur', 'Fri', 'Sat', 'Sun']],
            values=['Wed', 'Sat'],
        ),
        html.H5('Vendors to Poll', style={'textAlign': 'left', 'width': '49%', 'color' : 'blue'}),
        dcc.Checklist(
            id='mp-select-vendors',
            options=[{'label': i, 'value': i} for i in ['MakeMyTrip', 'AhaTaxis', 'Wiwigo', 'Onewaycab', 'MyTaxiIndia','GetMeCab','HippoCabs',]],
            values=['MakeMyTrip', 'AhaTaxis', 'Wiwigo', 'Onewaycab', 'MyTaxiIndia','GetMeCab','HippoCabs',],
        ),
        html.Button('Refresh', id='mp-refresh-stats',
            style={
                'align': 'center', 'color' : 'blue', 'display': 'inline-block'
            }
        ),
        dcc.Graph(
            id='mp-graph'
        ),
        html.Div(id='mp-intermediate-value', style={'display': 'none'}),
        html.Div(id='mp-intermediate-start', style={'display': 'none'}),
        html.Div(id='mp-intermediate-stop', style={'display': 'none'}),
        html.Div('MODERATE_PRIORITY', id='mp-session-id', style={'display': 'none'}),
        ], 
        style={'width': '33%', 'display': 'inline-block'}
    ),  
    # End - Moderate Priority Div

    # Start - Low Priority Div
    html.Div([
        html.H3('Low Priority Scraper',
            style={
                    'textAlign': 'left', 'color' : 'red'
                }
        ),
        html.Div(children=
            [   
                html.Div(
                    html.Button('Start', 
                        id='lp-start-button'
                    ),
                    style={'width': '49%', 'height': '100%', 'align': 'left', 'color' : 'blue', 'display': 'inline-block'}
                ),
                html.Div(
                    html.Button('Stop', 
                        id='lp-stop-button'
                    ),
                    style={'width': '49%', 'height': '100%', 'align': 'center', 'color' : 'blue', 'display': 'inline-block'}
                )               
            ]
        ),
        html.Div(children=
            [
                html.Div(children=
                    [
                        html.H5('Poll Dates', style={'textAlign': 'left', 'width': '49%', 'color' : 'blue'}),
                        dcc.DatePickerRange(
                            id='lp-poll-dates',
                            min_date_allowed=date.today(),
                            max_date_allowed=date.today() + timedelta(90),
                            initial_visible_month=date.today() + timedelta(5),
                            start_date=date.today(),
                            end_date=date.today() + timedelta(14)
                        ),
                    ], style={'display': 'inline-block', 'width': '100%'}
                ),
            ]
        ),
        html.Div(children=
            [
                html.Div(children=
                    [
                        html.H5('Spiders Per Batch', style={'textAlign': 'left', 'color' : 'blue'}),
                        dcc.Dropdown(
                            id='lp-batch-size',
                            options=[{'label': i, 'value': i} for i in ['10', '25', '50', '75', '100', '200', '300', '500']],
                            value='10',                      
                        ),                        
                    ], style={'display': 'inline-block', 'width': '24%'}
                ),
                html.Div(children=
                    [
                        html.H5('Poll Frequency', style={'textAlign': 'left', 'color' : 'blue'}),
                        dcc.Dropdown(
                            id='lp-poll-frequency',
                            options=[{'label': i, 'value': i} for i in ['10 minutes', '15 minutes', '30 minutes', '60 minutes', '2 hours', '3 hours', '5 hours', '8 hours', '24 hours']],
                            value='30 minutes',                       
                        ),                        
                    ], style={'display': 'inline-block', 'width': '24%'}
                )
            ]
        ),
        html.H5('Days To Poll', style={'textAlign': 'left', 'width': '49%', 'color' : 'blue'}),
        dcc.Checklist(
            id='lp-select-days',
            options=[{'label': i, 'value': i} for i in ['Mon', 'Tue', 'Wed', 'Thur', 'Fri', 'Sat', 'Sun']],
            values=['Sat'],
        ),
        html.H5('Vendors to Poll', style={'textAlign': 'left', 'width': '49%', 'color' : 'blue'}),
        dcc.Checklist(
            id='lp-select-vendors',
            options=[{'label': i, 'value': i} for i in ['MakeMyTrip', 'AhaTaxis', 'Wiwigo', 'Onewaycab', 'MyTaxiIndia','GetMeCab','HippoCabs',]],
            values=['MakeMyTrip', 'AhaTaxis', 'Wiwigo', 'Onewaycab', 'MyTaxiIndia','GetMeCab','HippoCabs',],
        ),
        html.Button('Refresh', id='lp-refresh-stats',
            style={
                'align': 'center', 'color' : 'blue', 'display': 'inline-block'
            }
        ),
        dcc.Graph(
            id='lp-graph'
        ),
        html.Div(id='lp-intermediate-value', style={'display': 'none'}),
        html.Div(id='lp-intermediate-start', style={'display': 'none'}),
        html.Div(id='lp-intermediate-stop', style={'display': 'none'}),
        html.Div('LOW_PRIORITY', id='lp-session-id', style={'display': 'none'}),
        ],
        style={'width': '33%', 'display': 'inline-block', 'float': 'right'},
    ),
    ]
    # End - Low Priority Div
)


# HIGH PRIORITY CALLBACK - START
@app.callback(
    dash.dependencies.Output('hp-intermediate-value', 'children'),
    [
        dash.dependencies.Input('hp-session-id', 'children'),
        dash.dependencies.Input('hp-poll-dates', 'start_date'),
        dash.dependencies.Input('hp-poll-dates', 'end_date'),
        dash.dependencies.Input('hp-batch-size', 'value'),
        dash.dependencies.Input('hp-poll-frequency', 'value'),
        dash.dependencies.Input('hp-select-days', 'values'),
        dash.dependencies.Input('hp-select-vendors', 'values'),
    ])
def hp_update_controls(
                    in_scheduler_id,                    
                    in_poll_dates_start,
                    in_poll_dates_end,
                    in_batch_size,
                    in_poll_frequency,
                    in_select_days,
                    in_select_vendors
                    ):
    return common_update_controls(
                    in_scheduler_id,                    
                    in_poll_dates_start,
                    in_poll_dates_end,
                    in_batch_size,
                    in_poll_frequency,
                    in_select_days,
                    in_select_vendors
                    )
    
@app.callback(
    dash.dependencies.Output('hp-intermediate-start', 'children'),
    [
        dash.dependencies.Input('hp-session-id', 'children'),
        dash.dependencies.Input('hp-start-button', 'n_clicks'),
    ]
)
def hp_start(in_scheduler_id, n_clicks):
    return common_start(in_scheduler_id, n_clicks)
    
@app.callback(
    dash.dependencies.Output('hp-intermediate-stop', 'children'),
    [
        dash.dependencies.Input('hp-session-id', 'children'),
        dash.dependencies.Input('hp-stop-button', 'n_clicks'),
    ]
)
def hp_stop(in_scheduler_id, n_clicks):
    return common_stop(in_scheduler_id, n_clicks)

@app.callback(
    dash.dependencies.Output('hp-graph', 'figure'),
    [
        dash.dependencies.Input('interval-component', 'n_intervals'),
        dash.dependencies.Input('hp-refresh-stats', 'n_clicks'),
    ]
)
def hp_update_graph(n_intervals, n_clicks):
    return common_update_graph('HIGH_PRIORITY')
    
# HIGH PRIORITY CALLBACK - END



# MODERATE PRIORITY CALLBACK - START
@app.callback(
    dash.dependencies.Output('mp-intermediate-value', 'children'),
    [
        dash.dependencies.Input('mp-session-id', 'children'),
        dash.dependencies.Input('mp-poll-dates', 'start_date'),
        dash.dependencies.Input('mp-poll-dates', 'end_date'),
        dash.dependencies.Input('mp-batch-size', 'value'),
        dash.dependencies.Input('mp-poll-frequency', 'value'),
        dash.dependencies.Input('mp-select-days', 'values'),
        dash.dependencies.Input('mp-select-vendors', 'values'),
    ])
def mp_update_controls(
                    in_scheduler_id,                    
                    in_poll_dates_start,
                    in_poll_dates_end,
                    in_batch_size,
                    in_poll_frequency,
                    in_select_days,
                    in_select_vendors
                    ):
    return common_update_controls(
                    in_scheduler_id,                    
                    in_poll_dates_start,
                    in_poll_dates_end,
                    in_batch_size,
                    in_poll_frequency,
                    in_select_days,
                    in_select_vendors
                    )
    
@app.callback(
    dash.dependencies.Output('mp-intermediate-start', 'children'),
    [
        dash.dependencies.Input('mp-session-id', 'children'),
        dash.dependencies.Input('mp-start-button', 'n_clicks'),
    ]
)
def mp_start(in_scheduler_id, n_clicks):
    return common_start(in_scheduler_id, n_clicks)

@app.callback(
    dash.dependencies.Output('mp-intermediate-stop', 'children'),
    [
        dash.dependencies.Input('mp-session-id', 'children'),
        dash.dependencies.Input('mp-stop-button', 'n_clicks'),
    ]
)
def mp_stop(in_scheduler_id, n_clicks):
    return common_stop(in_scheduler_id, n_clicks)

@app.callback(
    dash.dependencies.Output('mp-graph', 'figure'),
    [
        dash.dependencies.Input('interval-component', 'n_intervals'),
        dash.dependencies.Input('mp-refresh-stats', 'n_clicks'),
    ]
)
def mp_update_graph(n_intervals, n_clicks):
    return common_update_graph('MODERATE_PRIORITY')

# MODERATE PRIORITY CALLBACK - END


# LOW PRIORITY CALLBACK - START
@app.callback(
    dash.dependencies.Output('lp-intermediate-value', 'children'),
    [
        dash.dependencies.Input('lp-session-id', 'children'),
        dash.dependencies.Input('lp-poll-dates', 'start_date'),
        dash.dependencies.Input('lp-poll-dates', 'end_date'),
        dash.dependencies.Input('lp-batch-size', 'value'),
        dash.dependencies.Input('lp-poll-frequency', 'value'),
        dash.dependencies.Input('lp-select-days', 'values'),
        dash.dependencies.Input('lp-select-vendors', 'values'),
    ])
def lp_update_controls(
                    in_scheduler_id,                    
                    in_poll_dates_start,
                    in_poll_dates_end,
                    in_batch_size,
                    in_poll_frequency,
                    in_select_days,
                    in_select_vendors
                    ):
    return common_update_controls(
                    in_scheduler_id,                    
                    in_poll_dates_start,
                    in_poll_dates_end,
                    in_batch_size,
                    in_poll_frequency,
                    in_select_days,
                    in_select_vendors
                    )
    
@app.callback(
    dash.dependencies.Output('lp-intermediate-start', 'children'),
    [
        dash.dependencies.Input('lp-session-id', 'children'),
        dash.dependencies.Input('lp-start-button', 'n_clicks'),
    ]
)
def lp_start(in_scheduler_id, n_clicks):
    return common_start(in_scheduler_id, n_clicks)
    
@app.callback(
    dash.dependencies.Output('lp-intermediate-stop', 'children'),
    [
        dash.dependencies.Input('lp-session-id', 'children'),
        dash.dependencies.Input('lp-stop-button', 'n_clicks'),
    ]
)
def lp_stop(in_scheduler_id, n_clicks):
    return common_stop(in_scheduler_id, n_clicks)


@app.callback(
    dash.dependencies.Output('lp-graph', 'figure'),
    [
        dash.dependencies.Input('interval-component', 'n_intervals'),
        dash.dependencies.Input('lp-refresh-stats', 'n_clicks'),
    ]
)
def lp_update_graph(n_intervals, n_clicks):
    return common_update_graph('LOW_PRIORITY')

# LOW PRIORITY CALLBACK - END



# COMMON FUNCTIONS - START
    
def common_update_controls(
                    in_scheduler_id,                    
                    in_poll_dates_start,
                    in_poll_dates_end,
                    in_batch_size,
                    in_poll_frequency,
                    in_select_days,
                    in_select_vendors
                    ):
    _controls_to_json = json.dumps(
        {
            'in_scheduler_id'       : in_scheduler_id,
            'in_poll_dates_start'   : in_poll_dates_start,
            'in_poll_dates_end'     : in_poll_dates_end, 
            'in_batch_size'         : in_batch_size,
            'in_poll_frequency'     : in_poll_frequency,
            'in_select_days'        : in_select_days,
            'in_select_vendors'     : in_select_vendors
        }
    )
    print_x('RunServer::.common_update_controls(%s): _json_data = %s' % (in_scheduler_id, _controls_to_json))
    logging.log(logging.INFO, 'RunServer::.common_update_controls(%s): _json_data = %s' % (in_scheduler_id, _controls_to_json))
    global_session_dict[in_scheduler_id] = _controls_to_json
    return _controls_to_json

def common_start(in_scheduler_id, n_clicks):
    logging.log(logging.INFO, "RunServer::common_start(%s): Enter" % in_scheduler_id)   
    _json_data = global_session_dict[in_scheduler_id]
    if _json_data == None or _json_data == '':
        logging.log(logging.INFO, "RunServer::common_start(%s): controls date not initialized" % in_scheduler_id)
        return
        
    print_x(_json_data)
    logging.log(logging.INFO, "RunServer::common_start(%s): Executing" % in_scheduler_id)
    
    scheduler = HawkeyeScheduler(in_scheduler_id, 'START', json.loads(_json_data))
    scheduler.start()
    
    #run_all.run()
    logging.log(logging.INFO, "RunServer::common_start(%s): Exit" % in_scheduler_id)

    
def common_stop(in_scheduler_id, n_clicks):
    logging.log(logging.INFO, "RunServer::common_stop(%s): Enter" % in_scheduler_id)   
    _json_data = global_session_dict[in_scheduler_id]
    if _json_data == None or _json_data == '':
        logging.log(logging.INFO, "RunServer::common_stop(%s): controls date not initialized" % in_scheduler_id)
        return
        
    print_x(_json_data)
    
    logging.log(logging.INFO, "RunServer::common_stop(%s): Executing"  % in_scheduler_id)
    
    scheduler = HawkeyeScheduler(in_scheduler_id, 'STOP', json.loads(_json_data))
    scheduler.stop()
       
    logging.log(logging.INFO, "RunServer::common_stop(%s): Exit"  % in_scheduler_id)

def common_update_graph(in_scheduler_id):

    print_x('RunServer::.hp_update_graph(*****): Enter - Mode = %s' % in_scheduler_id)
    logging.log(logging.DEBUG, 'RunServer::.hp_update_graph(*****): Enter - Mode = %s' % in_scheduler_id)
    
    data = []
    
    hawkeyetaskdata = HawkeyeTasks().Instance.get(in_scheduler_id)
    if hawkeyetaskdata != None and len(hawkeyetaskdata._progress_data) != 0:
        for vendor, progress in hawkeyetaskdata._progress_data.items():
            total = go.Bar(
                        x=[vendor + ' Total'],
                        y=[progress._total],
                        name=vendor + ' Total',
                        marker=go.Marker(
                            color='rgb(55, 83, 109)'
                        )
                    )
            pending = go.Bar(
                        x=[vendor + ' Pending'],
                        y=[progress._pending],
                        name=vendor + ' Pending',
                        marker=go.Marker(
                            color='rgb(255,165,0)'
                        )
                    )
            successful = go.Bar(
                        x=[vendor + ' Successful'],
                        y=[progress._successful],
                        name=vendor + ' Successful',
                        marker=go.Marker(
                            color='rgb(0,128,0)'
                        )
                    )
            error = go.Bar(
                        x=[vendor + ' Error'],
                        y=[progress._error],
                        name=vendor + ' Error',
                        marker=go.Marker(
                            color='rgb(255,69,0)'
                        )
                    )
            
            data.append(total)
            data.append(pending)
            data.append(successful)
            data.append(error)
    else:
        print_x('RunServer::.hp_update_graph(*****): Exit (None) - Mode = %s' % in_scheduler_id)
        logging.log(logging.DEBUG, 'RunServer::.hp_update_graph(*****): Exit (None) - Mode = %s' % in_scheduler_id)
    
    figure=go.Figure(
        data,
        layout=go.Layout(
            title='Spyder Progress',
            showlegend=False,
        )
    )
    print_x('RunServer::.hp_update_graph(*****): Exit - Mode = %s' % in_scheduler_id)
    logging.log(logging.DEBUG, 'RunServer::.hp_update_graph(*****): Exit - Mode = %s' % in_scheduler_id)
    return figure

def initialize_logger():
    print ("Inside initialize_logger()")
    curr_date_time = datetime.now()
    
    if not os.path.exists('.\\logs\\'):
        os.makedirs('.\\logs\\')
    log_file = '.\\logs\\' + 'log-' + str(curr_date_time.strftime('%Y_%m_%d_%H_%M_%S')) + '.log' 
    handler = RotatingFileHandler(log_file, maxBytes=10000000, backupCount=25)
    handler.setLevel(logging.INFO)
    app.server.logger.addHandler(handler)

# COMMON FUNCTIONS - END

def print_x(msg):
    #print(msg)
    pass
if __name__ == '__main__':
    initialize_logger()
    app.run_server(debug=True, host='127.0.0.1', port=8052)
    
    

