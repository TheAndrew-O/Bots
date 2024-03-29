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

# Twilio configuration (Optional but highly suggested)
toNumber = '+1number'
fromNumber = '+1number'
accountSid = 'ID'
authToken = 'TOKEN'
client = Client(accountSid, authToken)

#Make Sure that credit card information is already added to Newegg/account.

# Product Page
# Newegg URL
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
    # Change Profile Here in quotes.
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
            # Uncomment following line to use on Best Buy websites
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
                    # Send Message to phone that item is ready for purchase
                    client.messages.create(to=toNumber, from_=fromNumber, body='IN CART')
                except (NameError, TwilioRestException):
                    pass
            except (NoSuchElementException, TimeoutException):
                print("Item is not in cart anymore. Retrying..")
                timeSleep(3, driver)
                buyCard(driver)
                return
            try:
                # If added item to cart and still in cart, then proceed with transaction
                wait.until(
                    EC.presence_of_element_located((By.XPATH, "//*[@id='signInSubmit']")))
                driver.find_element_by_xpath("//*[@id='signInSubmit']").click()
                print("signing in")
                # enter credit
                security_code = driver.find_element_by_xpath(
                    '//*[@id="app"]/div/section/div/div/form/div[2]/div[1]/div/div[3]/div/div[2]/div[1]/div[2]/div[3]/input')
                time.sleep(1)
                # Change CVV number
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
                    # If order not placed because website needs to sign in again
                    security_code = driver.find_element_by_xpath('//*[@id="app"]/div/section/div/div/form/div[2]/div[1]/div/div[3]/div/div[2]/div[1]/div[2]/div[3]/input')
                    print("Entering key")
                    time.sleep(1)
                    # Change CVV
                    security_code.send_keys('123')
                    print("entered")
                    driver.find_element_by_xpath('//*[@id="btnCreditCard"]').click()
                    print('Order Placed!')
                    driver.quit()
                except NoSuchElementException:
                    print("Failed to sign in again.")
                    driver.quit()
                    return
                try:
                    client.messages.create(to=toNumber, from_=fromNumber, body='ORDER PLACED!')
                    return
                except (NameError, TwilioRestException):
                    return

        except NoSuchElementException:
            pass
        timeSleep(5, driver)

if __name__ == '__main__':
    driver = createDriver()
    buyCard(driver)
