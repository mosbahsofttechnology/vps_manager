apt-get install python3 python3-pip unzip nginx gunicorn -y 

pkill gunicorn 

rm -rf servermanager/ vps_manager/ v11.zip nohup.out v10.zip v12.zip 

git clone https://github.com/abbasnazari-0/vps_manager.git 
mv vps_manager/servermanager /etc/nginx/sites-enabled/servermanager 
unlink /etc/nginx/sites-enabled/default && nginx -s reload 

pip3 install flask jdatetime jsonpickle psutil 

rm /etc/systemd/system/manager_vps.service

echo "[Unit]
Description=VPS MANAGER SERVICE
After=network.target
StartLimitIntervalSec=0
[Service]
Type=simple
Restart=always
RuntimeMaxSec=6h
RestartSec=1
User=root
ExecStart=gunicorn -w 3 vps_manager:app --bind 0.0.0.0:4000 
WorkingDirectory=/root/

[Install]
WantedBy=multi-user.target

" >> /etc/systemd/system/manager_vps.service

sudo systemctl daemon-reload
sudo systemctl enable manager_vps.service
sudo systemctl start manager_vps.service

echo ""
echo ""
echo ""
echo "success Install MANAGER"
echo ""
