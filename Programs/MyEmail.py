"""
自定义邮件发送模块
"""
import smtplib
from email.mime.text import MIMEText


def sendEmail(mail_host,mail_user,mail_password,sender,receivers,content="内容",title="主题"):
    """
    发送邮件
    :param content:邮件内容
    :param title: 邮件主题
    :param mail_host: 邮件服务器地址
    :param mail_user: 邮件用户(一般就是发件方)
    :param mail_password: 邮件用户授权密码（非登陆密码）
    :param sender: 发送方邮件
    :param receivers: 邮件接收方（列表）
    :return:
    """
    message = MIMEText(content, 'plain', 'utf-8')  # 内容, 格式, 编码
    message['From'] = "{}".format(sender)
    message['To'] = ",".join(receivers)
    message['Subject'] = title

    try:
        smtpObj = smtplib.SMTP_SSL(mail_host, 465)  # 启用SSL发信, 端口一般是465
        smtpObj.login(mail_user, mail_password)  # 登录验证
        smtpObj.sendmail(sender, receivers, message.as_string())  # 发送
        print("邮件发送成功")
    except smtplib.SMTPException as e:
        print(e)