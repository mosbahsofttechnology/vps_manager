import json
import sqlite3
import mysql.connector
import ipaddress
import requests
from urllib.parse import urlparse, parse_qs
import re
import string
import random
import time
import os
mydb = mysql.connector.connect(
  host="37.152.182.34",
  user="manager",
  password="nazari@0794054171@As",
  database="lhs"
)
import jdatetime

dburl = "/etc/x-ui/x-ui.db"
# dburl = "x-ui.db"

# run query
conn = sqlite3.connect(dburl)

def sendMessageToTelegramBot(message):
    APITOKEN = "6117050323:AAGBvHWFrfR-c8vNHH7Bnl1ittQl2VU0NdE"

    # آیدی چت گروه یا کاربری که میخوای پیام رو بهش بفرستی رو اینجا قرار بده
    chat_id = "@vps_status"

    # URL آدرس API برای ارسال پیام
    url = f"https://api.telegram.org/bot{APITOKEN}/sendMessage"

    # پارامترهای بدنه درخواست
    payload = {
        "chat_id": chat_id,
        "text": message,
        
    }

    # ارسال درخواست POST به آدرس API
    response = requests.post(url, json=payload)

    # بررسی وضعیت پاسخ
    if response.status_code == 200:
        return "پیام با موفقیت ارسال شد."
    else:
        return "مشکلی در ارسال پیام به وجود آمد."


def restart_xui_in_thread():
  os.system("systemctl restart x-ui")
  
def get_my_ip():
  import socket
  s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  s.connect(("8.8.8.8", 80))
  ip = s.getsockname()[0]
  s.close()
  return ip

def randomStringDigits(stringLength=10):
  lettersAndDigits = string.ascii_letters + string.digits
  return ''.join(random.choice(lettersAndDigits) for i in range(stringLength))


my_ip = get_my_ip()



def disable_user(email):
  sql = f"SELECT inbound_id FROM client_traffics WHERE `email`  = '{email}' LIMIT 1"
  
  conn = sqlite3.connect(dburl)
  # run 
  c = conn.cursor()
  c.execute(sql)
  main_data  = c.fetchall()
  if len(main_data) == 0:
    return {"status": "error", "message": "port is not found"}
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
      if( users[i]['enable'] == False ):
        return {"status": "success", "email": email, "message": "user already disabled"}
      users[i]['enable'] = False
      break
    

  clients['clients'] = users
  try:  
    c.execute("UPDATE inbounds SET settings = ? WHERE id = ?", (json.dumps(clients, indent = 4, sort_keys = True),inbound_id))
    conn.commit()
    
  except sqlite3.OperationalError as e:
    return (e)
  

  return {"status": "success", "email": email, "message": "user disabled"}


def create_user( inbound_port_target, id, total_traffics , title, expire_date, config_id):
    # print('http://' + address + ':4000' + '/create?inbound_port_target=' + str(port) + '&id=' + uuid + '&trafiic=' + str(mass) + '&title=' + token + '&expire=' + str(day) + '')

    if(inbound_port_target == 0):
        return "Please select a port 2" 
    if(total_traffics != 0):
      total_traffics = int(total_traffics) * 1024 * 1024 * 1024

        # connect to db
    conn = sqlite3.connect(dburl)

    expire_date = int(expire_date)
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
    
    print(f"SELECT settings,id  FROM inbounds WHERE port = {int(inbound_port_target)} LIMIT 1")
    
    # inbound table
    c.execute(f"SELECT settings,id  FROM inbounds WHERE port = {int(inbound_port_target)} LIMIT 1")
    # fetch one
    main_data  =  c.fetchall()
    
    
    if main_data == "[]" or main_data == []:
        return {"status": "error", "message": "1port is not found"}
      
    # orubt*
    # print(main_data)
    # print(main_data)
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
    except sqlite3.OperationalError as e:
      return (e)

    
    # restart x-ui
    time.sleep(1.0)
    # restart_xui_in_thread()
    return {"status": "success", "message": "user creating", "data": ""}


def convert_mapped_ipv4(address):
    if address.startswith('::ffff:'):
        ipv4_address = ipaddress.IPv6Address(address).ipv4_mapped
        return str(ipv4_address)
    else:
        return address
mycursor = mydb.cursor()
def is_ip_or_url(input_str):
    try:
        ipaddress.ip_address(input_str)
        return False  # اگر ورودی یک IP باشد
    except ValueError:
        try:
            urlparse(input_str)
            return True  # اگر ورودی یک URL باشد
        except ValueError:
            return False  # اگر ورودی هیچکدام نباشد
