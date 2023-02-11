import json
import logging
import os
import platform
import random
import smtplib
import socket
import ssl
import string
import subprocess
import time
import mysql.connector
import sys

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from random import randint
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from pathlib import Path
from pytz import timezone
from datetime import datetime

APP_PATH = os.getcwd()
APP_NAME = APP_PATH.split('/')[2]


def random_line(input_data):
    lines = open(input_data).read().splitlines()
    return random.choice(lines)


def random_password(length=10):
    letters_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_digits) for n in range(length))


class Main:

    def __init__(self, cycle):
        self.chrome = None
        self.inx = randint(1000000000, 9999999999)
        self.psw = random_password(10)
        self.cycle = cycle
        self.start = time.time()
        self.status = True
        self.ip = False
        self.timezone = False
        self.id = None
        self.first_name = None
        self.last_name = None
        self.birth_date = None
        self.fraud_score = 101

    def write_log(self, message, log_type='info'):

        print("  ['{}'] Session: {} | Cycle: {} | {}".format(log_type, self.inx, self.cycle, message))

        if log_type == 'info':
            logging.info("     Session: {} | Cycle: {} | {}".format(self.inx, self.cycle, message))

        elif log_type == 'error':
            logging.error("    Session: {} | Cycle: {} | {}".format(self.inx, self.cycle, message))

        elif log_type == 'warning':
            logging.warning("  Session: {} | Cycle: {} | {}".format(self.inx, self.cycle, message))

        elif log_type == 'critical':
            logging.critical(" Session: {} | Cycle: {} | {}".format(self.inx, self.cycle, message))

    def WebDriver(self):
        try:
            options = webdriver.ChromeOptions()
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument("--proxy-server=%s" % self.get_random_proxy())
            options.add_argument("--user-agent=%s" % self.get_random_useragent())
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            # options.add_argument("--start-maximized")
            chrome_driver_binary = r"{}/Input/driver/chromedriver".format(APP_PATH)
            self.chrome = webdriver.Chrome(chrome_driver_binary, options=options)
        except:
            self.finish('error', "Error Loading WebDriver", True)

    def Navigate(self, url):
        try:
            self.chrome.get(url)
            self.write_log("URL: {} | Page Title: {}".format(url, self.chrome.title))
        except:
            self.finish('error', "Error Navigate WebDriver", True)

    def get_random_proxy(self):
        f = open('{}/Input/ReverseProxy.txt'.format(APP_PATH), 'r')
        proxies = f.readlines()
        random.shuffle(proxies)
        proxy = proxies[0].replace('\n', '')
        self.write_log('Proxy: {}'.format(proxy))
        return proxy

    def get_random_useragent(self):

        with open('{}/Input/UserAgent.txt'.format(APP_PATH)) as file:
            useragents = file.readlines()

        if len(useragents) < 100:
            self.get_new_useragent()
            with open('{}/Input/UserAgent.txt'.format(APP_PATH)) as file:
                useragents = file.readlines()

        random.shuffle(useragents)
        useragent = useragents[0].replace('\n', '')
        self.write_log('UserAgent: {}'.format(useragent))
        return useragent

    def get_new_useragent(self):
        try:
            sql_result = MySQL().select("SELECT ua FROM useragents WHERE status = '1'")

            if len(sql_result) > 100:

                with open("{}/Input/UserAgent.txt".format(APP_PATH), "w", newline='') as file_line:
                    for row in sql_result:
                        print(row[0], file=file_line)

                self.write_log("{} UserAgents saved to txt file".format(len(sql_result)))

            else:
                self.write_log("Not found UserAgent in MySQL")

        except mysql.connector.Error as error:
            self.write_log("Failed to select from useragents table {}".format(error))

    def change_hostname(self):
        try:
            old_hostname = socket.gethostname()
            new_hostname = random_line('{}/Input/HostName.txt'.format(APP_PATH))
            os.system("echo {} | sudo -S hostname -b {}".format('TODO', new_hostname))
            changed_hostname = socket.gethostname()

            self.write_log("Hostname {} => {}".format(old_hostname, changed_hostname))
        except SystemError:
            self.write_log("Hostname Change Error")

    def make_screenshot(self):
        try:
            self.chrome.save_screenshot("{}/Screenshot/{}_{}.png".format(APP_PATH, self.inx, self.cycle))
            self.write_log("Screenshot Saved to {}/Screenshot/{}_{}.png".format(APP_PATH, self.inx, self.cycle))
        except:
            self.write_log("Can\'t Save Screenshot", 'critical')

    def finish(self, result, log='', make_screenshot=False):
        self.write_log("{} | Total Time: {} seconds".format(log, format(time.time() - self.start, '.2f')), result)

        if make_screenshot:
            self.make_screenshot()

        self.chrome.quit()
        self.status = False

    def ipApi(self, wait):
        try:
            self.Navigate('https://ipapi.co/json/')

            WebDriverWait(self.chrome, wait).until(EC.presence_of_element_located((By.TAG_NAME, "pre")))

            pre = self.chrome.find_element_by_tag_name("pre").text
            data = json.loads(pre)

            self.ip = data['ip']
            self.timezone = data['timezone']
            self.write_log("IP: {} | Country: {} | Region: {} | Timezone: {}".format(data['ip'], data['country'], data['region'], data['timezone']))

            if data['country'] != "US":
                self.finish('warning', "Not US | Country: {}".format(data['country']), True)

            return data
        except:
            self.finish('warning', "Error ipApi.com", True)

    def ipQualityScore(self, wait, score):
        # found = self.check_blacklist(self.ip)
        # if len(found) > 0:
        #     self.finish('warning', "Blacklist IP {} Found in MySQL on {}".format(self.ip, found[0]['timestamp']), False)

        # Check ipQualityScore Credits
        # https://www.ipqualityscore.com/api/json/account/TODO

        keys = [
            'TODO',
        ]

        key = random.choice(keys)
        url = "https://www.ipqualityscore.com/api/json/ip/{}/{}".format(key, self.ip)

        if self.status:
            try:
                self.Navigate(url)
                WebDriverWait(self.chrome, wait).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                body = self.chrome.find_element_by_tag_name("body").text
            except:
                self.finish('warning', "Error Content no Loaded: {}".format(url), True)

        if self.status:
            try:
                result = json.loads(body)
                fraud_score = result['fraud_score']
                self.fraud_score = result['fraud_score']

                if fraud_score > score:
                    self.save_blacklist_ip(self.ip, fraud_score)
                    self.finish('warning', 'Fraud Score: {}'.format(fraud_score), True)
                else:
                    self.write_log('Fraud Score: {}'.format(fraud_score))

            except:
                self.finish('warning', "Error JSON Format: {}".format(url), True)

    def save_blacklist_ip(self, blacklist_ip, score):
        try:
            date = time.strftime('%Y-%m-%d %H:%M:%S')
            sql = "INSERT INTO blacklist (ip, score, `timestamp`) VALUES('{}', '{}', '{}') ON DUPLICATE KEY UPDATE score = '{}', `timestamp` = '{}';".format(blacklist_ip, score, date, score, date)
            sql_result = MySQL().update(sql)
            self.finish('warning', "{} Blacklist IP inserted in MySQL".format(sql_result), False)
        except mysql.connector.Error as error:
            self.finish('critical', "Failed to insert record into blacklist table {}".format(error), False)

    def check_blacklist(self, blacklist_ip):
        try:
            sql = "SELECT * FROM blacklist WHERE ip = '{}';".format(blacklist_ip)
            sql_result = MySQL().select(sql)
            return sql_result
        except mysql.connector.Error as error:
            self.finish('critical', "Failed to SELECT record from blacklist table {}".format(error), False)

    def changeTimeZone(self):
        if self.status:
            if self.timezone:
                try:
                    subprocess.call('echo {} | sudo -S timedatectl set-timezone {}'.format('wwwpop13', self.timezone), shell=True)
                    self.write_log("Change TimeZone to {}".format(self.timezone))
                except SystemError:
                    self.write_log("Error Changing TimeZone {}".format(self.timezone), 'error')

    def send_test_email(self, receiver_email):
        sender_email = 'TODO'
        password = 'TODO'

        message = MIMEMultipart("alternative")
        message["Subject"] = "Daily Newsletter for {} {} from {}".format(receiver_email, receiver_email, time.strftime("%Y-%m-%d %H:%M", time.localtime(time.time())))
        message["From"] = sender_email
        message["To"] = receiver_email

        # Create the plain-text and HTML version of your message
        text = "This is a Daily Newsletter {}".format(time.time())
        html = """\
        <html>
          <body>
            <p>Hi,<br>
               TODO
            </p>
          </body>
        </html>
        """

        # Turn these into plain/html MIMEText objects
        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")

        # Add HTML/plain-text parts to MIMEMultipart message
        # The email client will try to render the last part first
        message.attach(part1)
        message.attach(part2)

        # Create secure connection with server and send email
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(
                sender_email, receiver_email, message.as_string()
            )

        self.write_log("Test Email Sent {}".format(receiver_email))

    def solve_captcha(self):
        to_do_captcha = True
        # print('TODO CAptcha')
        # try:
        #     client = deathbycaptcha.SocketClient('TODO', 'TODO')
        #     balance = client.get_balance() / 100
        #     print("  [+] DeathByCaptcha Balance: {}".format(balance))
        #     status = True
        #
        # except:
        #     print("  [X] DeathByCaptcha Error")
        #     logging.warning(' DeathByCaptcha Error')
        #     status = False
        #
        # if status:
        #     for c in range(1, 5):
        #         try:
        #             captcha_file_name = "{}/Captcha/{}_{}.png".format(APP_DIR, inx, c)
        #             img = chrome.find_element_by_xpath("//img[@aria-label='Visual Challenge']")
        #             src = img.get_attribute('src')
        #
        #             urllib.request.urlretrieve(src, captcha_file_name)
        #
        #             client = deathbycaptcha.SocketClient('TODO', 'TODO')
        #             balance = client.get_balance() / 100
        #
        #             print("  [+] DeathByCaptcha Balance: {}".format(balance))
        #             captcha = client.decode(captcha_file_name, 30)
        #             logging.info(
        #                 ' Session: {} | Cycle: {} | Captcha Cycle: {} | Captcha ID: {} | Captcha Text: {} | Captcha '
        #                 'Balance: {} '.format(inx, i, c, captcha["captcha"], captcha["text"], balance))
        #
        #             if captcha:
        #                 print("  [+] CAPTCHA %s solved: %s" % (captcha["captcha"], captcha["text"]))
        #                 chrome.find_element_by_xpath("//input[@aria-label='Enter the characters you see']").send_keys(captcha["text"].replace(" ", ""))
        #                 time.sleep(randint(1, 3))
        #                 chrome.find_element_by_id("iSignupAction").click()
        #                 time.sleep(randint(8, 10))
        #
        #                 if chrome.find_elements_by_xpath("//*[contains(text(), 'match the picture. Please try again')]"):
        #                     client.report(captcha["captcha"])
        #                     print("  [X] deathbycaptcha Report Bad Captcha")
        #                     logging.info(' Session: {} | Cycle: {} | Captcha Cycle: {} | Bad Captcha | Captcha ID: ''{} | Captcha Text: {} | Captcha Balance: {} '.format(inx, i, c, captcha["captcha"], captcha["text"], balance))
        #
        #         except:
        #             make_screenshot(inx, i, 'info')
        #             print("  [X] Not Found Captcha Image")
        #             logging.warning(' Session: {} | Cycle: {} | Captcha Cycle: {} | Not Found Captcha Image'.format(inx, i, c))

    def random_on_page(self):
        try:
            time.sleep(randint(3, 10))
            elm = self.chrome.find_element_by_tag_name('html')
            elm.send_keys(Keys.END)
            time.sleep(randint(3, 10))
            elm.send_keys(Keys.HOME)
            time.sleep(randint(3, 10))
            self.chrome.execute_script("window.scrollTo(0,{})".format(randint(500, 2000)))
            time.sleep(randint(3, 10))
        except:
            self.write_log("Error Random on Page", 'warning')

    def scroll_ads(self):
        try:
            google_ads = self.chrome.find_elements_by_class_name("adsbygoogle")
            random.shuffle(google_ads)

            to_scroll = 0
            if len(google_ads) == 0:
                self.write_log("None Scroll Google Ads", 'warning')
            elif len(google_ads) > 2:
                to_scroll = randint(1, 2)
                self.write_log("On Page there is {} Scroll Google Ads | Scrolling only {}".format(len(google_ads), to_scroll))
            else:
                to_scroll = len(google_ads)
                self.write_log("On Page there is {} Scroll Google Ads | Scrolling All {}".format(len(google_ads), to_scroll))

            for i in range(to_scroll):
                self.chrome.execute_script('arguments[0].scrollIntoView();', google_ads[i])
                time.sleep(randint(3, 10))

        except:
            self.write_log("Error Scroll Google Ads", 'warning')

    def google_ads_click(self):
        try:
            google_ads = self.chrome.find_elements_by_class_name("adsbygoogle")
            random.shuffle(google_ads)

            google_ads[0].click()

            time.sleep(randint(5, 20))
            self.random_on_page()
            time.sleep(randint(5, 20))

            self.write_log("Click Google Ads {} ".format(google_ads[0].get_attribute('outerHTTML')))
        except:
            self.write_log("Click Google Ads", 'warning')

    def adclerks_ads_click(self):
        try:
            adclerks_ads = self.chrome.find_elements_by_xpath("//a[contains(@href, 'adclerks.com/core/adclick/')]")
            random.shuffle(adclerks_ads)
            adclerks_ads[0].click()

            time.sleep(randint(5, 20))
            self.random_on_page()
            time.sleep(randint(5, 20))

            self.write_log("AdClerks Ads {} {}".format(adclerks_ads[0].get_attribute('href'), adclerks_ads[0].get_attribute('title')))
        except:
            self.write_log("AdClerks Ads", 'warning')

