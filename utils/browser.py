from selenium import webdriver
from selenium_stealth import stealth
import time

def init_webdriver():
    driver = webdriver.Chrome()
    stealth(driver,
            vendor = "Google Inc.",
            platform="Linux x86_64")
    return driver


def scroll_down(driver, deep, pixels=500, pause=0.1):
    for _ in range(deep):
        driver.execute_script(f"window.scrollBy(0, {pixels});")
        time.sleep(pause)
