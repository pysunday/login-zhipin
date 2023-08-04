# coding: utf-8
import os
import json
import inquirer
from inquirer.themes import GreenPassion
from sunday.login.zhipin import config
from sunday.utils import mergeObj, LoginBase
from sunday.core import paths, Logger, enver, exit, cache_name, Auth, getCurrentUser
from bs4 import BeautifulSoup
from pydash import get

# 命令行执行登录操作
@cache_name('zhipin')
class Zhipin(LoginBase):
    def __init__(self):
        self.logger = Logger('ZHIPIN LOGIN').getLogger()
        LoginBase.__init__(self, __file__, logger=self.logger)
        self.rs, self.isLogin = self.initRs(config.getUserInfo)

    def checkLogin(self, checkUrl):
        # 验证是否登录
        res = self.fetch.get(checkUrl)
        return res.status_code != 200 or res.json()['code'] != 0

    def showQrcode(self, text):
        # 打印二维码
        import qrcode
        qr = qrcode.QRCode()
        qr.add_data(text)
        qr.print_tty()

    def checkScan(self, uuid, deep=0):
        """检查扫码情况"""
        if deep == 0: self.logger.warning('二维码打印成功，请用zhipin手机软件扫码, 请在25秒内完成扫码！')
        scanRes = self.rs.get(config.scanUrl % uuid).json()
        if not scanRes.get('scaned'):
            if scanRes.get('msg') == 'timeout':
                questions = [
                    inquirer.List('isReScan',
                        message='扫码超时，是否重新扫码?',
                        choices=[('重新扫码', True), ('不扫了，直接退出', False)]
                    ),
                ]
                answers = inquirer.prompt(questions, theme=GreenPassion())
                if not answers["isReScan"]: exit('扫码登录后才能继续使用！')
                self.logger.warning('请重新扫码!')
                return self.checkScan(uuid, deep + 1)
            else:
                exit('扫码流程未知错误请稍后重试!')
        return True
    
    def checkApp(self, qrid, deep=0):
        """检查APP登录确认情况"""
        if deep == 0: self.logger.warning('请用zhipin手机软件确认登录, 请在25秒内完成确认！')
        scanRes = self.rs.get(config.scanLoginUrl % qrid).json()
        if deep == 20: exit('长时间未确认登录退出程序，请重试！')
        if not scanRes.get('scaned'):
            if scanRes.get('msg') == 'timeout':
                return self.checkApp(qrid, deep + 1)
            else:
                exit('APP确认流程未知错误请稍后重试!')
        elif not scanRes.get('login'):
            exit('取消登录成功')
        return True
    
    def getQrid(self, uuid):
        qrid = get(self.rs.get(config.getSecondKeyUrl % uuid).json(), 'zpData.qrId')
        self.logger.debug('uuid: %s, qrid: %s' % (uuid, qrid))
        return qrid

    def setCookieA(self):
        # cookie设置__a的值, 设置uniqid是会用到
        import math, random, time
        a = str(math.floor(9e7 * random.random() + 1e7))
        b = str(round(time.time()))
        times = str(random.randint(0, 9))
        value = '.'.join([a, b, '', b, times, '1', times, times])
        self.setCookie('__a', value, '.zhipin.com')

    def initCookies(self):
        # 初始化cookie
        self.setCookieA()

    def login(self):
        if self.isLogin:
            self.logger.info('登录成功')
            return self
        self.initCookies()
        res = self.rs.get(config.loginUrl)
        soup = BeautifulSoup(res.content, 'lxml')
        uuid = soup.select_one('input[class="uuid"]').attrs['value']
        self.showQrcode(uuid)
        self.checkScan(uuid)
        self.checkApp(uuid)
        self.rs.get(config.dispatcher % uuid)
        if not self.checkLogin(config.getUserInfo):
            self.logger.info('登录成功')
            self.saveCookie()
            return self
        else:
            self.logger.warning('登录失败')
            exit('登录失败')

    def login2brower(self):
        # 登录态同步到浏览器
        cookies = json.dumps([f'{key}={val}' for key, val in self.rs.getCookiesDict().items()])
        print('步骤1. 浏览器进入网站：https://www.zhipin.com/')
        jsexec = f"javascript:{cookies}.map(t => document.cookie = t.trim() + ';' + 'path=/');history.pushState(undefined, undefined, '#cookie写入成功！')"
        print(f'步骤2. 顶部网址输入框写入并回车：{jsexec}')

    def setZpStoken(self):
        # 登录态同步到浏览器并返回设置__zp_stoken__值
        self.login2brower()
        print('步骤3. 浏览器输入网址：https://www.zhipin.com/web/geek/job')
        jsexec = f"javascript:history.pushState(undefined, undefined, '#' + /__zp_stoken__=(.*);?/.exec(document.cookie)[1])"
        print(f'步骤4. 顶部网址输入框写入并回车：{jsexec}')
        print(f'步骤5. 顶部网址输入框#后端的字符串复制到这里')
        zpToken = input('将步骤5复制的文本黏贴到这里: ')
        self.rs.setCookie('__zp_stoken__', zpToken, '*.zhipin.com')


if __name__ == "__main__":
    login = Zhipin()
    login.login()
