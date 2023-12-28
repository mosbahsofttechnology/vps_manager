import json
import sqlite3
import mysql.connector

mydb = mysql.connector.connect(
  host="37.152.182.34",
  user="manager",
  password="nazari@0794054171@As",
  database="lhs"
)

dburl = "/etc/x-ui/x-ui.db"
# dburl = "x-ui.db"

  
sql = f"SELECT * FROM client_traffics WHERE `enable` = 1"
# run query
conn = sqlite3.connect(dburl)
c = conn.cursor()
c.execute(sql)
 
def find_id_with_email(email):
  sql = f"SELECT settings,id  FROM inbounds WHERE `settings`  LIKE  '%{email}%' LIMIT 1"
  conn = sqlite3.connect(dburl)
  # run 
  c = conn.cursor()
  c.execute(sql)
#   return main_data[0][0]
  main_data  =  c.fetchall()
  if len(main_data) == 0:
      return None
  clients = json.loads(main_data[0][0])
  inbound_id =  main_data[0][1]

  for client in clients['clients']:
    if client['email'] == str(email):
      return  client['id']

mycursor = mydb.cursor()

# show data 
main_data  = c.fetchall()
for  i in main_data:
  email = i[3]
  up = i[4]
  down = i[5]
  id = (find_id_with_email(email))
  if id != None :   
     mycursor.execute(f"SELECT * FROM tbl_user_usages WHERE `email` = '{email}' AND `user_id` = '{id}'")
     myresult = mycursor.fetchall()
     
     if len(myresult) == 0:
        mycursor.execute(f"INSERT INTO tbl_user_usages (email, user_id, up, down) VALUES ('{email}', '{id}', '{up}', '{down}')")
        mydb.commit()
     else:
        mycursor.execute(f"UPDATE tbl_user_usages SET up = '{up}', down = '{down}' WHERE email = '{up}' AND user_id = '{id}'")
        mydb.commit()
conn.close()




