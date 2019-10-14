import dash
import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objs as go
import json

import psycopg2 #postgres connection lib


app = dash.Dash(__name__,)

styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}

# Plotly mapbox public token
mapbox_access_token = "pk.eyJ1IjoicGxvdGx5bWFwYm94IiwiYSI6ImNqdnBvNDMyaTAxYzkzeW5ubWdpZ2VjbmMifQ.TXcBE-xg9BFdV2ocecc_7g"

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

list_of_energies = {
	"CSP", "PV", "Wind",
}

try:
	#connect to server
	conn = psycopg2.connect(host="localhost", port="5432", database="mapre", user="Anaavu", password="")
	#create cursor to execute SQL commands
	cur = conn.cursor()
	#the SQL query to execute
	cur.execute('SELECT version()')
	#retrieve query result
	db_version = cur.fetchone()
	print(db_version)

except (Exception, psycopg2.Error) as error :
    print ("Error while connecting to PostgreSQL", error)


cur.execute(' SELECT ST_AsGeoJSON(ST_Transform(geom, 4326)), lt_tra FROM public."angola_pv_shp"; ')
geometry = cur.fetchall()
print(geometry[0])
json1 = json.loads(geometry[0][0])


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
    dcc.Graph(
    	id='map',
    	figure=go.Figure(
			data=[{
			    'type' : 'choropleth',
			    'locations' : json1["coordinates"][0],
                #'z' : geometry[0][1],
			    'marker' : dict(
                    line=dict(
                        width=10,
                        color='rgba(102, 102, 102)')
                    ),
			}],
			layout=go.Layout(
			    {
                'autosize' : True,
			    'clickmode' : 'event+select',
			    'title' : 'coordinates',
			    'showlegend' : True,
			    'legend' : go.layout.Legend(
			            x=0,
			            y=1.0
			        ),
                'geo' : go.layout.Geo(
                    center=dict(
                        lon=json1['coordinates'][0][0][0][0],
                        lat=json1['coordinates'][0][0][0][0],
                        ),
                    projection=dict(
                        scale=15),
                    showcountries=True

                    ),
			        'margin' : go.layout.Margin(l=40, r=0, t=40, b=30),
                'mapbox' : dict(
                    #zoom=12
                    )
			    } ),
			    ##style={}
		)
    ),
    # dcc.Graph(
    # 	id='map',
    # 	figure=go.Figure(
    # 		data=[{
    #         type='scattergeo',
    #         lat=geometry[0][0]["coordinates"],
    #         lon=geometry[0][0]["coordinates"],
    #         marker = dict(size = 8, opacity = 0.5),
    #     }],
    #     layout=go.Layout(
    #     	{
    #     	#clickmode='event+select',
    #         title='US Export of Plastic Scrap',
    #         showlegend=True,
    #         legend=go.layout.Legend(
    #             x=0,
    #             y=1.0
    #         ),
    #         margin=go.layout.Margin(l=40, r=0, t=40, b=30)
    #     } ),
    #     style={}
    # 		)
    # 	),

    html.Iframe(id='anal', srcDoc=open("angola_analysis.html", "r").read(),
    	style={'display': 'inline-block', 'width': '100%', 'height': '800px'}),
],
)

if __name__ == '__main__':
    app.run_server(port=8080, debug=True)
#
#you'll just intro dcc.graphs in layout and callback map+graph based on dropdown and callback chart based on map clickdata
