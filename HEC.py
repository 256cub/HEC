from Main import *

if len(sys.argv) > 1:
    if sys.argv[1] == 'install':
        Install()
        exit()
    elif sys.argv[1] == 'useragent':
        app = Main(0)
        app.get_new_useragent()
        exit()

logging.basicConfig(filename="/var/log/" + APP_NAME + "/info.log", level=logging.INFO, format='%(asctime)s %(name)s | %(levelname)s => %(message)s')

# CYCLE
for cycle in range(1, 5):
    app = Main(cycle)

    sql_result = MySQL().select("SELECT id, name, birth_date FROM phones WHERE email IS NULL AND vm2 IS NOT NULL ORDER BY rand() LIMIT 1;")

    usernamesObj = Username()
    usernames = usernamesObj.generate(sql_result)

    app.WebDriver()

    app.ipApi(20)
    # app.ipQualityScore(10, 70)

    app.changeTimeZone()
    # app.change_hostname()

    if app.status:
        try:
            url = 'https://signup.live.com/signup'

            app.chrome.get(url)
            time.sleep(randint(1, 3))
            memberName = app.chrome.find_element_by_id("MemberName")

        except NameError:
            app.finish('error', 'Error Loading Hotmail SignUp Page', True)

    if app.status:

        try:
            time.sleep(randint(5, 10))
            memberName.send_keys(usernames[0])
            time.sleep(randint(5, 10))
            Select(app.chrome.find_element_by_id('LiveDomainBoxList')).select_by_value('hotmail.com')
            time.sleep(randint(1, 3))
            app.chrome.find_element_by_id('iSignupAction').click()
            time.sleep(randint(5, 10))

            WebDriverWait(app.chrome, 20).until(EC.visibility_of_element_located((By.ID, "iSignupAction")))

            for u in range(len(usernames)):

                if app.chrome.find_elements_by_xpath("//*[contains(text(), 'Someone already has this email')]"):
                    if u != 0:
                        memberName.clear()
                        memberName.send_keys(usernames[u])

                        if 'hotmail.com' in usernames[u]:
                            Select(app.chrome.find_element_by_id('LiveDomainBoxList')).select_by_value('hotmail.com')
                        elif 'outlook.com' in usernames[u]:
                            Select(app.chrome.find_element_by_id('LiveDomainBoxList')).select_by_value('outlook.com')

                        app.chrome.find_element_by_id('iSignupAction').click()
                        time.sleep(randint(3, 5))

            try:
                if app.chrome.find_elements_by_xpath("//*[contains(text(), 'Someone already has this email')]"):
                    sql_result = MySQL().update("UPDATE phones SET email = 'None-{}' WHERE id = '{}'".format(usernamesObj.id, usernamesObj.id))
                    app.finish('error', "No Username Available", True)

            except:
                no_username_available = True

        except:
            app.finish('warning', "Error Completing Input Usernames {}".format(usernames), True)

        app.write_log('Completing Username: {} | Password: {}'.format(usernames[u], app.psw))

        if app.status:
            try:
                app.chrome.find_element_by_id("PasswordInput").send_keys(app.psw)
                time.sleep(randint(1, 3))
                app.chrome.find_element_by_id('iSignupAction').click()
                time.sleep(randint(5, 10))

                element = WebDriverWait(app.chrome, 20).until(EC.presence_of_element_located((By.ID, "iSignupAction")))
            except:
                app.finish('error', "Error Completing Input PasswordInput", True)

        if app.status:
            try:
                app.chrome.find_element_by_id("FirstName").send_keys(usernamesObj.first_name)
                time.sleep(randint(1, 3))
                app.chrome.find_element_by_id("LastName").send_keys(usernamesObj.last_name)
                time.sleep(randint(1, 3))
                app.chrome.find_element_by_id('iSignupAction').click()
                time.sleep(randint(1, 3))
                element = WebDriverWait(app.chrome, 20).until(EC.presence_of_element_located((By.ID, "iSignupAction")))
            except:
                app.finish('error', "Error Completing Input FirstName + LastName", True)

        if app.status:
            try:
                Select(app.chrome.find_element_by_id('Country')).select_by_value('US')
                Select(app.chrome.find_element_by_id('BirthMonth')).select_by_value('{}'.format(usernamesObj.birth_date.month))
                Select(app.chrome.find_element_by_id('BirthDay')).select_by_value('{}'.format(usernamesObj.birth_date.day))
                # Select(app.chrome.find_element_by_id('BirthYear')).select_by_value('{}'.format(usernamesObj.birth_date.year))

                # app.chrome.find_element_by_id('iSignupAction').click()
                time.sleep(60)
                # WebDriverWait(app.chrome, 20).until(EC.presence_of_element_located((By.ID, "hipTemplateContainer")))
            except:
                app.finish('error', "Error Completing Input Country + Birth", True)

        if app.status:
            try:
                if app.chrome.find_element_by_xpath("//select[@aria-label='Country code']"):
                    app.finish('error', "Need Phone Verification", True)

            except:
                no_phone = True

        if app.status:
            app.solve_captcha()

    if app.status:

        time.sleep(60)

        try:
            app.chrome.find_element_by_xpath("//input[@id='idSIButton9']").click()
            app.write_log('Click on idSIButton9')
            time.sleep(10)
        except:
            nothing_to_click = True

        try:

            app.write_log('Wait up to 180 seconds for Completing Captcha')
            WebDriverWait(app.chrome, 180).until(EC.visibility_of_element_located((By.XPATH, "//a[@data-bi-id='home.banner.profile-column.subtitle.cta']")))

            # if False:
                # TODO FunCaptcha AutoSolver
                # app.chrome.get('https://iframe-auth.arkoselabs.com/B7D8911C-5CC8-A9A3-35B0-554ACEE604DA/index.html?mkt=en')
                #  https://iframe-auth.arkoselabs.com/B7D8911C-5CC8-A9A3-35B0-554ACEE604DA/index.html?mkt=en
                # images = app.chrome.find_elements_by_tag_name('img')
                # img = app.chrome.find_element_by_xpath('///img')

            email = app.chrome.find_element_by_xpath("//a[@data-bi-id='home.banner.profile-column.subtitle.cta']").text.lower()
            email_array = email.splitlines()
            email = email_array[1]

            sql_result = MySQL().update("UPDATE phones SET email = '{}', psw = '{}' WHERE id = '{}'".format(email, app.psw, usernamesObj.id))
            app.write_log('info', 'Email {} Updated to MySQL | {}'.format(email, sql_result))
        except:
            # app.finish('critical', "Email Done Page not Load Fully")
            print('CRITICAL')
            app.write_log('Completing Username: {} | Password: {}'.format(usernames[u], app.psw), 'critical')
            time.sleep(600)

        try:
            app.chrome.get('https://outlook.live.com/')

            # app.chrome.find_element_by_tag_name('body').send_keys(Keys.CONTROL + 't')
            # app.chrome.find_element_by_tag_name('body').send_keys(Keys.CONTROL + Keys.TAB)
            # windows = app.chrome.window_handles
            # app.chrome.switch_to.window(windows[1])

            try:
                WebDriverWait(app.chrome, 20).until(EC.visibility_of_element_located((By.CLASS_NAME, "refreshPageButton")))
                app.chrome.find_element_by_class_name('refreshPageButton').click()
            except:
                nothing_to_click = True

            try:
                WebDriverWait(app.chrome, 20).until(EC.visibility_of_element_located((By.XPATH, "//i[@class='root-62']")))
            except:
                nothing_to_click = True

            app.send_test_email(email)

            time.sleep(randint(20, 30))

            url = 'https://outlook.live.com/mail/options/mail/accounts'
            app.chrome.get(url)

            try:
                WebDriverWait(app.chrome, 20).until(EC.visibility_of_element_located((By.XPATH, '//label[@for="ChoiceGroup145-enable"]')))
            except:
                nothing_to_click = True

            try:
                app.chrome.find_element_by_class_name('ms-ChoiceField-wrapper').click()
                # app.chrome.find_element_by_xpath('//label[@for="ChoiceGroup145-enable"]').click()
                time.sleep(randint(3, 5))
                app.chrome.find_element_by_xpath("//span[contains(text(), 'Save')]").click()
                time.sleep(10)

                app.finish('info', 'OK', True)
            except:
                app.finish('warning', "Can\'t Activate POP", True)

        except:
            app.finish('warning', "Error Last Page", True)
