"""
author:sqa
time:2020/5/30 11:25

"""
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
import json
import requests

import os
import sys
import django
pathname = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, pathname)
sys.path.insert(0, os.path.abspath(os.path.join(pathname, '..')))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "iCourse.settings")
django.setup()
from backend.models import Course_Table,College,Course
username = '20171120028'
password = 'lrtsqa1314A'
url = 'https://ids.ynu.edu.cn/authserver/login?service=http%3A%2F%2Fehall.ynu.edu.cn%2Flogin%3Fservice%3Dhttp%3A%2F%2Fehall.ynu.edu.cn%2Fnew%2Findex.html'


def course_crawler(url, username, password):
    driver = webdriver.Chrome(executable_path='D:\\只狼\\chromedriver.exe')
    driver.get(url)
    driver.find_element_by_id('username').send_keys(username)
    driver.find_element_by_id('password').send_keys(password)
    time.sleep(5)
    driver.find_element_by_tag_name('button').click()
    locator = (By.XPATH, '//*[@id="ampPersonalAsideLeftMini"]/div/div[2]')
    WebDriverWait(driver, 20, 0.5).until(EC.presence_of_element_located(locator))
    time.sleep(5)
    driver.find_element_by_xpath('//*[@id="ampPersonalAsideLeftMini"]/div/div[2]').click()
    # driver.find_element_by_xpath('//*[@id="ampPersonalAsideLeftTabHead"]/div[2]/span').click()
    time.sleep(2)
    driver.find_element_by_xpath('//*[@id="ampPersonalAsideLeftAllCanUseAppsTabContent"]/div[1]/div[17]/h5').click()
    windows = driver.window_handles
    driver.switch_to.window(windows[-1])
    driver.find_element_by_tag_name('a').click()
    locator = (By.TAG_NAME, 'table')
    WebDriverWait(driver, 20, 0.5).until(EC.presence_of_element_located(locator))
    driver.find_element_by_xpath('/html/body/header/header[1]/div/div/div[4]/div[4]/a[1]/div').click()
    locator = (By.TAG_NAME, 'table')
    WebDriverWait(driver, 20, 0.5).until(EC.presence_of_element_located(locator))
    print(driver.get_cookies())
    str1 = ''
    for cookie in driver.get_cookies():
        str1 += cookie['name'] + '=' + cookie['value'] + ';'
    str1 = str1.strip(';')
    header = {
        'Accept': 'application / json, text / javascript, * / *; q = 0.01',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh - CN, zh;q = 0.9',
        'Cookie': str1,
        'Host': 'ehall.ynu.edu.cn',
        'User-Agent': 'Mozilla / 5.0(Windows NT 10.0;Win64;x64) AppleWebKit / 537.36(KHTML, likeGecko) Chrome / 83.0.4103.61Safari / 537.36'
    }
    url = 'http://ehall.ynu.edu.cn/jwapp/sys/kcbcx/modules/ydjkb/xqkcbcx.do'

    all_course = []
    for num in range(0, 42):
        num = str(num)
        form_data = {
            'querySetting': '[{"name": "XNXQDM", "caption": "学年学期", "linkOpt": "AND", "builderList": "cbl_m_List","builder": "m_value_equal", "value": "2019-2020-1"}]',
            'pageSize': '100',
            'pageNumber': num,
        }
        data = json.loads(requests.post(url, headers=header, data=form_data).text)
        results = data['datas']['xqkcbcx']['rows']
        for result in results:
            print(result['KKDWDM_DISPLAY'])
            try:
                college_id = College.objects.get(name=result['KKDWDM_DISPLAY']).id
                course = {'name': result['KCM'], 'lessonsAddress': result['SKDD'], 'teacher': result['JSJS'],
                          'college_id':college_id,'credit':float(result['XF']),'elective':1 if result['KCXZDM_DISPLAY']=='必修' else 0,
                          'course_code':result['JXBID'],'visit_count':0,'XQ1': result['XQ1'], 'XQ2': result['XQ2'], 'XQ3': result['XQ3'], 'XQ4': result['XQ4'],
            'XQ5': result['XQ5']
                          }
                all_course.append(course)
            except :
                pass


    return all_course






if __name__ == '__main__':
    allcourses = course_crawler(url, username, password)
    print(allcourses)
    for course in allcourses:
        try:
            course_table = Course.objects.create(**course)
        except :
            pass
