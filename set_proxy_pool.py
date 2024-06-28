import requests
from requests.auth import HTTPBasicAuth

def set_proxy_pool(proxy_pool_url, api_url, auth):
    # auto-proxy-pool配置
    data = {
        "log": {},
        "config": {
            "disableStatusView": "true",
            "httpUseProxy": "false"
        },
        "users": {},
        "upstream": {
            "proxy": {
                "apiUrl": api_url,
                "upstreamFixedAuth": "",
                "requestInterval": "1000ms",
                "lifecycle": "200s",
                "proactive": "50s",
                "proactiveOnIdleSize": 0,
                "proactiveOnIdleCheckInterval": "",
                "maxSize": 3,
                "loadBalanceMultiple": 0,
                "disableOptimizationIp": False,
                "enableReduceReuseIp": False,
                "groupIndex": 0,
                "failSleep": "",
                "failThreshold": 0,
                "disableHttpUseTunnel": False
            }
        },
        "changeRequest": [
            {
                "hostRegex": ".*",
                "loadBalanceInterval": 0,
                "black": False,
                "proxy": "proxy"
            }
        ],
        "dev": {},
        "DefaultFailBack": ""
    }

    # 认证凭证
    auth = HTTPBasicAuth(auth['username'], auth['password'])

    config_url = proxy_pool_url + '/admin/config'

    # 发送PUT请求
    response = requests.put(config_url, auth=auth, json=data)

    if response.status_code == 200:
        print(response.content.decode('utf-8'))
        return True
    else:
        print(f"失败，状态码: {response.status_code}")
        return False

if __name__ == '__main__':
    # content = set_proxy_pool('http://ip:prot', 'http://v2.api.juliangip.com/dynamic/getips?num=1&pt=1&result_type=text&split=2&trade_no=1xxxxxxxxxxx1&sign=exxxxxxxxxxxxxxxxx0', 'user', 'passwd')
    # if content:
    #     print("设置成功")
    pass