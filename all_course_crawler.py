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
url = 'https://ids.ynu.edu.cn/authserver/login?service=http%3A%2F%2Fehall.ynu.edu.cn%2Flogin%3Fservice%3Dhttp%3A%2F%2Fehall.ynu.edu.cn%2Fnew%2Findex.html'
def course_crawler(url):
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get(url)
    driver.find_element_by_id('username').send_keys('20171120028')
    driver.find_element_by_id('password').send_keys('lrtsqa1314A')
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
    kebiaos = []
    for kebiao in driver.find_elements_by_link_text('课表查看'):
        kebiaos.append(kebiao)
    for i,kebiao in enumerate(kebiaos):
        kebiaos[i].click()
        driver.back()
        driver.back()
        time.sleep(2)
        driver.find_element_by_tag_name('a').click()
        locator = (By.TAG_NAME, 'table')
        WebDriverWait(driver, 20, 0.5).until(EC.presence_of_element_located(locator))



if __name__ == '__main__':
    course_crawler(url)