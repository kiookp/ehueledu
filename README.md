git 到 服务器 

运行docker之前需要配置好ini 配置文件

docker 后台运行指令
````
docker run -d -v /root/ehueledu:/data ipd805/kkedu:v1.0 sh -c "cd /data && python3 app.py"
````
pyperclip 路径问题：
 
 
````
pip install --target=./ pyperclip
````
