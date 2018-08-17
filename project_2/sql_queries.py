###
###
### sql_queries.py
###
###


###
###
### SQL Queries, Part 1: Describing Users
###
###


import sqlite3
import pprint
import pandas as pd
import numpy as np

%matplotlib inline
import matplotlib.pyplot as plt
import seaborn as sns


# select the file 
sqlite_file = "./philly.db" 
# connect to the db 
conn = sqlite3.connect(sqlite_file) 
# get a cursor object 
cur = conn.cursor() 


# THE DISTINCT NUMBER OF USERS QUERY 
query1a = "\
SELECT COUNT(DISTINCT(combo.uid)) \
FROM (SELECT uid FROM nodes UNION ALL SELECT uid FROM ways) AS combo \
;"


# execute the query 
cur.execute(query1a)
# collect the output 
all_rows = cur.fetchall()
# convert the output to a Pandas Dataframe 
users_df = pd.DataFrame(all_rows)
users_df.columns = ['DISTINCT NUMBER OF USERS']
# print the output
pprint.pprint(users_df)


# NUMBER OF USERS WITH ONLY ONE POST 
query1b = "\
SELECT COUNT(*) AS one_post \
FROM \
(SELECT combo.user AS user, COUNT(*) AS num \
FROM (SELECT user FROM nodes UNION ALL SELECT user FROM ways) AS combo \
GROUP BY combo.user) \
WHERE num = 1 \
;"


# execute the query
cur.execute(query1b)
# collect the output 
all_rows = cur.fetchall()
# convert the output to a Pandas Dataframe 
users_df = pd.DataFrame(all_rows)
users_df.columns = ['USERS WITH ONE POST']
# print the output
pprint.pprint(users_df)


# top 10 users
query1c = "\
SELECT combo.user AS users, COUNT(combo.user) AS edits \
FROM (SELECT user FROM nodes UNION ALL SELECT user FROM ways) AS combo \
GROUP BY users \
ORDER BY edits DESC \
LIMIT 10 \
;"


# execute the query
cur.execute(query1c)
# collect the output 
all_rows = cur.fetchall()
# convert the output to a Pandas Dataframe 
users_df = pd.DataFrame(all_rows)
users_df.columns = ['USER', 'EDITS']
# print the output
pprint.pprint(users_df)


# describe users 
query1d = "\
SELECT combo.user, count(*) AS edits \
FROM (SELECT user FROM nodes UNION ALL SELECT user FROM ways) AS combo \
GROUP BY combo.user \
ORDER BY edits DESC \
;"


# execute the query
cur.execute(query1d)
# collect the output 
all_rows = cur.fetchall()
# convert the output to a Pandas Dataframe 
users_df = pd.DataFrame(all_rows)
users_df.columns = ['USERS', 'EDITS']
pprint.pprint(users_df.describe())


def graph_dependent_variable_data(df, dependent_variable, start_graph_range, end_graph_range, step_size):
    plt.figure(figsize=(12,6))
    plt.ylabel("Frequency")
    plt.xlabel("Number of Edits Per User") 
    plt.title("Distribution of the Number of Edits")
    # set the x-axis based on the function inputs 
    plt.xlim(start_graph_range, end_graph_range)
    bins = np.arange(start_graph_range, 
                     end_graph_range, 
                     step = step_size)
    # drop the NaN values before
    plt.hist(df[dependent_variable].dropna(), bins=bins, alpha=.5)
    # set the ticks relative to step_size 
    plt.xticks(range(start_graph_range, end_graph_range, step_size*5))
    plt.show()
dependent_variable = 'EDITS'
graph_dependent_variable_data(users_df, dependent_variable, 0, 100, 2)



###
###
### SQL Queries, Part 2: Finding Vegan Options
###
###



# all vegan instances
query2a = "\
SELECT combo.key, combo.value, COUNT(*) as num \
FROM (SELECT id, key, value FROM nodes_tags UNION ALL SELECT id, key, value FROM ways_tags) AS combo \
WHERE ((combo.key LIKE '%vegan%') OR (combo.value LIKE '%vegan%'))\
GROUP BY combo.key, combo.value \
ORDER BY num DESC \
;"

# execute the query 
cur.execute(query2a)
# collect the output 
all_rows = cur.fetchall()
# convert the output to a Pandas Dataframe 
vegan_df = pd.DataFrame(all_rows)
vegan_df.columns = ['KEY', 'VALUE', 'INSTANCES']
pprint.pprint(vegan_df)



# vegan tag overlap 
query2b = "\
SELECT combo.id, combo.key, combo.value, COUNT(*) as num \
FROM (SELECT id, key, value FROM nodes_tags UNION ALL SELECT id, key, value FROM ways_tags) AS combo \
WHERE (combo.key = 'vegan') \
GROUP BY combo.id \
ORDER BY num DESC \
;"

# execute the query 
cur.execute(query2b)
# collect the output 
all_rows = cur.fetchall()
# convert the output to a Pandas Dataframe 
vegan_df = pd.DataFrame(all_rows)
vegan_df.columns = ['ID','KEY', 'VALUE', 'INSTANCES']
pprint.pprint(vegan_df)



# searching for missing vegan tags 
query2c = "\
SELECT combo.id, combo.key, combo.value, COUNT(*) as num \
FROM (SELECT id, key, value FROM nodes_tags UNION ALL SELECT id, key, value FROM ways_tags) AS combo \
WHERE ((combo.key LIKE '%vegan%') OR (combo.value LIKE '%vegan%')) \
GROUP BY combo.id \
ORDER BY num DESC \
;"

# execute the query 
cur.execute(query2c)
# collect the output 
all_rows = cur.fetchall()
# convert the output to a Pandas Dataframe 
vegan_df = pd.DataFrame(all_rows)
vegan_df.columns = ['ID', 'KEY', 'VALUE', 'INSTANCES']
pprint.pprint(vegan_df)
