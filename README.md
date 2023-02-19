[Step 1] first install apps [Step 1]

    apt-get install python3
    apt-get install python3-pip 
    apt-get install unzip  nginx  gunicorn -y

[Step 2] download scripts

    wget https://github.com/abbasnazari-0/vps_manager/archive/refs/tags/v1.zip
    unzip v1.zip -d .

[Step 3] config in server to some direcory managment

    mv vps_manager-1/servermanager  /etc/nginx/sites-enabled/servermanager
    mkdir servermanager 
    mv vps_manager-1/__init__.py servermanager/__init__.py
    rm -rf vps_manager-1

[Step 4] config nbinx

    unlink /etc/nginx/sites-enabled/default
    nginx -s reload

[Step 5] install python settings

    pip3 install flask  jdatetime

[Step 6]run flask server

    nohup gunicorn -w 3 servermanager:app &
