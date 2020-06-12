"""
author:sqa
time:2020/5/29 18:25

"""
from hashlib import md5
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from PIL import Image
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import requests
import json


url = 'https://ids.ynu.edu.cn/authserver/login?service=http%3A%2F%2Fehall.ynu.edu.cn%2Flogin%3Fservice%3Dhttp%3A%2F%2Fehall.ynu.edu.cn%2Fnew%2Findex.html'
username = '20171120028'
password = 'lrtsqa1314A'
picpath = 'E:\\All Codes\\Github\\iCourse-master\\backend\\pic'
class Chaojiying_Client(object):

    def __init__(self, username, password, soft_id):
        self.username = username
        self.password =  password.encode('utf8')
        self.password = md5(self.password).hexdigest()
        self.soft_id = soft_id
        self.base_params = {
            'user': self.username,
            'pass2': self.password,
            'softid': self.soft_id,
        }
        self.headers = {
            'Connection': 'Keep-Alive',
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0)',
        }

    def PostPic(self, im, codetype):
        """
        im: 图片字节
        codetype: 题目类型 参考 http://www.chaojiying.com/price.html
        """
        params = {
            'codetype': codetype,
        }
        params.update(self.base_params)
        files = {'userfile': ('ccc.jpg', im)}
        r = requests.post('http://upload.chaojiying.net/Upload/Processing.php', data=params, files=files, headers=self.headers)
        return r.json()

    def ReportError(self, im_id):
        """
        im_id:报错题目的图片ID
        """
        params = {
            'id': im_id,
        }
        params.update(self.base_params)
        r = requests.post('http://upload.chaojiying.net/Upload/ReportError.php', data=params, headers=self.headers)
        return r.json()


def course_crawler(url, username, password):
    # chrome_options = Options()
    # chrome_options.add_argument('--headless')
    # chrome_options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(executable_path='D:\\只狼\\chromedriver.exe')  # 调用带参数的谷歌浏览器
    # driver =webdriver.PhantomJS(executable_path='E:\PhantomJS\phantomjs-1.9.7-windows\phantomjs.exe')
    driver.get(url)
    driver.maximize_window()
    driver.save_screenshot(picpath+'1.png')
    driver.find_element_by_id('username').send_keys(username)
    driver.find_element_by_id('password').send_keys(password)
    captchaimg = driver.find_element_by_id('captchaImg')
    left = captchaimg.location['x']
    top = captchaimg.location['y']
    elementWidth = captchaimg.location['x'] + captchaimg.size['width']
    elementHeight = captchaimg.location['y'] + captchaimg.size['height']
    picture = Image.open(picpath+'1.png')
    picture = picture.crop((left, top, elementWidth, elementHeight))
    picture.save(picpath+'2.png')
    chaojiying = Chaojiying_Client('sqasqasqa', 'lrtsqa1314', '905739')
    im = open(picpath+'2.png', 'rb').read()  # 本地图片文件路径 来替换 a.jpg 有时WIN系统须要//
    result = chaojiying.PostPic(im,1902)['pic_str']
    # print(result)
    driver.find_element_by_xpath('//*[@id="captchaResponse"]').send_keys(result)
    driver.find_element_by_tag_name('button').click()
    locator = (By.XPATH,
               '//*[@id="widget-hot-01"]/div[1]/widget-app-item[3]/div/div/div[2]/div[1]')
    WebDriverWait(driver, 20, 0.5).until(EC.presence_of_element_located(locator))
    driver.find_element_by_xpath(
        '//*[@id="widget-hot-01"]/div[1]/widget-app-item[3]/div/div/div[2]/div[1]').click()
    windows = driver.window_handles
    driver.switch_to.window(windows[-1])
    driver.find_element_by_tag_name('a').click()
    locator = (By.TAG_NAME, 'tr')
    WebDriverWait(driver, 20, 0.5).until(EC.presence_of_element_located(locator))
    print(driver.get_cookies())
    str1 = ''
    for cookie in driver.get_cookies():
        str1 += cookie['name'] + '=' + cookie['value'] + ';'
    str1 = str1.strip(';')
    print(str1)
    header = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Encoding': 'gzip,deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cookie': str1,
        'Host': 'ehall.ynu.edu.cn',
        'Origin': 'http://ehall.ynu.edu.cn',
        'User-Agent': 'Mozilla / 5.0(Windows NT 10.0;Win64;x64) AppleWebKit / 537.36(KHTML, likeGecko) Chrome / 83.0.4103.61Safari / 537.36'
    }
    data = json.loads(requests.get('http://ehall.ynu.edu.cn/jwapp/sys/wdkb/modules/xskcb/xskcb.do?XNXQDM=2019-2020-1',
                                   headers=header).text)
    # print(json.loads(requests.get('http://ehall.ynu.edu.cn/jwapp/sys/wdkb/modules/xskcb/xskcb.do?XNXQDM=2019-2020-1',headers=header).text))
    results = data['datas']['xskcb']['rows']
    all_course = []
    for result in results:
        # print(result)
        course = {'KCM': result['KCM'], 'SKJS': result['SKJS'],'KCID':result['JXBID']}
        all_course.append(course)
    driver.close()
    print(all_course)
    return all_course



if __name__ == '__main__':
    course_crawler(url, username, password)
