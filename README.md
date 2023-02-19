apt-get install python3
apt-get install python3-pip 
apt-get install unzip  nginx  gunicorn -y


wget https://github.com/abbasnazari-0/vps_manager/archive/refs/tags/v1.zip
unzip v1.zip -d .


mv vps_manager-1/servermanager  /etc/nginx/sites-enabled/servermanager

mkdir servermanager 

mv vps_manager-1/__init__.py servermanager/__init__.py

rm -rf vps_manager-1


unlink /etc/nginx/sites-enabled/default
nginx -s reload

pip3 install flask  jdatetime

nohup gunicorn -w 3 servermanager:app &
