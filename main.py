import os
from os import path
from datetime import date
from import_dataset import download_json, split_json_to_dfs
from other_functions import millify, clean_directory, find_suffix_filenames

# ----------------------------------------------------------------------------
# Dash
import plotly.express as px
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from plotly.subplots import make_subplots
import plotly.graph_objects as go

# ----------------------------------------------------------------------------
# Chart Studio
import chart_studio

# ----------------------------------------------------------------------------
# Structure
def create_directory(path):
    if not os.path.exists(path):
        os.mkdir(path)
    else:
        print(path + ' already exists!')

create_directory('Datasets')

# ----------------------------------------------------------------------------
# Check for the most current file
today = date.today()
todays_file = 'covid_{}.json'.format(today)
current_filename = 'Datasets/' + todays_file

# Check if the most current file exist
if os.path.isfile(current_filename) == True:
    print('The most current file alread exists. No new file was downloaded')
else:
    download_json()

# Check all files that has .josn extension
check_files = find_suffix_filenames('Datasets/', '.json')
# Clean (remove) older.json file while keeping the most recent one. 
clean_directory(check_files, exclude=[todays_file])

country_information, country_key, combined_df = split_json_to_dfs(current_filename)

# ----------------------------------------------------------------------------
# Replacing Location
combined_df = combined_df.merge(country_key, how='left',left_on='country_code', right_on='index').drop(['country_code', 'index'], axis = 1)
col_reorder = combined_df.columns.to_list()
if 'location' in col_reorder: col_reorder.remove('location')
col_reorder.insert(1, 'location')
combined_df = combined_df[col_reorder]


# ----------------------------------------------------------------------------
# DropDown
drop_option = country_key.copy()
drop_option['value'] = drop_option['location']
drop_option = drop_option.drop(['index','continent'], 1)
drop_option = drop_option.rename(columns = {'location': 'label', 'value': 'value'})
drop_option_list = drop_option.to_dict(orient='records')


# ----------------------------------------------------------------------------
# Dash App

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("COVID-19 DASHBOARD", style = {'text_align' : 'center'}),
    
    html.Div(id = 'output_container', children = []),


    ################# Dropdown
    dcc.Dropdown(id = "select_country",
                 options = drop_option_list,
                 multi=False,
                 value = 'World',
                 style={'width': '40%'}
    
    ),
    
    html.Br(),
    ################# Datacard
    dcc.Graph(id = 'datacard', figure={}),


    ################# Graph
    html.Div(children=[
        dcc.Graph(id = 'total_cases', style={'display': 'inline-block'}),
        dcc.Graph(id = 'cases', style={'display': 'inline-block'}),
        dcc.Graph(id = 'deaths', style={'display': 'inline-block'})
    ])
])

# ----------------------------------------------------------------------------
# Connect Plotly app with Dash Component
@app.callback(
    [Output(component_id = 'cases', component_property= 'figure'),
    Output(component_id='output_container', component_property='children'),
    Output(component_id='deaths', component_property='figure'),
    Output(component_id='total_cases', component_property='figure')],
    [Input(component_id='select_country', component_property= 'value')])
def update_graph(option_select):
    # Output 1 container
    print(option_select)
    container = ["The country chosen by user is: {}".format(option_select)]
    
    # Output 2 graph
    df = combined_df.copy()
    df = df[df['location'] == option_select]
    df['new_cases_MA'] = df['new_cases'].rolling(window = 7).mean()

    height = 350
    width = height * 1.5

    fig = px.line(
        data_frame=df,
        x = 'date',
        y = ['new_cases', 'new_cases_MA'],
        title= 'New Cases in {}'.format(option_select),
        height = height,
        width = width)#,
        #labels= {'new_Cases': 'Daily New Cases', 'new_cases_MA': '7-Day Moving Average'}
    

    fig2 = px.line(
        data_frame=df,
        x = 'date',
        y = 'new_deaths',
        title= 'New Deaths in {}'.format(option_select),
        width = width,
        height = height)
    
    fig3 = px.line(
        data_frame=df,
        x = 'date',
        y = 'total_cases',
        title= 'Total Cases in {}'.format(option_select),
        width = width,
        height = height)

    return fig, container, fig2, fig3

@app.callback(
    Output(component_id='datacard', component_property='figure'),
    [Input(component_id='select_country', component_property= 'value')])
def stat_narrative(option_select):
    df2 = country_information.copy()
    df2 = df2[df2['location'] == option_select]
    country_stat_dict = df2.to_dict('records')[0]

    # Data Card
    fig = go.Figure()
    fig.add_trace(
        go.Indicator(mode = "number",
        value = country_stat_dict['population'],
        #delta = {'position': "top", 'reference': 320},
        domain = {'row': 0, 'column': 0},
        title = {'text': 'Population'}
        ))
    fig.add_trace(
        go.Indicator(mode = "number",
        value = country_stat_dict['median_age'],
        #delta = {'position': "top", 'reference': 320},
        domain = {'row': 0, 'column': 1},
        title = {'text': 'Median Age'}
        ))
    fig.add_trace(
        go.Indicator(mode = "number",
        value = country_stat_dict['life_expectancy'],
        #delta = {'position': "top", 'reference': 320},
        domain = {'row': 0, 'column': 2},
        title = {'text': 'Life Expectancy'}
        ))
    fig.update_layout(
        grid = {'rows': 1, 'columns': 3, 'pattern': "independent"},
        width = 800,
        height = 200)
    
    return fig

# ----------------------------------------------------------------------------
# Connect Plotly app with Dash Component
if __name__ == '__main__':
    app.run_server(debug=True)