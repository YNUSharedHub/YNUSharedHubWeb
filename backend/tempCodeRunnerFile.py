 = driver.find_element_by_id('captchaImg')
    # left = captchaimg.location['x']
    # top = captchaimg.location['y']
    # elementWidth = captchaimg.location['x'] + captchaimg.size['width']
    # elementHeight = captchaimg.location['y'] + captchaimg.size['height']
    # picture = Image.open(picpath+'1.png')
    # picture = picture.crop((left, top, elementWidth, elementHeight))
    # picture.save(picpath+'2.png')
    # chaojiying = Chaojiying_Client('lrtsqa', 'lrtsqa1314', '905592')
    # im = open(picpath+'2.png', 'rb').read()  # 本地图片文件路径 来替换 a.jpg 有时WIN系统须要//
    # result = chaojiying.PostPic(im,1902)['pic_str']
    # # print(result)
    # driver.find_element_by_xpath('//*[@id="captchaResponse"]').send_keys(result)