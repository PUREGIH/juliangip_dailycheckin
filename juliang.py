from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from tencentcaptcha import Tencent
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from set_proxy_pool import set_proxy_pool
import urllib.parse
import time
import json
import os
import zipfile
import requests
import hashlib

# 创建代理插件
def create_proxy_extension(proxy_host, proxy_port, proxy_user, proxy_pass):
    manifest_json = """
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Chrome Proxy",
        "permissions": [
            "proxy",
            "tabs",
            "unlimitedStorage",
            "storage",
            "<all_urls>",
            "webRequest",
            "webRequestBlocking"
        ],
        "background": {
            "scripts": ["background.js"]
        }
    }
    """

    background_js = f"""
    var config = {{
            mode: "fixed_servers",
            rules: {{
            singleProxy: {{
                scheme: "http",
                host: "{proxy_host}",
                port: parseInt({proxy_port})
            }},
            bypassList: ["localhost"]
            }}
        }};
    chrome.proxy.settings.set({{value: config, scope: "regular"}}, function() {{}});
    function callbackFn(details) {{
        return {{
            authCredentials: {{
                username: "{proxy_user}",
                password: "{proxy_pass}"
            }}
        }};
    }}
    chrome.webRequest.onAuthRequired.addListener(
                callbackFn,
                {{urls: ["<all_urls>"]}},
                ['blocking']
    );
    """

    pluginfile = 'proxy_auth_plugin.zip'

    with zipfile.ZipFile(pluginfile, 'w') as zp:
        zp.writestr("manifest.json", manifest_json)
        zp.writestr("background.js", background_js)

    return pluginfile
# 读取配置文件
def read_config(file_path):
    try:
        abs_path = os.path.abspath(file_path)
        print(f"加载配置：{abs_path}")
        with open(file_path, 'r', encoding='utf-8') as file:
            config = json.load(file)
        return config
    except FileNotFoundError:
        print(f"配置文件 {file_path} 找不到。")
    except json.JSONDecodeError:
        print(f"从文件 {file_path} 解码JSON时出错。")
    return None
# 获取配置信息
def get_config(config, key, default=None):
    value = config.get(key, default)
    if value is None:
        raise ValueError(f"没有配置 {key}")
    return value
# 检查代理配置是否有效
def is_proxy_valid(config):
    keys = ['proxy_address', 'proxy_username', 'proxy_password']
    for key in keys:
        if key not in config or not config[key]:
            return False
    return True
# wxpusher消息推送
def wxpush(title, text, uids, appToken):
    content = f'''<!DOCTYPE html> <html lang="zh-CN"> <head> <meta charset="UTF-8"> <title>{title}</title> <style type=text/css> body {{ background-image: linear-gradient(120deg, #1E90FF 0%, #a5d0e5 100%); background-size: 300%; animation: bgAnimation 6s linear infinite; }} @keyframes bgAnimation {{ 0% {{background-position: 0% 50%;}} 50% {{background-position: 100% 50%;}} 100% {{background-position: 0% 50%;}} }} </style> </head> <body> <pre>{text}</pre><br> <br> </body> </html> '''
    urlpust = 'http://wxpusher.zjiecode.com/api/send/message'
    for uid in uids:
        datapust = {
            "appToken": appToken,
            "content": content,
            "summary": title,
            "contentType": 2,
            "uids": [uid]
        }
        try:
            response = requests.post(url=urlpust, json=datapust)
            if response.status_code == 200:
                print('推送成功！')
            else:
                print('推送失败！')
        except requests.RequestException:
            print('推送失败！')

# 解析字符串
def parse_string(input_string, error_message):
    parts = input_string.split('@')
    if len(parts) < 2:
        raise ValueError(error_message)
    return parts
# 解析账号
def parse_account(account):
    parts = parse_string(account, f"账号格式错误: {account}")
    username, password = parts[0], parts[1]
    uids = parts[2] if len(parts) > 2 and parts[2] else None
    return username, password, uids
