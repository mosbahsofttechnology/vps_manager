import json
import sqlite3
import mysql.connector
import ipaddress
import requests
from urllib.parse import urlparse, parse_qs
import re
mydb = mysql.connector.connect(
  host="37.152.182.34",
  user="manager",
  password="nazari@0794054171@As",
  database="lhs"
)
def get_my_ip():
  import socket
  s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  s.connect(("8.8.8.8", 80))
  ip = s.getsockname()[0]
  s.close()
  return ip
my_ip = get_my_ip()

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
    print('http://' + address + ':4000' + '/create?inbound_port_target=' + str(port) + '&id=' + uuid + '&trafiic=' + str(mass) + '&title=' + token + '&expire=' + str(day) + '')
    response = requests.post('http://' + address + ':4000' + '/create?inbound_port_target=' + str(port) + '&id=' + uuid + '&trafiic=' + str(mass) + '&title=' + token + '&expire=' + str(day) + '', timeout=10)
    print(response.text)
    if(response.status_code == 200):
        if(json.loads(response.text)['status'] == "error"):
              print (f"cant run in {address}")
        if(json.loads(response.text)['status'] == 'success'):
            sql = f"INSERT INTO tbl_users_configs (user_token, config_id) VALUES ('{token}', '{config_id}')"
            mycursor.execute(sql)
            mydb.commit()
            print (f"successfully created on {address}")
            
    else:
        # TODO send error report in telegram
        # sendMessageToTelegramBot (f"ادمین جون مثل اینکه مشکلی در ساخت یوزر برای کاربرمون ایجاد شده \nشناسه کاربر: {token} \n مشکل داخلی: {response.text} \n uuid کاربر : {uuid} \n در سرور {address} \n با این جواب : {json.loads(response.text)} ")
        print("unkown error")
          
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
        
        
    return {'host': address, 'port': url_parts.port}



# exit(0)
  
dburl = "/etc/x-ui/x-ui.db"
# dburl = "x-ui.db"


  
sql = f"SELECT * FROM client_traffics WHERE `enable` = 1"
# run query
conn = sqlite3.connect(dburl)
c = conn.cursor()
c.execute(sql)
 

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



def report_usage():
  # show data 
  main_data  = c.fetchall()
  for  i in main_data:
    email = i[3]
    up = i[4]
    down = i[5]
    my_ip = get_my_ip()
    inboundData = (find_id_with_email(email))
    if inboundData != None :   
      mycursor.execute(f"SELECT * FROM tbl_user_usages WHERE `email` = '{email}' AND `user_id` = '{inboundData['id']}' AND port = '{inboundData['port']}' AND  ip = '{my_ip}'")
      myresult = mycursor.fetchall()
      
      if len(myresult) == 0:
        
          mycursor.execute(f"INSERT INTO tbl_user_usages (email, user_id, up, down, ip, port) VALUES ('{email}', '{inboundData['id']}', '{up}', '{down}', '{my_ip}', '{inboundData['port']}')")
          mydb.commit()
      else:
          print(f"UPDATE tbl_user_usages SET up = '{up}', down = '{down}' WHERE email = '{email}' AND user_id = '{inboundData['id']}' AND ip = '{my_ip}' AND port = '{inboundData['port']}'")
          mycursor.execute(f"UPDATE tbl_user_usages SET up = '{up}', down = '{down}' WHERE email = '{email}' AND user_id = '{inboundData['id']}' AND ip = '{my_ip}' AND port = '{inboundData['port']}'")
          mydb.commit()
  conn.close()

def inser_users():
  # check has new user
  sql_new_user_checker = """SELECT 
      tbl_user.id, tbl_user.token, tbl_user.config_tag_id, tbl_user.time, tbl_user.day, tbl_user.usage_max, tbl_user.email,
      JSON_ARRAYAGG(JSON_OBJECT('config', tbl_config.config, 'ip', tbl_config.ip, 'id', tbl_config.item_id)) as configs
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
      print(vless_url)
      if(vless_url ['host'] == my_ip):
        # check in user usage table user exited or not
        
        sql_check_user = f"SELECT * FROM tbl_users_configs WHERE user_token LIKE '{x[1]}%' AND config_id = '{config['id']}'"
        
        mycursor.execute(sql_check_user)
        myresult_checker = mycursor .fetchall()
        if(len(myresult_checker) > 0):
          continue
    
        
        email = x[1]
        id = x[6]
        config_id = config['id']
        day = x[4]
        mass = x[5]
        port = vless_url ['port']
        create_user_in_target_server(my_ip, port, id, mass, email + "_" + str(config['id']), day, config_id)
    



inser_users()
report_usage()