class MySQL:
    def __init__(self):
        self.connection = mysql.connector.connect(
            host="TODO",
            user="TODO",
            passwd="TODO",
            database="TODO",
            auth_plugin="mysql_native_password"
        )

    def select(self, query):
        sql_cursor = self.connection.cursor(dictionary=True)
        sql_cursor.execute(query)
        sql_result = sql_cursor.fetchall()
        self.connection.close()
        return sql_result

    def update(self, query):
        sql_cursor = self.connection.cursor()
        sql_cursor.execute(query)
        self.connection.commit()
        sql_cursor.close()
        return sql_cursor

    def close(self):
        self.connection.close()


class Username:
    def __init__(self):
        self.usernames = []
        self.id = None
        self.first_name = None
        self.last_name = None
        self.birth_date = None

    def generate(self, sql_result):
        for row in sql_result:

            name = row["name"].strip()
            fullname = name.split(" ")

            self.id = row["id"]
            self.birth_date = row["birth_date"]

            self.first_name = fullname[0].strip()
            self.last_name = fullname[1].strip()

            self.usernames = [
                "{}@hotmail.com".format(name.replace(" ", "")),
                "{}@outlook.com".format(name.replace(" ", ""))
            ]

            if name.count(" ") == 1:
                the_vowel = ('a', 'e', 'i', 'o', 'u')

                if fullname[0].lower() not in the_vowel:
                    self.usernames.append("{}{}@hotmail.com".format(self.first_name[0], self.last_name))
                    self.usernames.append("{}{}@outlook.com".format(self.first_name[0], self.last_name))

                self.usernames.append("{}{}@hotmail.com".format(self.last_name, self.first_name))
                self.usernames.append("{}{}@outlook.com".format(self.last_name, self.first_name))

                self.usernames.append("{}.{}@hotmail.com".format(self.first_name, self.last_name))
                self.usernames.append("{}.{}@outlook.com".format(self.first_name, self.last_name))

                if fullname[0].lower() not in the_vowel:
                    self.usernames.append("{}.{}@hotmail.com".format(self.first_name[0], self.last_name))
                    self.usernames.append("{}.{}@outlook.com".format(self.first_name[0], self.last_name))

        return self.usernames


