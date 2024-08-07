import os
import paramiko
import requests
import json
import logging
from datetime import datetime, timezone, timedelta
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
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


# def post_weichat_2():
#     token = os.getenv('ANPUSH_TOKEN')
#     if not token:
#         logger.error("ANPUSH_TOKEN is not set.")
#         return

#     url = "https://api.anpush.com/push/"+token
#     # 从环境变量中获取token
    
   
#     # post发送的字典参数
#     data_dict = {
#         'title': 'serv00保活签到',
#         'content': content,  # 确保变量在此处之前已经被定义
#         "channel": "56466"
#     }
#     headers = {
#     "Content-Type": "application/x-www-form-urlencoded"
#     }
#     r = requests.post(url, headers=headers, data=data_dict)  # 发起请求
#     print(r.text)
#     logger.info("推送状态: %s", r.text)

# if __name__ == '__main__':
#     post_weichat_2()

def send_webhook(content):
    token = os.getenv('WEBHOOK')
    webhook_url = token  # 请在这里填入你的key
    headers = {'Content-Type': 'application/json'}
    payload = {
        "msgtype": "text",
        "text": {
            "content": content
        }
    }

    try:
        response = requests.post(webhook_url, json=payload, headers=headers)
        if response.json().get('errcode') == 0:
            return response.json()  # 如果请求成功，返回响应数据
        else:
            raise Exception(response.json().get('errmsg', '发送失败'))
    except Exception as e:
        print(f"An error occurred: {e}")


# 使用函数示例
result = send_webhook(content)
print(result)
logger.info("推送状态: %s", result)
