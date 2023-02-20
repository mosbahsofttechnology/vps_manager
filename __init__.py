import string
from flask import Flask, render_template
import json
import sqlite3
import random
from flask import request
import uuid
import jdatetime
import jsonpickle
import os
import time


app = Flask(__name__)

dburl = "/etc/x-ui-english/x-ui-english.db"
# dburl = "x-ui-english.db"

#generate random email
def randomStringDigits(stringLength=10):
  lettersAndDigits = string.ascii_letters + string.digits
  return ''.join(random.choice(lettersAndDigits) for i in range(stringLength))

def convert_bytes(num):
  for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
    if num < 1024.0:
      return "%3.1f %s" % (num, x)
    num /= 1024.0
    
def stamp_to_persian_date(stamp):
  return jdatetime.date.fromtimestamp(stamp)

  
@app.route('/create', methods=['GET', 'POST'])
def create_user():
    item_count = request.args.get('item_count', default = 1, type = int)
    expire_date_day = request.args.get('expire', default = 30, type = int)
    total_traffics = request.args.get('trafiic', default = 30, type = int)
    inbound_id = request.args.get('inbound_id', default = 1, type = int)
    limit_ip_count = request.args.get('limit_ip_count', default = 1, type = int)
    title = request.args.get('title', default = "Speedoooooooooooooo", type = str)
    baseurl = request.args.get('baseurl', default = "mtn2amn.amnbridge.top", type = str)
   
    
    # connect to db
    conn = sqlite3.connect(dburl)
    
    
    
    # convert expire_date_day to timestamp + 000
    expire_date = ((expire_date_day * 86400) + int(jdatetime.datetime.now().timestamp()) ) * 1000
    
    # convert total_traffics to bytes
    total_traffics = total_traffics * 1024 * 1024 * 1024
    
        
    c = conn.cursor()
    
    # inbound table
    c.execute("SELECT settings,id,stream_settings,port, protocol FROM inbounds WHERE id = ?", (inbound_id,))
    main_data = settings = c.fetchall()
    
    # get all settings
    port = main_data[0][3]
    protocol = main_data[0][4]
    
    # advanced settings
    base_setting= (json.loads(main_data[0][2]))
    network  = base_setting['network']
    
    
    withtls=False
    try:
      servername = base_setting['tlsSettings']['serverName']
      security = base_setting['security']
      withtls = True
    except:
      withtls = False
      
    
      
    
    
    # client_traffics table
    settings = main_data[0][0]
    
    data = json.loads(settings)['clients']
    
    

    result = []
    for i in range(item_count):
      id = str(uuid.uuid1())
      
      email = randomStringDigits(10) + "@x-ui-english.dev"
      c.execute("INSERT INTO client_traffics VALUES (?,?,?,?,?,?,?,?) ", (None, inbound_id, 1, email, 0, 0, expire_date, total_traffics))
     
      
      if withtls:
        newData = data[0].copy()
        newData['id'] = id
        newData['id'] = id
        newData['email'] = email
        newData['limitIp'] = limit_ip_count
        newData['totalGB'] = total_traffics
        newData['expiryTime'] = expire_date
        data.append(newData)
        settings = json.dumps({"clients": data, "decryption": "none", "fallbacks": []})
        result.append("vless://" +
                    id + "@" + baseurl + ':'
                    + str(port) + '?type='+network+'&security=' + security  + '&path=%2F' + '&host=' + servername +  '&sni=' +  servername + 
                    '#'
                    + title)
      else:
        newData = data[0].copy()
        newData['id'] = id
        newData['email'] = email
        newData['limitIp'] = limit_ip_count
        newData['totalGB'] = total_traffics
        newData['expiryTime'] = expire_date
        data.append(newData)
        settings = json.dumps({"clients": data, "disableInsecureEncryption": False})
        result.append("vless://" +  id + "@" + baseurl + ':'  + str(port) + '?type='+network+  '#' + title)
        
        
    c.execute("UPDATE inbounds SET settings = ? WHERE id = ?", (settings, inbound_id))

    conn.commit()
    conn.close()
    
    
    # restart x-ui
    time.sleep(2.0)
    os.system("systemctl restart x-ui")

    return jsonpickle.encode(result)
  
@app.route('/remove', methods=['GET', 'POST'])
def remove_user():
    id = request.args.get('id', type = str)
    
    

    conn = sqlite3.connect(dburl)
    c = conn.cursor()
    
     
    c.execute("SELECT * FROM inbounds WHERE settings LIKE '%"+id+"%'")
    main_data  = c.fetchall()
    
    
    # client_traffics table
    settings =main_data[0][11]
    inbound_id =  main_data[0][0]
    
    data = json.loads(settings)['clients']
    
    email = ""
    # find id in data
    for i in range(len(data)):
      if data[i]['id'] == id:
        email = data[i]['email']
        del data[i]
        break
     
    # update inbounds table
    settings = json.dumps({"clients": data, "decryption": "none", "fallbacks": []})
    c.execute("UPDATE inbounds SET settings = ? WHERE id = ?", (settings, inbound_id))
     
    # delete in client_traffics table
    c.execute("DELETE FROM client_traffics WHERE email = ?", (email,))
    
     
     
    

    conn.commit()
    conn.close()    
    time.sleep(2.0)
    os.system("systemctl restart x-ui")
    return 'a user that email is ' + email + ' has been removed'
  
  
