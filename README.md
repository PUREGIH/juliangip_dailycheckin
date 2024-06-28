# 巨量IP签到

---
## 介绍
windows下的巨量IP签到脚本

滑块验证使用`Ttshitu`API接口

## 依赖
```
python -m venv env
env\Scripts\activate
pip install -r requirements.txt
```
## 使用
打开`config.json`配置文件编辑:
```json
{
  "juliang_account": [
    "phonenumber@passwd@wxpusherUID"
  ],
  "ttshitu_config": {
    "username": "xxxx",
    "password": "xxxx"
  },
  "proxy_config": {
    "proxy_address": "ip:port",
    "proxy_username": "user",
    "proxy_password": "passwd"
  },
  "wxpush_config": {
    "appToken": "xxxxxx",
    "title": "巨量IP签到"
  },
  "juliang_api_config": ["trade_no@API_KEY"
  ],
  "auto_proxy_pool_config": {
    "proxy_pool_url": "http://ip:port",
    "auth": {
      "username": "admin",
      "password": "passwd"
    }
  }
}
```
- `juliang_account`巨量账号，`wxpusherUID`wxpusher推送的UID，可以不填。
- `ttshitu_config`图图打码API配置。
- `proxy_config`代理配置，可以不填。
- `wxpush_config`wxpusher推送配置，可以不填。
- `juliang_api_config`巨量API，`trade_no`为业务编号，`API_KEY`为API密钥。
- `auto_proxy_pool_config`用于自动提交PROXY API到代理池，可以不填。
编辑`juliang.py`文件，修改第344行：
```python
# 修改为你的chromedriver路径
chromedriver_path = r'C:\Users\windowsuser\AppData\Local\Google\Chrome\Application\chromedriver.exe'
```

运行脚本：

`python juliang.py`

添加到计划任务：

项目文件夹下新建`*.bat`文件，编辑：
```bat
@echo off
set VIRTUAL_ENV=your_path\juliang_env
set PATH=%VIRTUAL_ENV%\Scripts;%PATH%
call %VIRTUAL_ENV%\Scripts\activate
python your_path\juliangip_dailycheckin\juliang.py
call %VIRTUAL_ENV%\Scripts\deactivate
```
将`*.bat`添加到计划任务。