# 解析API配置
def parse_api_config(config):
    parts = parse_string(config, f"API配置格式错误: {config}")
    trade_no, key = parts[0], parts[1]
    return trade_no, key

# 配置Chrome选项
def configure_chrome_options(use_proxy, proxy_address, proxy_username, proxy_password):
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    if use_proxy:
        proxy_host, proxy_port = proxy_address.split(':')
        proxy_plugin = create_proxy_extension(proxy_host, proxy_port, proxy_username, proxy_password)
        chrome_options.add_extension(proxy_plugin)
    return chrome_options

class Juliang_net(Tencent):
    """
    基于巨量IP的签到类
    """
    def __init__(self, url, username, password, browser):
        super().__init__(url, username, password, browser)
        self.browser = browser  # 设置浏览器对象
        self.wait = WebDriverWait(self.browser, 30)  # 显式等待 30 秒

    def set_info(self):
        """
        填写表单信息
        """
        self.browser.get(url=self.url)
        try:
            # 输入账号密码
            print("正在输入用户名和密码...")
            input_username = self.wait.until(EC.presence_of_element_located((By.NAME, 'username')))
            input_password = self.wait.until(EC.presence_of_element_located((By.NAME, 'password')))
            input_username.send_keys(self.username)
            input_password.send_keys(self.password)

            # 点击登录按钮
            print("单击登录按钮...")
            login_button = self.browser.find_element(By.ID, 'login')
            login_button.click()
            
            # 增加延迟，确保页面成功登录
            time.sleep(5)

            print("正在等待可单击的签到按钮...")
            sign_button = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'free_card_2')))
            sign_button.click()
            print("已单击“签到”按钮")
            time.sleep(10)
            
        except Exception as e:
            print('错误:', e)
            print("准备重试...")
            self.set_info()
    # 构建URL
    @staticmethod
    def build_api_url(trade_no, key, num=1, **options):
        """
        构建URL
        """
        params = {
            'trade_no': trade_no,
            'num': num,
            **options
        }

        sign = Juliang_net.md5_sign(params, key)
        query_string = urllib.parse.urlencode(params) + "&sign=" + sign

        url = f'http://v2.api.juliangip.com/dynamic/getips?{query_string}'
        return url

    @staticmethod
    def md5_sign(params, secret):
        sign_content = Juliang_net.get_sign_content(params)
        return hashlib.md5((sign_content + '&key=' + secret).encode('utf-8')).hexdigest()

    @staticmethod
    def get_sign_content(params):
        params.pop('sign', None)  # 删除 sign
        sorted_params = sorted(params.items())
        sign_content = '&'.join([f"{k}={str(v)}" for k, v in sorted_params if str(v) is not None and not str(v).startswith('@')])
        return sign_content

    # def get_url(self, api_key):
    #     """
    #     获取API URL
    #     """
    #     try:
    #         # 进入 “包时” 页面
    #         self.browser.get('https://www.juliangip.com/users/product/time')

    #         # 增加延迟确保页面完全载入
    #         time.sleep(5)

    #         # 进入提取页
    #         get_url_page = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div[2]/table/tbody/tr/td[9]/a[1]')))
    #         get_url_page.click()

    #         # 继续延迟3秒
    #         time.sleep(3)

    #         # 控制滚动页面的高度
    #         target_height = 700  # 目标滚动高度
    #         scroll_increment = 250  # 每次滚动的高度
    #         current_position = 0

    #         while current_position < target_height:
    #             self.browser.execute_script(f"window.scrollTo(0, {current_position});")
    #             current_position += scroll_increment
    #             time.sleep(1)  # 等待滚动加载完成

    #         # 点击提取API按钮
    #         extract_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="api"]/div[1]/div[1]/div[1]/div[2]/form/div[11]/div/button/span')))
    #         extract_button.click()

    #         time.sleep(3)

    #         # 关闭弹窗
    #         quit_msg = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'el-message-box__close')))
    #         quit_msg.click()

    #         # 清空剪贴板内容
    #         pyperclip.copy('')

    #         time.sleep(2)

    #         # 点击复制链接按钮
    #         copy_button = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'el-icon-document-copy')))
    #         copy_button.click()
            
    #         # 增加延迟以确保内容复制完成
    #         time.sleep(2)

    #         # 获取剪贴板内容
    #         base_url = pyperclip.paste()
    #         print("url:", base_url)

    #         # 定位业务编号元素
    #         trade_no_element = self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/div[2]/table/tbody/tr/td[2]')))
    #         # 获取业务编号
    #         trade_no = trade_no_element.text

    #         # 业务编号是否为空
    #         if not trade_no:
    #             print("业务编号为空")
    #             return None

    #         #构建URL
    #         new_url = Juliang_net.build_url(trade_no, 1, api_key, sqlit=2)
    #         print("api url:", new_url)


    #     except Exception as e:
    #         print(f"操作时出错：{e}")
    #         return None