@app.route('/user_item_count', methods=['GET', 'POST'])
def user_item_count():
    conn = sqlite3.connect(dburl)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM client_traffics")
    main_data = c.fetchall()
    conn.close()
    os.system("systemctl restart x-ui")
    return str(main_data[0][0])
    
@app.route('/user_list', methods=['GET', 'POST'])
def user_list():
    conn = sqlite3.connect(dburl)
    c = conn.cursor()
    c.execute("SELECT * FROM client_traffics")
    main_data = c.fetchall()
    
    # just email and expire_date and total_traffics
    result = [] 
    for i in range(len(main_data)):
      result.append({"email": main_data[i][3],"expire_date": stamp_to_persian_date(main_data[i][6]),"total_trafic": convert_bytes(main_data[i][7])})
    
    conn.close()
    time.sleep(2.0)
    os.system("systemctl restart x-ui")
    return str(result)
  
  
@app.route('/change_expire_date', methods=['GET', 'POST'])
def change_expire_date():
    id = request.args.get('id', type = str)
    expire_date_day = request.args.get('expire', default = 30, type = int)
    
    conn = sqlite3.connect(dburl)
    c = conn.cursor()
    
    
    # convert expire_date_day to timestamp
    expire_date = expire_date_day * 86400
    # sum new expire_date with now
    expire_date = expire_date + int(jdatetime.datetime.now().timestamp()) * 1000 
    
    
    
    # update inbounds table
    c.execute("SELECT * FROM inbounds WHERE settings LIKE '%"+id+"%'")
    main_data  = c.fetchall()
         
    settings =main_data[0][11]
    inbound_id =  main_data[0][0]
    
    data = json.loads(settings)['clients']
    
    email = ""
    # find id in data
    for i in range(len(data)):
      if data[i]['id'] == id:
        email = data[i]['email']
        data[i]['expiryTime'] = expire_date
        break

    
        # update inbounds table
    settings = json.dumps({"clients": data, "decryption": "none", "fallbacks": []})
    c.execute("UPDATE inbounds SET settings = ? WHERE id = ?", (settings, inbound_id))


    c.execute("UPDATE client_traffics SET expiry_time = ? WHERE email = ?", (expire_date, email))
    
    conn.commit()
    conn.close()
    time.sleep(2.0)
    os.system("systemctl restart x-ui")
    return 'expire date has been changed'
  
@app.route('/change_total_traffics', methods=['GET', 'POST'])
def change_total_traffics():
    id = request.args.get('id', type = str)
    total_traffics = request.args.get('total_traffics', default = 1, type = int)
    
    conn = sqlite3.connect(dburl)
    c = conn.cursor()
    
    
    # convert total_traffics to bytes
    total_traffics = total_traffics * 1024 * 1024 * 1024
    
    # update inbounds table
    c.execute("SELECT * FROM inbounds WHERE settings LIKE '%"+id+"%'")
    main_data  = c.fetchall()
         
    settings =main_data[0][11]
    inbound_id =  main_data[0][0]
    
    data = json.loads(settings)['clients']
    
    email = ""
    total= 0
    # find id in data
    for i in range(len(data)):
      if data[i]['id'] == id:
        email = data[i]['email']
        total = data[i]['totalGB']+ total_traffics
        data[i]['totalGB'] = total
        break

    
        # update inbounds table
    settings = json.dumps({"clients": data, "decryption": "none", "fallbacks": []})
    c.execute("UPDATE inbounds SET settings = ? WHERE id = ?", (settings, inbound_id))


    c.execute("UPDATE client_traffics SET total = ? WHERE email = ?", (total, email))
    
    conn.commit()
    conn.close()
    time.sleep(2.0)
    os.system("systemctl restart x-ui")
    return 'total traffics has been changed'
  
@app.route('/chnage_ip_limit', methods=['GET', 'POST'])
def chnage_ip_limit():
    id = request.args.get('id', type = str)
    ip_limit = request.args.get('ip_limit', default = 1, type = int)
    
    conn = sqlite3.connect(dburl)
    c = conn.cursor()
    
    
    # update inbounds table
    c.execute("SELECT * FROM inbounds WHERE settings LIKE '%"+id+"%'")
    main_data  = c.fetchall()
         
    settings =main_data[0][11]
    inbound_id =  main_data[0][0]
    
    data = json.loads(settings)['clients']
    
    # find id in data
    for i in range(len(data)):
      if data[i]['id'] == id:
        data[i]['limitIp'] = ip_limit
        break

    
        # update inbounds table
    settings = json.dumps({"clients": data, "decryption": "none", "fallbacks": []})
    c.execute("UPDATE inbounds SET settings = ? WHERE id = ?", (settings, inbound_id))


 
    conn.commit()
    conn.close()
    time.sleep(2.0)
    os.system("systemctl restart x-ui")
    return 'ip limit has been changed'
if __name__ == '__main__':
  app.run(host='0.0.0.0')
  
