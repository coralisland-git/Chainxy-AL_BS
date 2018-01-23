import platform
try:
    from pyvirtualdisplay import Display
except:
    pass
from selenium import webdriver

class WebDriverFactory(object):
    display = None
    driver = None

    def get(self, size=(800, 600)):
        if 'Linux' in platform.system():
            self.display = Display(visible=0, size = size)
            self.display.start()
            self.driver = webdriver.Chrome("/usr/lib/chromium-browser/chromedriver")
            return self.driver
        elif 'Windows' in platform.system():
            self.driver = webdriver.Chrome("./chromedriver.exe")
            return self.driver

    def close(self):
        if self.driver is not None:
            self.driver.quit()
        if self.display is not None:
            self.display.stop()
