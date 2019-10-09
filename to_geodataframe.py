import psycopg2 #postgres connection lib
import geopandas

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


sql = """ SELECT * FROM public."angola_pv_shp" """
df = geopandas.GeoDataFrame.from_postgis(sql, conn)
print(df)
print(type(df))

# alternatives:
# psychopg2.ST_AsGeoJSON
# plpygis
# https://geoalchemy-2.readthedocs.io/en/latest/

cur.execute(' SELECT ST_AsGeoJSON(geom) FROM public."angola_pv_shp" limit 1; ')
geometry = cur.fetchone()
print(geometry)