# 用于API接口调用时执行登录相关操作
from sunday.core.fetch import Fetch
from sunday.login.zhipin import Zhipin
from sunday.utils import mergeObj, LoginBase
from sunday.login.zhipin import config
from sunday.login.zhipin.error import ZhipinLoginError
from sunday.core import paths, Logger, enver, exit, cache_name, Auth, getCurrentUser
from bs4 import BeautifulSoup

# 获取渲染二维码的唯一标识
class LoginByQrcodeGetUuid():
    def __init__(self):
        self.logger = Logger('ZHIPIN LOGIN').getLogger()
        self.fetch = Fetch()

    def setCookieA(self):
        # cookie设置__a的值, 设置uniqid是会用到
        import math, random, time
        a = str(math.floor(9e7 * random.random() + 1e7))
        b = str(round(time.time()))
        times = str(random.randint(0, 9))
        value = '.'.join([a, b, '', b, times, '1', times, times])
        self.fetch.setCookie('__a', value, '.zhipin.com')

    def initCookies(self):
        # 初始化cookie
        self.setCookieA()

    def getUuid(self):
        self.initCookies()
        res = self.fetch.get(config.loginUrl)
        soup = BeautifulSoup(res.content, 'lxml')
        uuid = soup.select_one('input[class="uuid"]').attrs['value']
        return {
            'qrid': uuid,
            'session': self.fetch.getCookiesDict()
        }

# 二维码方式登录执行的检查
class LoginByQrcodeCheck():
    def __init__(self, params={}):
        self.uuid = params.get('qrid')
        session = params.get('session')
        if not self.uuid or not session: raise ZhipinLoginError(20002, other='qrid, session')
        self.fetch = Fetch()
        for key, val in session.items():
            self.fetch.setCookie(key, val, '.zhipin.com')

    def checkScan(self):
        """检查扫码情况"""
        scanRes = self.fetch.get(config.scanUrl % self.uuid, timeout=300).json()
        if not scanRes.get('scaned'):
            if scanRes.get('msg') == 'timeout':
                raise ZhipinLoginError(20001)
            else:
                raise ZhipinLoginError(-1)
        return True

    def checkApp(self):
        """检查APP登录确认情况, 已经确认则返回新的登录态"""
        scanRes = self.fetch.get(config.scanLoginUrl % self.uuid).json()
        if not scanRes.get('scaned'):
            if scanRes.get('msg') == 'timeout':
                raise ZhipinLoginError(20004)
            else:
                raise ZhipinLoginError(-1)
        elif not scanRes.get('login'):
            raise ZhipinLoginError(20003)
        self.fetch.get(config.dispatcher % self.uuid)
        return self.fetch.getCookiesDict()
