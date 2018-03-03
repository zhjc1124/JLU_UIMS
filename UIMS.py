from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import json

chrome_options = Options()
chrome_options.add_argument('--headless')


class UIMS(object):
    def __init__(self, user, pwd):
        self.cookies = self.login(user, pwd)
        self.session = requests.session()
        requests.utils.add_dict_to_cookiejar(self.session.cookies, self.cookies)

    def login(self, username, password):
        driver = webdriver.Chrome(chrome_options=chrome_options)
        driver.get('http://uims.jlu.edu.cn')
        # 等待页面加载完毕
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "script")))
        print("success login")
        js = 'dojo.byId("txtUserName").focus();' \
             'var form = dojo.byId("loginForm");' \
             'form.j_username.value = "%s";' \
             'form.pwdPlain.value = "%s";' \
             'loginPage.clickSubmit();' % (username, password)
        driver.execute_script(js)
        cookies = {}
        for c in driver.get_cookies():
            if c['name'] != 'pwdStrength':
                cookies[c['name']] = c['value']
        return cookies

    def get_course(self):
        s = self.session
        r = s.post('http://uims.jlu.edu.cn/ntms/action/getCurrentUserInfo.do')
        user_info = json.loads(r.text)
        post_data = {
            "tag": "teachClassStud@schedule",
            "branch": "default",
            "params": {
                "termId": user_info['defRes']['term_l'],
                "studId": user_info['userId']}
        }
        headers = {'Content-Type': 'application/json;charset=UTF-8'}
        r = s.post('http://uims.jlu.edu.cn/ntms/service/res.do', json.dumps(post_data), headers=headers)
        return json.loads(r.text)['value']


if __name__ == '__main__':
    # user, pwd = input().split(',')
    user, pwd = '52151126', '11171x'
    UIMS(user, pwd).get_course()

