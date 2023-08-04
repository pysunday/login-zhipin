from sunday.core.fetch import Fetch
from sunday.login.zhipin import Zhipin
from sunday.login.zhipin.error import ZhipinLoginError
from sunday.utils import mergeObj, LoginBase
from sunday.core import paths, Logger, enver, exit, cache_name, Auth, getCurrentUser
from sunday.login.zhipin import config

# 用于API接口调用时检查是否已经登录
class CheckLogin():
    def __init__(self, session=None):
        self.fetch = Fetch()
        self.logger = Logger('zhipin是否登录').getLogger()
        if session is not None:
            for key, val in session.items():
                self.fetch.setCookie(key, val, '.zhipin.com')

    def check(self):
        # 执行检查，登录成功返回用户信息
        res = self.fetch.get_json(config.getUserInfo)
        if res.get('code') == 0:
            self.logger.info('登录成功')
            return res.get('zpData')
        else:
            self.logger.warning(res.get('text'))
            raise ZhipinLoginError(20000, other=res.get('message'))
