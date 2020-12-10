import mysql.connector

##################################################
# DATABASE
mydb = mysql.connector.connect(
  host="localhost",
  port="3306",
  user="root",
  password="password"
)

mycursor = mydb.cursor()

try:
	mycursor.execute("CREATE DATABASE mydatabase")
except:
	print("failed to make new base")

mycursor.execute("SHOW DATABASES")

for x in mycursor:
  print(x)
##################################################
# TABLES
mydb = mysql.connector.connect(
  host="localhost",
  port="3306",
  user="root",
  password="password",
  database="mydatabase"
)
mycursor = mydb.cursor()
try:
	mycursor.execute("CREATE TABLE customers (name VARCHAR(255), address VARCHAR(255))")
except:
	mycursor.execute("TRUNCATE TABLE customers")

mycursor.execute("SHOW TABLES")

print("Tables:")
for x in mycursor:
  print(x)
######################################################
# INSERT
sql = "INSERT INTO customers (name, address) VALUES (%s, %s)"
val = ("John", "tx")
mycursor.execute(sql, val)

sql = "INSERT INTO customers (name, address) VALUES (%s, %s)"
val = [
  ('Peter', 'az'),
  ('Amy', 'il'),
  ('Hannah', 'mt'),
  ('Michael', 'ca'),
  ('Sandy', 'ny'),
  ('Betty', 'ny'),
  ('Richard', 'pa'),
  ('Susan', 'or'),
  ('Vicky', 'tx'),
  ('Ben', 'tx'),
  ('William', 'tx'),
  ('Chuck', 'il'),
  ('Viola', 'ca'),
  ('Amy', 'il')
]

mycursor.executemany(sql, val)
##########################################################
# SELECT
mycursor.execute("SELECT * FROM customers")

myresult = mycursor.fetchall()

print("Customers:")
for x in myresult:
  print(x)

##########################################################
# SELECT DISTICT
mycursor.execute("SELECT DISTINCT address FROM customers")

myresult = mycursor.fetchall()

print("Customers:")
for x in myresult:
  print(x)

##########################################################
# SELECT SET
mycursor.execute("SELECT * FROM customers WHERE address IN (\"tx\", \"az\")")

myresult = mycursor.fetchall()

print("Customers:")
for x in myresult:
  print(x)

mydb.commit()

mydb.close()