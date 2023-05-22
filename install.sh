apt-get install python3 python3-pip unzip nginx gunicorn -y 

pkill gunicorn 

rm -rf servermanager/ vps_manager/ v11.zip nohup.out v10.zip v12.zip 

git clone https://github.com/abbasnazari-0/vps_manager.git 
mv vps_manager/servermanager /etc/nginx/sites-enabled/servermanager 
unlink /etc/nginx/sites-enabled/default && nginx -s reload 

pip3 install flask jdatetime jsonpickle psutil 

echo "
[Unit]
Description=VPS MANAGER SERVICE

[Service]
ExecStart=gunicorn -w 3 vps_manager:app --bind 0.0.0.0:4000
WorkingDirectory=/root/vps_manager/
Restart=always

[Install]
WantedBy=multi-user.target" >> /etc/systemd/system/manager_vps.service

sudo systemctl daemon-reload
sudo systemctl enable manager_vps.service
sudo systemctl start manager_vps.service

echo ""
echo ""
echo ""
echo "success Install MANAGER"
echo ""
