from hashlib import md5
import requests
import json
import re


def transfer(username, password):
    j_password = md5(('UIMS' + username + password).encode()).hexdigest()
    pwd_strenth = 0
    if len(password) < 4 or username == password or password == '000000':
        pass
    else:
        if any(map(lambda x: x.isdigit(), password)):
            pwd_strenth += 1
        if any(map(lambda x:x.isalpha(), password)):
            pwd_strenth += 1
        if not password.isalnum():
            pwd_strenth += 1
        if len(password) < 6 and pwd_strenth:
            pwd_strenth -= 1
    return j_password, pwd_strenth


class UIMS(object):
    def __init__(self, user, pwd):
        self.session = requests.session()
        self.login(user, pwd)

    def login(self, username, password):
        s = self.session
        s.get('http://uims.jlu.edu.cn/ntms/')
        j_password, pwd_strength = transfer(username, password)
        cookies = {
            'loginPage': 'userLogin.jsp',
            'alu': username,
            'pwdStrength': str(pwd_strength),
        }
        requests.utils.add_dict_to_cookiejar(s.cookies, cookies)

        post_data = {
            'j_username': username,
            'j_password': j_password,
            'mousePath': 'TFwABSAAAtRAQBFRAwBNRBQBVRCABdRDABlREABtQFgB1QHAB9PJQCFOLQCNONQCVNPQCdNRgClNUACtNWQC1NYgC9NaQDFOcADNQdgDVQegDdSfwDlUggDtVhQD1VhwD9WiQEFWigENWiwEdWjAElWjQE1WjgFFWkAFNWkgFUWlAFdWlwFkWmgFtWngF1WogF9WpgGFWqgGNWrgGVWtAGdWugGlWwAGtVxgG1VzgG9U1gHFU3gHNU5QHVT7AHdXDAEp'
        }
        r = s.post('http://uims.jlu.edu.cn/ntms/j_spring_security_check', data=post_data)
        message = re.findall('<span class="error_message" id="error_message">(.*?)</span>', r.text)
        if message:
            raise ValueError(message[0])

    def get_course(self, save_file=None):
        s = self.session
        r = s.post('http://uims.jlu.edu.cn/ntms/action/getCurrentUserInfo.do')
        user_info = json.loads(r.text)
        post_data = {
            "tag": "search@teachingTerm",
            "branch": "byId",
            "params": {
                "termId": user_info['defRes']['term_l']
            }
        }
        headers = {'Content-Type': 'application/json'}
        r = s.post('http://uims.jlu.edu.cn/ntms/service/res.do', json.dumps(post_data), headers=headers)
        start_date = json.loads(r.text)['value'][0]['startDate'].split('T')[0]

        post_data["params"]["studId"] = user_info['userId']
        post_data["branch"] = "default"
        post_data["tag"] = "teachClassStud@schedule"
        r = s.post('http://uims.jlu.edu.cn/ntms/service/res.do', json.dumps(post_data), headers=headers)
        if save_file:
            with open(save_file, 'w') as f:
                json.dump([start_date, json.loads(r.text)['value']], f)
        return start_date, json.loads(r.text)['value']


if __name__ == '__main__':
    # user, pwd = input().split(',')
    user, pwd = 'username', 'password'
    print(UIMS(user, pwd).get_course(save_file='courses.json'))

