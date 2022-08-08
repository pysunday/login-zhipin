# coding: utf-8
import os
import inquirer
from inquirer.themes import GreenPassion
from sunday.login.zhipin import config
from sunday.utils import mergeObj, LoginBase
from sunday.core import paths, Logger, enver, exit, cache_name, Auth, getCurrentUser
from bs4 import BeautifulSoup
from pydash import get

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

    def login(self):
        if self.isLogin:
            self.logger.info('登录成功')
            return self
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
        

if __name__ == "__main__":
    login = Zhipin()
    login.login()
