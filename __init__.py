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
import psutil

app = Flask(__name__)

dburl = "/etc/x-ui/x-ui.db"
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
def format_size(size_bytes):
    """Convert a size in bytes to a human-readable format."""
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(size_bytes) < 1024.0:
            return f"{size_bytes:.2f} {unit}B"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} YiB"

def get_network_traffic():
    network_counters_before = psutil.net_io_counters()
    time.sleep(1)
    network_counters_after = psutil.net_io_counters()

    sent_bytes = network_counters_after.bytes_sent - network_counters_before.bytes_sent
    recv_bytes = network_counters_after.bytes_recv - network_counters_before.bytes_recv

    return sent_bytes, recv_bytes
  
def randomStringDigits(stringLength=10):
  lettersAndDigits = string.ascii_letters + string.digits
  return ''.join(random.choice(lettersAndDigits) for i in range(stringLength))

import threading

def restart_xui_in_thread():
  def restart_service():
    os.system("systemctl restart x-ui")
  thread = threading.Thread(target=restart_service)
  thread.start()
@app.route('/create', methods=['GET', 'POST'])
def create_user():
    item_count = request.args.get('item_count', default = 1, type = int)
    expire_date = request.args.get('expire', default = 0, type = int)
    limit_ip_count = request.args.get('limit_ip_count', default = 1, type = int)
    baseurl = request.args.get('baseurl', default = "mtn2amn.amnbridge.top", type = str)
    title = request.args.get('title', default = "Speedoooooooooooooo", type = str)
    inbound_port_target = request.args.get('inbound_port_target', default = 0, type = int)
    total_traffics = request.args.get('trafiic', default = 0, type = int)
    id = request.args.get('id', default = 1, type = str)
    if(inbound_port_target == 0):
        return "Please select a port 2" 
    if(total_traffics != 0):
      total_traffics = total_traffics * 1024 * 1024 * 1024

    # connect to db
    conn = sqlite3.connect(dburl)


    if(expire_date != 0):  
      # convert expire_date_day to timestamp + 000
      expire_date = ((expire_date * 86400) + int(jdatetime.datetime.now().timestamp()) ) * 1000
    
    # convert total_traffics to bytes

    c = conn.cursor()
    
    
    
    
    # check title is exist
    c.execute("SELECT id FROM client_traffics WHERE email = ?", (title,))
    # if more then 0 return
    if len(c.fetchall()) > 0:
      return {"status": "error", "message": "title is already exist"}
    
    
    
    # inbound table
    c.execute("SELECT settings,id  FROM inbounds WHERE port = ? LIMIT 1", (inbound_port_target,))
    # fetch one
    main_data  =  c.fetchall()
    print(main_data)
    clients = json.loads(main_data[0][0])
    inbound_id =  main_data[0][1]
    
    for client in clients['clients']:
      if client['id'] == str(id):
        return {"status": "error", "message": "id is already exist"}

    first_client = (clients['clients'][0])
    new_client = first_client.copy()
    new_client['id'] = str(id)
    new_client['totalGB'] = int(total_traffics)
    new_client['email'] = str(title)
    new_client['subId'] = str(randomStringDigits (10))
    new_client['enable'] = True
    new_client['expiryTime'] = int(expire_date)

      
    # add new client to clients
    clients['clients'].append(new_client)

    sql_traffic_tbl = f"INSERT INTO client_traffics  (`inbound_id`, `enable`, `email`, `total`, `up`, `down`, `expiry_time`) VALUES ({inbound_id}, 1, '{title}', {int(total_traffics)}, 0, 0,  {int(expire_date)})"

    try:
      c.execute(sql_traffic_tbl)
      conn.commit()
    except Exception as error:
      return (error)
    try:  
      c.execute("UPDATE inbounds SET settings = ? WHERE port = ?", (json.dumps(clients, indent = 4, sort_keys = True),inbound_port_target))
      conn.commit()
      conn.close()
    except sqlite3.OperationalError as e:
      return (e)

    # restart x-ui
    time.sleep(1.0)
    restart_xui_in_thread()
    return {"status": "success", "message": "user creating", "data": ""}
  
