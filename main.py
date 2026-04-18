import psycopg2

# connection
conn = psycopg2.connect(
    dbname="postgres",
    user="postgres",
    password="adikadikadik777",
    host="localhost",
    port="5432"
)

cur = conn.cursor()

# query
cur.execute("SELECT * FROM phonebook")

# fetch rows
rows = cur.fetchall()

# print table
for row in rows:
    print(row)

# close
cur.close()
conn.close()