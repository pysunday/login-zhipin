**该仓库代码仅用于个人学习、研究或欣赏。仓库代码作者不保证内容的正确性。通过使用该插件及相关代码产生的风险与仓库代码作者无关。**

**如相关主体（zhipin）不愿意该仓库代码公开，请及时通知仓库作者，予以删除**

# 说明

该插件为sunday生态插件，用于登录zhipin网站，并通过持久化缓存保持登录态。

**注意：由于登录互斥，如在其它非手机终端设备登录过，则该登录态过期，过期后重新登录即可**

## 安装插件

该插件依赖[sunday](https://github.com/pysunday/pysunday), 需要先安装sunday

执行sunday安装目录：`sunday_install pysunday/login-zhipin`

## 引入

```python
from sunday.login.zhipin import Zhipin as ZhipinLogin
```

## 使用

```
In [1]: from sunday.login.zhipin import Zhipin as ZhipinLogin
In [2]: zhipin = ZhipinLogin().login().rs
In [3]: print(zhipin.get('https://www.zhipin.com/wapi/zpuser/wap/getUserInfo.json').json())
Out[3]:
{'code': 0,
 'message': 'Success',
 'zpData': {
    'userId': 用户编号,
    'name': '用户名',
    ...
  }
}
```
