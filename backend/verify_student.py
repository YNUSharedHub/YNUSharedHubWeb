"""
author:sqa
time:2020/6/2 12:29

"""
import requests
from PIL import Image
from hashlib import md5
from selenium import webdriver
url = 'https://ids.ynu.edu.cn/authserver/login?service=http%3A%2F%2Fehall.ynu.edu.cn%2Flogin%3Fservice%3Dhttp%3A%2F%2Fehall.ynu.edu.cn%2Fnew%2Findex.html'
import requests
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

def verify_student(username,password):
    driver = webdriver.Chrome(executable_path='D:\只狼\chromedriver.exe')  # 调用带参数的谷歌浏览器
    driver.get(url)
    driver.maximize_window()
    driver.save_screenshot('E:\\All Codes\\Github\\iCourse-master\\backend\\pic\\1.png')
    driver.find_element_by_id('username').send_keys(username)
    driver.find_element_by_id('password').send_keys(password)
    captchaimg = driver.find_element_by_id('captchaImg')
    left = captchaimg.location['x']
    top = captchaimg.location['y']
    elementWidth = captchaimg.location['x'] + captchaimg.size['width']
    elementHeight = captchaimg.location['y'] + captchaimg.size['height']
    picture = Image.open('E:\\All Codes\\Github\\iCourse-master\\backend\\pic\\1.png')
    picture = picture.crop((left, top, elementWidth, elementHeight))
    picture.save('E:\\All Codes\\Github\\iCourse-master\\backend\\pic\\2.png')
    chaojiying = Chaojiying_Client('lrtsqa', 'lrtsqa1314', '905592')
    im = open('E:\\All Codes\\Github\\iCourse-master\\backend\\pic\\2.png',
              'rb').read()  # 本地图片文件路径 来替换 a.jpg 有时WIN系统须要//
    result = chaojiying.PostPic(im, 1902)['pic_str']
    driver.find_element_by_xpath('//*[@id="captchaResponse"]').send_keys(result)
    driver.find_element_by_tag_name('button').click()
    try:
        driver.find_element_by_xpath(
            '//*[@id="msg"]')
        print(2)
        driver.quit()
        return False
    except :
        print(1)
        driver.quit()
        return True
if __name__ == '__main__':
    verify_student('20171120028','lrtsqa1314A')