import time
from selenium import webdriver as wd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# The account you want to check
account = ""

# Chrome executable
chrome_binary = r"chrome.exe"   # Add your path here


def load_account(driver, account):

    account_url = f"https://www.instagram.com/{account}/"
    print(account_url)
    driver.get(account_url)


def login(driver):
    username = ""   # Your username
    password = ""   # Your password

    # Load page
    driver.get("https://www.instagram.com/accounts/login/")

    # Login
    driver.find_element_by_xpath("//div/input[@name='username']").send_keys(username)
    driver.find_element_by_xpath("//div/input[@name='password']").send_keys(password)
    driver.find_element_by_xpath("//span/button").click()

    # Wait for the login page to load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.LINK_TEXT, "Watch All")))

    print("Successfuly logged-in!")


def scrape_followers(driver, account):
    # Load account page
    # account_url = f"https://www.instagram.com/{account}/"
    # driver.get("https://www.instagram.com/{0}/".format(account))
    # print(account_url)
    # driver.get(account_url)


    # Click the 'Follower(s)' link
    driver.find_element_by_partial_link_text("follower").click()

    # Wait for the followers modal to load
    xpath = "/html/body/div[3]/div/div[2]/div"
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, xpath)))

    SCROLL_PAUSE = 1  # Pause to allow loading of content

    driver.execute_script("followersbox = document.getElementsByClassName('j6cq2')[0];")
    last_height = driver.execute_script("return followersbox.scrollHeight;")

    # We need to scroll the followers modal to ensure that all followers are loaded
    while True:

        driver.execute_script("followersbox.scrollTo(0, followersbox.scrollHeight);")

        # Wait for page to load
        time.sleep(SCROLL_PAUSE)

        # Calculate new scrollHeight and compare with the previous
        new_height = driver.execute_script("return followersbox.scrollHeight;")

        print(f"Last height: {last_height}")
        print(f"New height: {new_height}")

        if new_height == last_height:
            break

        last_height = new_height

    # Finally, scrape the followers "/html/body/div[3]/div/div[2]/div/div[2]/ul/div/li"
    # xpath = "/html/body/div[4]/div/div/div[2]/div/div[2]/ul/li"
    xpath = "/html/body/div[3]/div/div[2]/div/div[2]/ul/div/li"
    followers_elems = driver.find_elements_by_xpath(xpath)

    followers_temp = [e.text for e in followers_elems]  # List of followers (username, full name, follow text)
    followers = []  # List of followers (usernames only)

    # Go through each entry in the list, append the username to the followers list
    for i in followers_temp:
        username, sep, name = i.partition('\n')
        followers.append(username)

    print("______________________________________")
    print("FOLLOWERS")

    return followers


def scrape_following(driver, account):
    # Load account page
    account_url = f"https://www.instagram.com/{account}/"

    # Click the 'Following' link
    driver.find_element_by_partial_link_text("following").click()
    # Wait for the following modal to load
    xpath = "/html/body/div[3]/div/div[2]/div"
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, xpath)))

    SCROLL_PAUSE = 1  # Pause to allow loading of content
    driver.execute_script("followingbox = document.getElementsByClassName('j6cq2')[0];")
    last_height = driver.execute_script("return followingbox.scrollHeight;")

    # We need to scroll the following modal to ensure that all following are loaded
    while True:
        driver.execute_script("followingbox.scrollTo(0, followingbox.scrollHeight);")

        # Wait for page to load
        time.sleep(SCROLL_PAUSE)

        # Calculate new scrollHeight and compare with the previous
        new_height = driver.execute_script("return followingbox.scrollHeight;")
        if new_height == last_height:
            break
        last_height = new_height

    # Finally, scrape the following
    xpath = "/html/body/div[3]/div/div[2]/div/div[2]/ul/div/li"
    following_elems = driver.find_elements_by_xpath(xpath)

    following_temp = [e.text for e in following_elems]  # List of following (username, full name, follow text)
    following = []  # List of following (usernames only)

    # Go through each entry in the list, append the username to the following list
    for i in following_temp:
        username, sep, name = i.partition('\n')
        following.append(username)

    print("\n______________________________________")
    print("FOLLOWING")
    return following


def scrape_posts_links(driver, account):

    # xpath = "/html/body/span/section/main/div/div[3]/article/div[1]"
    #
    # WebDriverWait(driver, 10).until(
    #     EC.presence_of_element_located((By.XPATH, xpath)))

    SCROLL_PAUSE = 2  # Pause to allow loading of content

    # driver.execute_script("posts = document.getElementsByClassName('SCxLW  o64aR')[0];")
    last_height = driver.execute_script("return document.scrollHeight;")



    print(last_height)


    post_links = []
    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")

    # links = driver.find_elements(By.cssSelector("v1Nh3 kIKUG  _bz0w"))

    while True:

        # links = driver.find_elements_by_css_selector(".v1Nh3.kIKUG._bz0w")

        # links = driver.find_elements_by_partial_link_text("/p/")

        # links = driver.find_elements_by_xpath("")
        # links = driver.find_elements_by_tag_name("a")
        # print(links)
        # links = [e.text for e in links]
        # links = driver.find_elements_by_class_name("v1Nh3 kIKUG  _bz0w")
        # print(links)


        # vrže nazaj vse linke vendar dela, samo filtrirat vn ta prave
        elems = driver.find_elements_by_xpath("//a[@href]")
        for elem in elems:
            print(elem.get_attribute("href"))


        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")


        # xpath = "//article/div[1]/div/div[1]/div[2]/a"

        # links = driver.find_elements_by_xpath(xpath)

        # links = driver.find_elements_by_class_name(name="v1Nh3 kIKUG  _bz0w")

        # links_attr = links.get_attribute("href")

        # print(links_attr)
        # Wait to load page
        time.sleep(SCROLL_PAUSE)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


    # xpath = "/html/body/span/section/main/div/div[3]/article/div[1]/div/div[1]"
    # following_elems = driver.find_elements_by_xpath(xpath)
    # following_temp = [e.text for e in following_elems]
    # print(following_temp)




if __name__ == "__main__":

    account = "taeyooung"
    options = wd.ChromeOptions()
    options.binary_location = r"C:/Program Files (x86)/Google/Chrome/Application/chrome.exe"  # chrome.exe
    driver_binary = r"D:/Data Science/Projects/instascrape/chromedriver.exe"
    # options.add_argument('--disable-extensions')
    # options.add_argument('--headless')
    # options.add_argument('--disable-gpu')
    # options.add_argument('--no-sandbox')
    driver = wd.Chrome(driver_binary, chrome_options=options)

    try:
        login(driver)  # login to you instagram account

        load_account(driver, account)

        scrape_posts_links(driver, account)
        # followers = scrape_followers(driver, account)

        # print(followers)
        # print(len(followers))
        # following = scrape_following(driver, account)
        # print(following)

    finally:
        driver.quit()
