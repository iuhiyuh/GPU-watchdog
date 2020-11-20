import getpass
import re
import smtplib
import socket
import subprocess
import time
from email.mime.text import MIMEText

import numpy as np


def login_email():
    msg_from = input('发送方邮箱账户:')  # 发送方邮箱
    passwd = input('发送方邮箱密码:')  # 填入发送方邮箱的授权码
    msg_to = input('收件人邮箱:')  # 收件人邮箱

    return msg_from, passwd, msg_to


def gather_info():
    user_name = getpass.getuser()

    ip_addr = socket.gethostbyname(socket.gethostname())

    used_gpu_memory = np.array(list(map(int, re.findall("(\d+)", subprocess.getstatusoutput(
        'nvidia-smi -q -d Memory |grep -A4 GPU|grep Used')[1], flags=0))))
    free_gpu_memory = np.squeeze(np.argwhere(used_gpu_memory < 10000)).tolist()
    gpu_message = f"当前可能空闲的卡号为：{str(free_gpu_memory)}."

    content = f"{user_name}, 您好！ " \
              f"IP 为 {ip_addr} 的服务器有显卡空余, " \
              f"{gpu_message}"

    return content, True if len(free_gpu_memory) > 0 else False


def send_email(content, msg_from, passwd, msg_to):
    msg = MIMEText(content)
    msg['Subject'] = "GPU 有空缺提示!"
    msg['From'] = msg_from
    msg['To'] = msg_to
    try:
        s = smtplib.SMTP_SSL("smtp.qq.com", 465)  # 邮件服务器及端口号
        s.login(msg_from, passwd)
        s.sendmail(msg_from, msg_to, msg.as_string())
        print("发送成功")
    except Exception as e:
        print(f"发送失败: {e}")
    finally:
        quit()


if __name__ == "__main__":
    msg_from, passwd, msg_to = login_email()
    while True:
        content, flag = gather_info()
        if flag:
            send_email(content, msg_from, passwd, msg_to)
        time.sleep(10000)