def create_user_in_target_server(address, port, uuid, mass, token, day, config_id):
    print("1address : " + address + " port : " + str(port) + " uuid : " + uuid + " mass : " + str(mass) + " token : " + token)
    global mycursor
    # send request tp http://$address:4000/create
    import requests
    import json
    # try:
        # if check_user_is_exist_in_target_server(address, token):
        #     return
    # except Exception as e:
    #     print("check_user_is_exist_in_target_server error : " + str(e))
    # print('http://' + address + ':4000' + '/create?inbound_port_target=' + str(port) + '&id=' + uuid + '&trafiic=' + str(mass) + '&title=' + token + '&expire=' + str(day) + '')
    # response = requests.post('http://' + address + ':4000' + '/create?inbound_port_target=' + str(port) + '&id=' + uuid + '&trafiic=' + str(mass) + '&title=' + token + '&expire=' + str(day) + '')
    res = create_user (  port,   uuid,  mass,  token,  day,  config_id)
    # response = requests.post('http://' + address + ':4000' + '/create?inbound_port_target=' + str(port) + '&id=' + uuid + '&trafiic=' + str(mass) + '&title=' + token + '&expire=' + str(day) + '')
    # print(response.text)
    # if(response.status_code == 200):
    # print (res)
    if((res)['status'] == "error"):
        print(res['message'])
            
    if((res)['status'] == 'success'):
        sql = f"INSERT INTO tbl_users_configs (user_token, config_id) VALUES ('{token}', '{config_id}')"
        mycursor.execute(sql)
        mydb.commit()
        print (f"successfully created on {address}")
            
    # else:
        # TODO send error report in telegram
        # sendMessageToTelegramBot (f"ادمین جون مثل اینکه مشکلی در ساخت یوزر برای کاربرمون ایجاد شده \nشناسه کاربر: {token} \n مشکل داخلی: {response.text} \n uuid کاربر : {uuid} \n در سرور {address} \n با این جواب : {json.loads(response.text)} ")
        # print("unkown error")
          
def vless_url_export_ip(uri_config, ipv4):
    address = ''
    
    # Parse the URL
    url_parts = urlparse(uri_config)

    # Get the query parameters
    query_params = parse_qs(url_parts.query)

    # Check the security parameter
    security = query_params.get('security', [''])[0]

    # Check if security is 'none' or 'reality'
    if security == 'none' or not security:
        # Return the host value
        address = query_params.get('host', '')
    elif security == 'reality':
        # Return the address value (IP address)
        matches = re.search('@(.*):', uri_config)
        ip_address = matches.group(1) if matches else ''   
        address = ip_address
    elif security == 'tls':
        # Return the host value
        address = query_params.get('host', '')
    else:
        matches = re.search('@(.*):', uri_config)
        ip_address = matches.group(1) if matches else ''
        address = ip_address
    # if address is list  convert to string
    if isinstance(address, list):
        address = address [0]
         
     
    if(address.startswith('[') and address.endswith(']')):
        # remove [ and ] from start and end
        address = address[1:-1]
    if(address.startswith('::ffff') ):
        # remove [ and ] from start and end
        address = convert_mapped_ipv4(address)
        
    address = address.lower()
    
    if (is_ip_or_url(address) == True):
        address = ipv4
        
    if (address == '' or address == None):
        address = ipv4
    return {'host': address, 'port': url_parts.port}



# exit(0)
  


  


def find_id_with_email(email):
  sql = f"SELECT settings,id, port  FROM inbounds WHERE `settings`  LIKE  '%{email}%' LIMIT 1"
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
  port =  main_data[0][2]
  

  for client in clients['clients']:
    if client['email'] == str(email):
      return  {'id': client['id'], "inbound_id" :  inbound_id, "port": port}


def inser_users():
  # check has new user
  sql_new_user_checker = """SELECT 
      tbl_user.id, tbl_user.token, tbl_user.config_tag_id, tbl_user.time, tbl_user.day, tbl_user.usage_max, tbl_user.email,
      JSON_ARRAYAGG(JSON_OBJECT('config', tbl_config.config, 'ip', tbl_config.ip, 'id', tbl_config.item_id)) as configs, tbl_user.user_enabling
  FROM
      tbl_user
      INNER JOIN tbl_config ON FIND_IN_SET(tbl_user.config_tag_id, tbl_config.id) 
  WHERE
      tbl_user.is_new = 'new_user' 
  GROUP BY
      tbl_user.id;
  """
  
  # run query
  mycursor.execute(sql_new_user_checker)
  myresult = mycursor.fetchall()

  for x in myresult:
    configs = json.loads(x[7])
    for config in configs:
      vless_url = vless_url_export_ip(config['config'], config['ip'])
      # print(str(vless_url ['host'] == my_ip) + config['config'])
      if(vless_url ['host'] == my_ip):
        # check in user usage table user exited or not
        
        # check for user is enabled
        is_enabled = x[8]
        if(is_enabled == 0):
          # return
          disable_user(x[1] + "_" + str(config['id']))
          continue
        
        # check for user is inserted in main table
        sql_check_user = f"SELECT id FROM tbl_users_configs WHERE user_token = '{x[1]}_{config['id']}' LIMIT 1"
        
        mycursor.execute(sql_check_user)
        myresult_checker = mycursor .fetchall()
        if(len(myresult_checker) > 0):
            # continue
          continue
        
        # instring to table and creating USER
        email = x[1]
        id = x[6]
        config_id = config['id']
        day = x[4]
        mass = x[5]
        port = vless_url ['port']
        # print()
        create_user_in_target_server(my_ip, port, id, mass, email + "_" + str(config['id']), day, config_id)
      if (vless_url['host'] == None):
       sendMessageToTelegramBot(f"ادمین جون من ربات منیجر یوزر ها هستم\n مثل اینکه آیپی این کانفیگ رو فراموش کردی تو جدول بزاری\n ممنون میشم یه نیم نگاهی بندازی\nکانفیگ مورد نظر :  \n{config['config']} ")





inser_users()
conn.close()
mydb.close()
restart_xui_in_thread()