# 主函数
def main():
    # 加载配置文件
    config = read_config('config.json') or exit("无法加载配置。")

    # 读取auto-proxy-pool配置
    proxy_pool_config = get_config(config, 'auto_proxy_pool_config')
    proxy_pool_url = proxy_pool_config['proxy_pool_url']
    auth = proxy_pool_config['auth']

    # 读取巨量IP账号和API配置
    juliang_account = get_config(config, 'juliang_account')
    juliang_api_config = get_config(config, 'juliang_api_config')

    # 读取wxpusher配置
    wxpush_config = get_config(config, 'wxpush_config', {})
    appToken = wxpush_config.get('appToken', '')
    title = wxpush_config.get('title', '巨量IP签到')

    # 读取代理配置
    proxy_config = get_config(config, 'proxy_config', {})

    # 检查代理配置是否有效
    use_proxy = is_proxy_valid(proxy_config)
    if use_proxy:
        proxy_address = proxy_config['proxy_address']
        proxy_username = proxy_config['proxy_username']
        proxy_password = proxy_config['proxy_password']
        print("使用代理设置：")
        print(f"IP: {proxy_address}")
        print(f"用户名: {proxy_username}")
        print(f"密码: {proxy_password}")
    else:
        proxy_address = None
        proxy_username = None
        proxy_password = None
        print("代理配置不完整，不使用代理。")

    # 开始执行签到操作
    if len(juliang_account) != len(juliang_api_config):
        raise ValueError("账号和API KEY数量不匹配")

    url = 'https://www.juliangip.com/user/login'

    for account, api_config in zip(juliang_account, juliang_api_config):
        print(f"正在处理帐户: {account}")

        username, password, uids = parse_account(account)
        trade_no, api_key = parse_api_config(api_config)

        # 配置Chrome选项
        chrome_options = configure_chrome_options(use_proxy, proxy_address, proxy_username, proxy_password)

        # 手动指定chromedriver路径
        chromedriver_path = r'C:\Users\windowsuser\AppData\Local\Google\Chrome\Application\chromedriver.exe'
        service = Service(chromedriver_path)

        # 创建浏览器实例
        try:
            browser = webdriver.Chrome(service=service, options=chrome_options)
            tencent = Juliang_net(url, username, password, browser)

            # 过滑块验证
            tencent.re_start()

            # 登录填表
            # tencent.set_info()

            # 提取url操作
            api_url = tencent.build_api_url(trade_no, api_key, split=2, area='四川')

            # 保存auto-proxy-pool
            save_pool = set_proxy_pool(proxy_pool_url, api_url, auth)

            if save_pool:
                # wxpusher消息推送
                if uids:
                    wxpush(title, api_url, [uids], appToken)

        except Exception as e:
            raise Exception(f"处理帐户 {username} 时发生错误: {e}")

        finally:
            # 确保关闭浏览器
            tencent.end()
if __name__ == '__main__':
    main()