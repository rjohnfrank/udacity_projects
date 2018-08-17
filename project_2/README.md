# Wrangle OpenStreetMap Data

Here are the descriptions of all the files used in this project, in logical order: 

wrangle_openstreetmap_data.html = the main document 
map_description.txt = the details of the OSM area chosen 
/osm_files/ = the directory that contains the OSM XML files (the original and the sample)
sample.py = the code for converting the original OSM XML file to the sample file
audit.py = the python code used for auditing the data 
data.py = the code used for cleaning the data 
/csv_files/ = these csv files were created using the data.py code 
csv_to_db.py = the code to convert the csv files to a db file for use with SQLite 
schema.py = the SQL schema used to create the db file 
philly.db = the data file for the SQL queries 
calc_file_sizes.py = to calculate the sizes of all of the data files in the project 
sql_queries.py = the collection of the SQL queries performed 
edits_per_user.png = an image file that illustrates one the SQL query results
references.txt = a list of the external sources used for this project 

