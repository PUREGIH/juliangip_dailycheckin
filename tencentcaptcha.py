# -*- coding: utf-8 -*-
"""
@author:Pineapple

@contact:cppjavapython@foxmail.com

@time:2020/8/2 17:29

@file:tencentcaptcha.py

@desc: login with Tencen .
"""
import base64
import random
import time

import re
import requests
import os

from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC  # 显性等待
from selenium.webdriver.support.wait import WebDriverWait

class Tencent:
    """
    识别腾讯验证码
    """

    def __init__(self, ttshitu_username, ttshitu_password, browser=None):
        """
        初始化浏览器配置，声明变量

        :param browser: 浏览器实例
        """
        self.browser = browser if browser else webdriver.Chrome()
        self.wait = WebDriverWait(self.browser, 20)
        self.ttshitu_username = ttshitu_username
        self.ttshitu_password = ttshitu_password

    def end(self):
        """
        结束后退出，可选
        """
        if self.browser:
            self.browser.quit()

    def set_info(self):
        """
        填写个人信息，在子类中完成
        """
        pass

    def tx_code(self):
        """
        主要部分，函数入口
        """
        self.set_info()
        self.wait.until(EC.presence_of_element_located((By.ID, 'tcaptcha_transform_dy')))  # 等待 iframe
        self.browser.switch_to.frame(self.browser.find_element(By.ID, 'tcaptcha_iframe_dy'))  # 加载 iframe
        time.sleep(2)
        style = self.browser.find_element(By.ID, 'slideBg').get_attribute("style")
        match = re.search('background-image: url\("(.*?)"\);', style)
        try:
            bk_block = match.group(1)
            if Tencent.save_img(bk_block):
                dex = self.get_pos()
                if dex:
                    track_list = Tencent.get_track(dex)
                    time.sleep(0.5)
                    slid_ing = self.browser.find_element(By.XPATH, '//*[@id="tcOperation"]/div[6]')  # 滑块定位
                    ActionChains(self.browser).click_and_hold(on_element=slid_ing).perform()  # 鼠标按下
                    time.sleep(0.2)
                    for track in track_list:
                        ActionChains(self.browser).move_by_offset(xoffset=track, yoffset=0).perform()  # 鼠标移动到距离当前位置（x,y）
                    time.sleep(1)
                    ActionChains(self.browser).release(on_element=slid_ing).perform()  # print('第三步,释放鼠标')
                    time.sleep(5)
                    return True
                else:
                    self.re_start()
            else:
                print('缺口图片捕获失败')
                return False
        except Exception as e:
            print('错误:', e.args)
            return False

    @staticmethod
    def save_img(bk_block):
        """
        保存图片

        :param bk_block: 图片url
        :return: bool类型，是否被保存
        """
        try:
            img = requests.get(bk_block).content
            with open("bg.jpeg", 'wb') as f:
                f.write(img)
            return True
        except requests.exceptions.RequestException as e:
            print(f"获取图片时出错： {e}")
            return False
        except Exception as e:
            print(f"保存图像时出错： {e}")
            return False

    def get_pos(self):
        """
        识别缺口
        注意：网页上显示的图片为缩放图片，缩放 50% 所以识别坐标需要 0.5

        :return: 缺口位置
        """
        # image = cv.imread('bg.jpeg')
        # # 高斯滤波
        # blurred = cv.GaussianBlur(image, (5, 5), 0)
        # # 边缘检测
        # canny = cv.Canny(blurred, 200, 400)
        # # 轮廓检测
        # contours, hierarchy = cv.findContours(
        #     canny, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        # for i, contour in enumerate(contours):
        #     m = cv.moments(contour)
        #     if m['m00'] == 0:
        #         cx = cy = 0
        #     else:
        #         cx, cy = m['m10'] / m['m00'], m['m01'] / m['m00']
        #     if 6000 < cv.contourArea(contour) < 8000 and 370 < cv.arcLength(contour, True) < 390:
        #         if cx < 400:
        #             continue
        #         x, y, w, h = cv.boundingRect(contour)  # 外接矩形
        #         cv.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)
        #         # cv.imshow('image', image)  # 显示识别结果
        #         print('【缺口识别】 {x}px'.format(x=x / 2))
        #         return x / 2
        # return 0
        # 判断当前环境是windows还是linux
        imul = ''
        if os.name == 'nt':
            imul = 'bg.jpeg'
        elif os.name == 'posix':
            imul = '/ql/scripts/root_littlepythonsheep/bg.jpeg'
        with open(imul, 'rb') as f:
            base64_data = base64.b64encode(f.read())
            b64 = base64_data.decode()
            
        # 调用验证码识别API
        data = {
            "username": self.ttshitu_username,
            "password": self.ttshitu_password,
            "typeid": 33,
            "image": b64
        }
        try:
            response = requests.post("http://api.ttshitu.com/predict", json=data)
            response.raise_for_status()  # 检查请求是否成功
            result = response.json()
        except requests.RequestException as e:
            print(f"请求失败: {e}")
            return 0
        
        # 解析识别结果
        try:
            dex = result["data"]["result"]
            dex = int(dex)
            dex -= 60
            print('【缺口识别】 {x}px'.format(x=dex / 2))
            return dex / 2
        except (KeyError, ValueError) as e:
            print(f"响应分析错误：{e}")
            return 0

    @staticmethod
    def get_track(distance):
        """
        轨迹方程

        :param distance: 距缺口的距离
        :return: 位移列表
        """
        # distance -= 75  # 初始位置
        # 初速度
        v = 0
        # 单位时间为0.2s来统计轨迹，轨迹即0.2内的位移
        t = 0.2
        # 位移/轨迹列表，列表内的一个元素代表0.2s的位移
        tracks = []
        # 当前的位移
        current = 0
        # 到达mid值开始减速
        mid = distance * 4 / 5

        distance += 10  # 先滑过一点，最后再反着滑动回来
        # a = random.randint(1,3)
        while current < distance:
            if current < mid:
                # 加速度越小，单位时间的位移越小,模拟的轨迹就越多越详细
                # a = random.randint(2, 4)  # 加速运动
                a = 3
            else:
                # a = -random.randint(3, 5)  # 减速运动
                a = -2
            # 初速度
            v0 = v
            # 0.2秒时间内的位移
            s = v0 * t + 0.5 * a * (t ** 2)
            # 当前的位置
            current += s
            # 添加到轨迹列表
            tracks.append(round(s))

            # 速度已经达到v,该速度作为下次的初速度
            v = v0 + a * t

        # 反着滑动到大概准确位置
        for i in range(4):
            tracks.append(-random.randint(2, 3))
        for i in range(4):
            tracks.append(-random.randint(1, 3))
        return tracks

    def move_to(self, index):
        """
        移动滑块

        :param index:
        :return:
        """
        pass

    def re_start(self):
        """
        准备开始

        :return: None
        """
        self.tx_code()
        # self.end()