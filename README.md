[Step 1] first install apps [Step 1]

    apt-get install python3 python3-pip unzip  nginx  gunicorn -y

# 

[Step 1.5] Optional [remove if exited work before new job]
#### if excited you can see folder of servermanager

    pkill gunicorn && rm -rf servermanager v11.zip nohup.out  v10.zip
#  

[Step 2] download scripts

    wget https://github.com/abbasnazari-0/vps_manager/archive/refs/tags/v11.zip &&  unzip v11.zip -d . && mv vps_manager-11/servermanager  /etc/nginx/sites-enabled/servermanager && mkdir servermanager &&  mv vps_manager-11/__init__.py servermanager/__init__.py && rm -rf vps_manager-11 && unlink /etc/nginx/sites-enabled/default &&  nginx -s reload

[Step 3] install python settings

    pip3 install flask  jdatetime jsonpickle

[Step 4] run flask server

    nohup gunicorn -w 3 servermanager:app --bind 0.0.0.0:4000 &




# Usage Gauid
 
## create user by set count.
 /create 
 
                    @  item_count=1
                    @  expire=30
                    @  trafiic=30
                    @  inbound_id=1
                    @  limit_ip_count=1
                    @  title=Speedoooooooooooooo


## remove user by id
/remove 

                    #  id=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
                    


## get all user_item_count 

/user_item_count



## chnage Expire Date by user_id

/change_expire_date.

                    # id=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
                    # expire=20



## chnage total traffic by user_id                    

/change_total_traffics

                    # id=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
                    # total_traffics=1



## change ip limit by user_id        

/chnage_ip_limit

                    # id=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
                    # ip_limit=20
                    
## restart x-ui      

        /restart/x-ui
        
## restart socat

        /restart/socat
