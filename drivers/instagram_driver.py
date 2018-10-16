from selenium import webdriver as wd
from time import sleep


class InstagramDriver:

    chrome_dir = r"/usr/bin/google-chrome"
    chrome_driver_dir = r"/home/leon/Projects/instascrape/chromedriver"

    def __init__(self, username: str, password: str):

        self.options = wd.ChromeOptions()
        self.options.binary_location = self.chrome_dir
        self.driver = wd.Chrome(self.chrome_driver_dir, chrome_options=self.options)

        self.username = username
        self.password = password

        self.login()

    def login(self):

        # Load page
        self.driver.get("https://www.instagram.com/accounts/login/")

        sleep(2)

        # Login
        self.driver.find_element_by_xpath("//div/input[@name='username']").send_keys(self.username)
        self.driver.find_element_by_xpath("//div/input[@name='password']").send_keys(self.password)
        login_btn = self.driver.find_element_by_xpath("//button[contains(text(),'Log in')]").click()
        # Wait for the login page to load
        # WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.LINK_TEXT, "Watch All")))

        print("Successfuly logged-in!")
        sleep(2)
