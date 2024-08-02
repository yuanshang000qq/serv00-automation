import os
import paramiko
import requests
import json
import logging
from datetime import datetime, timezone, timedelta

def ssh_multiple_connections(hosts_info, command):
    users = []
    hostnames = []
    for host_info in hosts_info:
        hostname = host_info['hostname']
        username = host_info['username']
        password = host_info['password']
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname=hostname, port=22, username=username, password=password)
            stdin, stdout, stderr = ssh.exec_command(command)
            user = stdout.read().decode().strip()
            users.append(user)
            hostnames.append(hostname)
            ssh.close()
            logger.info("运行状态: %s",f"用户：{username}，连接 {hostname} 成功")
        except Exception as e:
            logger.info("运行状态: %s",f"用户：{username}，连接 {hostname} 时出错: {str(e)}")
            #print(f"用户：{username}，连接 {hostname} 时出错: {str(e)}")
    return users, hostnames

ssh_info_str = os.getenv('SSH_INFO', '[]')
hosts_info = json.loads(ssh_info_str)

command = 'whoami'
user_list, hostname_list = ssh_multiple_connections(hosts_info, command)
user_num = len(user_list)
content = "SSH服务器登录信息：\n"
for user, hostname in zip(user_list, hostname_list):
    content += f"用户名：{user}，服务器：{hostname}\n"
beijing_timezone = timezone(timedelta(hours=8))
time = datetime.now(beijing_timezone).strftime('%Y-%m-%d %H:%M:%S')
loginip = requests.get('https://api.ipify.org?format=json').json()['ip']
content += f"本次登录用户共： {user_num} 个\n登录时间：{time}\n登录IP：{loginip}"

push = os.getenv('PUSH')

def post_weichat_2():
    url = 'http://www.pushplus.plus/send'
    # 从环境变量中获取token
    token = os.getenv('PUSHPLUS_TOKEN')
    if not token:
        logger.error("PUSHPLUS_TOKEN is not set.")
        return

    # post发送的字典参数
    data_dict = {
        'token': token,  # 使用环境变量中的token值
        'title': 'serv00保活签到',
        'template': 'txt',
        'content': content  # 确保msg变量在此处之前已经被定义
    }
    r = requests.post(url, data=data_dict)  # 发起请求
    print(r.text)
    logger.info("推送状态: %s", r.text)

if __name__ == '__main__':
    post_weichat_2()
