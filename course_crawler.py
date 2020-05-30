"""
author:sqa
time:2020/5/29 18:25

"""
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
url = 'https://ids.ynu.edu.cn/authserver/login?service=http%3A%2F%2Fehall.ynu.edu.cn%2Flogin%3Fservice%3Dhttp%3A%2F%2Fehall.ynu.edu.cn%2Fnew%2Findex.html'
def course_crawler(url):
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get(url)
    driver.find_element_by_id('username').send_keys('20171120028')
    driver.find_element_by_id('password').send_keys('lrtsqa1314A')
    driver.find_element_by_tag_name('button').click()
    locator = (By.XPATH,'/html/body/article[5]/section/div[2]/div[1]/div[3]/pc-card-html-4786697535230905-01/amp-w-frame/div/div[2]/div/div[1]/widget-app-item[2]/div/div/div[2]/div[1]')
    WebDriverWait(driver,20,0.5).until(EC.presence_of_element_located(locator))
    driver.find_element_by_xpath('/html/body/article[5]/section/div[2]/div[1]/div[3]/pc-card-html-4786697535230905-01/amp-w-frame/div/div[2]/div/div[1]/widget-app-item[2]/div/div/div[2]/div[1]').click()
    windows = driver.window_handles
    driver.switch_to.window(windows[-1])
    driver.find_element_by_tag_name('a').click()
    locator = (By.TAG_NAME,'tr')
    WebDriverWait(driver,20,0.5).until(EC.presence_of_element_located(locator))
    for course in driver.find_elements_by_tag_name('tr'):
        print(course.text)


if __name__ == '__main__':
    course_crawler(url)