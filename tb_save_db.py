## Total is Generation (copy)
import time
import psycopg2 #postgres connection lib

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

	#open the log file to start parsing it
	file = open("/Users/Anaavu/Documents/My Tableau Repository/Logs/log.txt","w+")
	last = "No lines in file"
	while True:
		line = file.readline()
		if not line: #if no new lines, wait until there is one
			time.sleep(0.01)
			continue
		if "set-parameter-value" in line and "value-string" in line: #if line refers to a new parameter input
			print(line)
			datetime = line.split("ts",1)[1][3:26] #grab timestamp
			parameter = line.split("global-field-name=",1)[1][16:47] #grab which parameter changed
			value = line.split("value-string=",1)[1][2:5] #grab new value
			print(datetime, parameter, value) #the value to save
			postgres_insert_query = """ INSERT INTO public."Parameters_save_Angola_PV" ("Timestamp", "Parameter", "Value") VALUES (%s,%s,%s)"""
			record_to_insert = (datetime, parameter, value)
			cur.execute(postgres_insert_query, record_to_insert)
			conn.commit()
			count = cur.rowcount
			print (count, "Record inserted successfully into mobile table")
		last = line

	print(last) 
	file.close()

except (Exception, psycopg2.Error) as error :
    print ("Error while connecting to PostgreSQL", error)


