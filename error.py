# coding: utf-8
from sunday.core.getException import getException

errorMap = {
        20000: '未登录',
        20001: 'App端扫码超时',
        20002: '参数缺失',
        20003: 'App端取消登录',
        20004: 'App端确认超时',
        -1: '未知错误',
        }

captchaErrorMax = 4

ZhipinLoginError = getException(errorMap, ['stack', 'origin'])

def getErrorObj(e):
    return {
            **dict(e),
            'success': False,
            }

