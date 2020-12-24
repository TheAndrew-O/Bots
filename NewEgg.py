import bs4
import sys
import time
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager

# Twilio configuration (Using Twilio is optional. Use this if you want to receive text messages when bot makes a purchase.)
toNumber = '+1number'
fromNumber = '+1number'
accountSid = 'ID'
authToken = 'TOKEN'
client = Client(accountSid, authToken)

# Product Page 
url = 'https://www.newegg.com/p/pl?d=rtx+3070&N=100007709&isdeptsrh=1'

def timeSleep(x, driver):
    for i in range(x, -1, -1):
        sys.stdout.write('\r')
        sys.stdout.write('{:2d} seconds'.format(i))
        sys.stdout.flush()
        time.sleep(1)
    driver.refresh()
    sys.stdout.write('\r')
    sys.stdout.write('Page refreshed\n')
    sys.stdout.flush()


def createDriver():
    """Creating driver."""
    options = Options()
    # Change To False if you want to see Firefox Browser Again.
    options.headless = True
    # Enter Firefox Profile Here in quotes.
    profile = webdriver.FirefoxProfile(
        r'C:\Users\USER\AppData\Roaming\Mozilla\Firefox\Profiles\CODE.default-release')
    driver = webdriver.Firefox(profile, options=options, executable_path=GeckoDriverManager().install())
    return driver

def buyCard(driver):
    driver.get(url)
    while True:
        try:
            #driver.get(url)
            wait = WebDriverWait(driver, 15)
            add_Cart = driver.find_element_by_xpath("//*[@class='btn btn-primary btn-mini']")
            add_Cart.click()
            #add_Cart = driver.find_element_by_xpath('//*[@id="ProductBuy"]/div/div[2]/button')
            #add_Cart.click()
            print("Item found, adding to cart")
            driver.get('https://secure.newegg.com/shop/cart')
            # check if in cart
            try:
                wait.until(
                    EC.presence_of_element_located((By.XPATH, "//*[@class='btn btn-primary btn-wide']")))
                driver.find_element_by_xpath("//*[@class='btn btn-primary btn-wide']").click()
                print("Item Is Still In Cart.")
                try:
                    client.messages.create(to=toNumber, from_=fromNumber, body='IN CART')
                except (NameError, TwilioRestException):
                    pass
            except (NoSuchElementException, TimeoutException):
                print("Item is not in cart anymore. Retrying..")
                timeSleep(3, driver)
                buyCard(driver)
                return
            try:
                wait.until(
                    EC.presence_of_element_located((By.XPATH, "//*[@id='signInSubmit']")))
                driver.find_element_by_xpath("//*[@id='signInSubmit']").click()
                print("signing in")
                # enter credit
                security_code = driver.find_element_by_xpath(
                    '//*[@id="app"]/div/section/div/div/form/div[2]/div[1]/div/div[3]/div/div[2]/div[1]/div[2]/div[3]/input')
                time.sleep(1)
                security_code.send_keys('123')
                driver.find_element_by_xpath('//*[@id="btnCreditCard"]').click()
                print('Order Placed!')
                try:
                    client.messages.create(to=toNumber, from_=fromNumber, body='ORDER PLACED!')
                except (NameError, TwilioRestException):
                    pass
            except (NoSuchElementException, TimeoutException):
                print("Already signed in")
                try:
                    security_code = driver.find_element_by_xpath('//*[@id="app"]/div/section/div/div/form/div[2]/div[1]/div/div[3]/div/div[2]/div[1]/div[2]/div[3]/input')
                    print("Entering key")
                    time.sleep(1)
                    security_code.send_keys('123')
                    print("entered")
                    driver.find_element_by_xpath('//*[@id="btnCreditCard"]').click()
                    print('Order Placed!')
                    driver.quit()
                except NoSuchElementException:
                    print("dude")
                    driver.quit()
                    return
                try:
                    client.messages.create(to=toNumber, from_=fromNumber, body='ORDER PLACED!')
                    return
                except (NameError, TwilioRestException):
                    return

        except NoSuchElementException:
            # print('nope')
            pass
        timeSleep(5, driver)

if __name__ == '__main__':
    driver = createDriver()
    buyCard(driver)