class Install:
    def __init__(self):
        self.HEADER = '\033[95m'
        self.OKBLUE = '\033[94m'
        self.OKGREEN = '\033[92m'
        self.WARNING = '\033[93m'
        self.FAIL = '\033[91m'
        self.ENDC = '\033[0m'
        self.BOLD = '\033[1m'
        self.UNDERLINE = '\033[4m'

        input_psw = input("Enter password: ")

        print(self.HEADER + " \n*** UPDATING UBUNTU APP ***\n " + self.ENDC)
        os.popen("sudo -S %s" % ('apt update -y'), 'w').write(input_psw)
        time.sleep(3)

        print(self.OKBLUE + " \n*** UPGRATING UBUNTU APP ***\n " + self.ENDC)
        os.popen("sudo -S %s" % ('apt upgrade -y'), 'w').write(input_psw)
        time.sleep(3)

        print(self.OKGREEN + " \n*** AUTOREMOVING UBUNTU APP ***\n " + self.ENDC)
        os.popen("sudo -S %s" % ('apt autoremove -y'), 'w').write(input_psw)
        time.sleep(3)

        print(self.HEADER + " \n*** INSTALLING GOOGLE CHROME ***\n " + self.ENDC)
        os.popen("sudo -S %s" % ('wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb'), 'w').write(input_psw)
        os.popen("sudo -S %s" % ('apt install ./google-chrome-stable_current_amd64.deb -y'), 'w').write(input_psw)
        time.sleep(3)

        print(self.UNDERLINE + " \n*** INSTALLING python3.8 ***\n " + self.ENDC)
        os.popen("sudo -S %s" % ('apt install python3.8 -y'), 'w').write(input_psw)
        os.popen("sudo -S %s" % ('update-alternatives --install /usr/bin/python python /usr/bin/python3.8 1'), 'w').write(input_psw)
        os.popen("sudo -S %s" % ('update-alternatives --set python /usr/bin/python3.8'), 'w').write(input_psw)
        time.sleep(3)

        print(self.BOLD + " \n*** INSTALLING pip ***\n " + self.ENDC)
        os.popen("sudo -S %s" % ('apt install python3-pip -y'), 'w').write(input_psw)
        os.popen("sudo -S %s" % ('apt install python-pip -y'), 'w').write(input_psw)
        time.sleep(3)

        print(self.FAIL + " \n*** INSTALLING PYTHON MODULES ***\n " + self.ENDC)
        os.popen("sudo -S %s" % ('pip3 install selenium'), 'w').write(input_psw)
        os.popen("sudo -S %s" % ('pip3 install mysql-connector-python'), 'w').write(input_psw)
        os.popen("sudo -S %s" % ('pip3 install mysql-connector'), 'w').write(input_psw)
        time.sleep(3)

        print(self.FAIL + " \n*** INSTALLING GUI  ***\n " + self.ENDC)
        os.popen("sudo -S %s" % ('apt install python python3-tk'), 'w').write(input_psw)
        os.popen("sudo -S %s" % ('pip3 install PySimpleGUI'), 'w').write(input_psw)
        time.sleep(3)

        print(self.OKBLUE + " \n*** CREATING LOG FOLDER ***\n " + self.ENDC)
        os.popen("sudo -S %s" % ('mkdir -m 777 /var/log/' + APP_NAME), 'w').write(input_psw)
        time.sleep(3)

        print(self.OKBLUE + " \n*** CREATING OTHER FOLDER ***\n " + self.ENDC)
        os.popen("sudo -S %s" % ('mkdir -m 777 ' + APP_PATH + '/Captcha'), 'w').write(input_psw)
        os.popen("sudo -S %s" % ('mkdir -m 777 ' + APP_PATH + '/Screenshot'), 'w').write(input_psw)
        time.sleep(3)

        print(self.UNDERLINE + " \n*** SETTING FULL PERMISSIONS ***\n " + self.ENDC)
        os.popen("sudo -S %s" % ('chmod -R 777 ' + APP_PATH), 'w').write(input_psw)
        time.sleep(3)
