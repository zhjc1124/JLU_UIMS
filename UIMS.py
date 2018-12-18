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

    def auto_evaluate(self):
        s = self.session
        post_data = {
            "tag": "student@evalItem",
            "branch": "self",
            "params": {
                "blank": "Y"
            }
        }
        headers = {'Content-Type': 'application/json'}
        r = s.post('http://uims.jlu.edu.cn/ntms/service/res.do', data=json.dumps(post_data), headers=headers)
        eval_info = json.loads(r.text)['value']
        for course in eval_info:
            # url = course['evalActTime']['evalGuideline']['paperUrl']
            id = course['evalItemId']
            post_url = 'http://uims.jlu.edu.cn/ntms/action/eval/eval-with-answer.do'
            post_data = {"guidelineId": 120, "evalItemId": "%s" % id,
                         "answers": {"prob11": "A", "prob12": "A", "prob13": "N", "prob14": "A",
                                     "prob15": "A", "prob21": "A", "prob22": "A", "prob23": "A", "prob31": "A",
                                     "prob32": "A", "prob33": "A", "prob41": "A", "prob42": "A", "prob43": "A",
                                     "prob51": "A", "prob52": "A", "sat6": "A", "mulsel71": "K", "advice72": "无",
                                     "prob73": "Y"},
                         "clicks": {"_boot_": 0, "prob11": 49050, "prob12": 50509,
                                    "prob13": 52769, "prob14": 54833, "prob15": 58783,
                                    "prob21": 61488, "prob22": 62599,
                                    "prob23": 64182, "prob31": 68422, "prob32": 70505,
                                    "prob33": 71589, "prob41": 73270,
                                    "prob42": 76550, "prob43": 79323, "prob51": 90550,
                                    "prob52": 94748, "sat6": 96238,
                                    "mulsel71": 101482, "prob73": 103695}}
            s.post(post_url, data=json.dumps(post_data), headers=headers)
        print('评价完成')


if __name__ == '__main__':
    user, pwd = input().split(',')
    # user, pwd = 'username', 'password'
    u = UIMS(user, pwd)
    u.auto_evaluate()

