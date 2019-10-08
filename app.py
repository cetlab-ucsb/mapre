import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


# dictionary items for dropdown
list_of_countries = {
    "Angola": "angola_analysis.html",
    "Botswana": "angola_analysis.html",
    "Burundi": "angola_analysis.html",
    "DRC": "angola_analysis.html",
    "Djibouti": "angola_analysis.html",
    "Egypt": "angola_analysis.html",
    "Ethiopia": "angola_analysis.html",
    "India": "angola_analysis.html",
    "Kenya": "angola_analysis.html",
    "Lesotho": "angola_analysis.html",
    "Libya": "angola_analysis.html",
    "Malawi": "angola_analysis.html",
    "Mozambique": "angola_analysis.html",
    "Namibia": "angola_analysis.html",
    "Rwanda": "angola_analysis.html",
    "South Africa": "angola_analysis.html",
    "Sudan": "angola_analysis.html",
    "Swaziland": "angola_analysis.html", 
    "Tanzania": "angola_analysis.html", 
    "Uganda": "angola_analysis.html", 
    "Zambia": "angola_analysis.html", 
    "Zimbabwe": "angola_analysis.html",
}


app.layout = html.Div([
    html.H2("Analysis",
            style={'textAlign': 'center', 'color': '#7FDBFF'}),
    html.Div(
    	className="div-for-dropdown",
    	children=[
    		# Dropdown for country to explore
    		dcc.Dropdown(
    			id="location-dropdown",
    			options=[
    				{"label": i, "value": i}
    				for i in list_of_countries
    			],
                placeholder="Select a location",
                style={'width': '50%'},
            )
        ],
    ),
    html.Div(id="analy",children=html.Iframe(srcDoc=open("analysis.html", "r").read(),
    	style={'display': 'inline-block', 'width': '100%', 'height': '800px'}),)
],
)


@app.callback(
	Output('analy', 'children'),
	[Input('location-dropdown', 'value')]
)
def update_page(country):
	if country:
		print(country)
		return html.Iframe(srcDoc=open(list_of_countries[country], "r").read(),
			style={'display': 'inline-block', 'width': '100%', 'height': '800px'}),
	else:
		print(4)
		return html.Iframe(srcDoc=open("analysis.html", "r").read(),
			style={'display': 'inline-block', 'width': '100%', 'height': '800px'}),


if __name__ == '__main__':
    app.run_server(port=8020,debug=True)