@app.route('/user_usage', methods=['GET', 'POST'])
def user_usage():
  email = request.args.get('email', type = str)
  

  
  
  conn = sqlite3.connect(dburl)
  c = conn.cursor()
  
  
    
  c.execute(f"SELECT * FROM client_traffics WHERE `email` = '{email}' LIMIT 1")
  
  main_data  = c.fetchall()
  
  
  # get up and down
  up = main_data[0][4]
  down = main_data[0][5]
  used = up + down
  return {"status": "success", "message": "user usages", "used": used}
  
@app.route('/disable_user', methods=['GET', 'POST'])
def disable_user():
  email = request.args.get('email', type = str)

  sql = f"SELECT inbound_id FROM client_traffics WHERE `email`  =  '{email}' LIMIT 1"
  conn = sqlite3.connect(dburl)
  # run 
  c = conn.cursor()
  c.execute(sql)
  main_data  = c.fetchall()
  inbound_id = main_data[0][0]
  # c.execute(f"UPDATE client_traffics SET `enable` = 0 WHERE `email` = '{email}'")
  
  # conn.commit()
  c.execute(f"SELECT settings  FROM inbounds WHERE id = {inbound_id} LIMIT 1")
  # fetch one
  main_data  =  c.fetchall()
  clients = json.loads(main_data[0][0])
  users = clients['clients']
  for i in range(len(users)):
    if users[i]['email'] == email:
      users[i]['enable'] = False
      break
  clients['clients'] = users
  try:  
    c.execute("UPDATE inbounds SET settings = ? WHERE id = ?", (json.dumps(clients, indent = 4, sort_keys = True),inbound_id))
    conn.commit()
    
  except sqlite3.OperationalError as e:
    return (e)
  
  conn.close()
  
  # os.system("systemctl restart x-ui")
  time.sleep(1.0)
  
  # run in background : restart_xui()
  restart_xui_in_thread()
  
  return {"status": "success", "email": email, "message": "user disabled"}
  
@app.route('/enable_user', methods=['GET', 'POST'])
def enable_user():
  email = request.args.get('email', type = str)
  sql = f"SELECT inbound_id FROM client_traffics WHERE `email`  =  '{email}' LIMIT 1"
  conn = sqlite3.connect(dburl)
  # run 
  c = conn.cursor()
  c.execute(sql)
  main_data  = c.fetchall()
  inbound_id = main_data[0][0]
  # c.execute(f"UPDATE client_traffics SET `enable` = 0 WHERE `email` = '{email}'")
  
  # conn.commit()
  c.execute(f"SELECT settings  FROM inbounds WHERE id = {inbound_id} LIMIT 1")
  # fetch one
  main_data  =  c.fetchall()
  clients = json.loads(main_data[0][0])
  users = clients['clients']
  for i in range(len(users)):
    if users[i]['email'] == email:
      users[i]['enable'] = True
      break
  clients['clients'] = users
  try:  
    c.execute("UPDATE inbounds SET settings = ? WHERE id = ?", (json.dumps(clients, indent = 4, sort_keys = True),inbound_id))
    conn.commit()
    
  except sqlite3.OperationalError as e:
    return (e)
  
  conn.close()
  # os.system("systemctl restart x-ui")
  time.sleep(1.0)
  restart_xui_in_thread()
  return {"status": "success", "email": email, "message": "user enable"}
  

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
  
@app.route('/restart/x-ui', methods=['GET', 'POST'])
def restart_xui():
    restart_xui_in_thread()
    return "Restarted X-UI"
    

@app.route('/restart/socat', methods=['GET', 'POST'])
def restart_socat():
    os.system("systemctl restart tunnel.service")
    return 'Restarted Socat'
  
@app.route('/analyze/now', methods=['GET', 'POST'])
def nowAnalyze():
  sent, received = get_network_traffic()
  sent_humanized = (sent)
  received_humanized = (received)
  return (json.dumps({"sent": sent_humanized, "received": received_humanized}))

@app.route('/restart/force', methods=['GET', 'POST'])
def restart_force():
    os.system("reboot")
    return 'system rebooting'
  
if __name__ == '__main__':
  app.run(host='0.0.0.0' , port=4000)
  
  
# ok
