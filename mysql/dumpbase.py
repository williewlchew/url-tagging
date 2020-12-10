import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  port="3306",
  user="root",
  password="password",
  database="mydatabase"
)
mycursor = mydb.cursor()

mycursor.execute("SELECT * FROM link_tag")

myresult = mycursor.fetchall()

print("Link-Tags:")
for x in myresult:
  print(x)

print("Tags:")
mycursor.execute("SELECT * FROM tags")

myresult = mycursor.fetchall()

for x in myresult:
  print(x)


print("Links:")
mycursor.execute("SELECT * FROM links")

myresult = mycursor.fetchall()

for x in myresult:
  print(x)

