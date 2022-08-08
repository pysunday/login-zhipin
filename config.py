# coding: utf-8

# 首页
homeUrl = 'https://zhipin.com/'

# 登录页
loginUrl = 'https://login.zhipin.com/'

# 获取用户信息
getUserInfo = 'https://www.zhipin.com/wapi/zpuser/wap/getUserInfo.json'

# 获取扫码状态
scanUrl = 'https://login.zhipin.com/wapi/zppassport/qrcode/scan?uuid=%s'

# 获取qrId
getSecondKeyUrl = 'https://login.zhipin.com/wapi/zppassport/captcha/getSecondKey?uuid=%s'

# 置换qrId
scanLoginUrl = 'https://login.zhipin.com/wapi/zppassport/qrcode/scanLogin?qrId=%s'

scanSecondUrl = 'https://login.zhipin.com/wapi/zppassport/qrcode/scanSecond?uuid=%s'

dispatcher = 'https://login.zhipin.com/wapi/zppassport/qrcode/dispatcher?qrId=%s'
