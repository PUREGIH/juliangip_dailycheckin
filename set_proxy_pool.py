import requests
from requests.auth import HTTPBasicAuth


def set_proxy_pool(proxy_pool_url, api_url_list, auth):
    # auto-proxy-pool配置
    data = {
        "log": {},
        "config": {
            "disableStatusView": "true",
            "httpUseProxy": "false"
        },
        "users": {},
        "upstream": {},
        "changeRequest": [],
        "dev": {},
        "DefaultFailBack": ""
    }

    # 动态生成 upstream 配置
    proxy_names = []
    for index, api_url in enumerate(api_url_list):
        proxy_name = f"proxy{index + 1}"
        proxy_names.append(proxy_name)
        data["upstream"][proxy_name] = {
            "apiUrl": api_url,
            "upstreamFixedAuth": "",
            "requestInterval": "1000ms",
            "lifecycle": "50s",
            "proactive": "20s",
            "proactiveOnIdleSize": 0,
            "proactiveOnIdleCheckInterval": "",
            "maxSize": 3,
            "loadBalanceMultiple": 1,
            "disableOptimizationIp": False,
            "enableReduceReuseIp": False,
            "groupIndex": 0,
            "failSleep": "",
            "failThreshold": 0,
            "disableHttpUseTunnel": False
        }

    # 将所有上游以逗号分隔的形式添加到 changeRequest
    data["changeRequest"].append({
        "hostRegex": ".*",
        "loadBalanceInterval": 0,
        "black": False,
        "proxy": ",".join(proxy_names)
    })

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
