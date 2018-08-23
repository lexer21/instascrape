# -*- coding: utf-8 -*-

import time
from selenium import webdriver as wd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def load_account(driver: wd.Chrome, account: str):

    account_url = f"https://www.instagram.com/{account}/"
    print(account_url)
    driver.get(account_url)


def login(driver: wd.Chrome, username: str, password: str):

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


def scrape_followers(driver: wd.Chrome, account: str) -> list:

    # Click the 'Follower(s)' link
    driver.find_element_by_partial_link_text("follower").click()

    # Wait for the followers modal to load
    xpath = "/html/body/div[3]/div/div[2]/div"
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath)))

    SCROLL_PAUSE = 1  # Pause to allow loading of content

    modalbox = "followersbox"
    scroll_class = "j6cq2"
    scroll_modal(driver, SCROLL_PAUSE, modalbox, scroll_class)

    xpath = "/html/body/div[3]/div/div[2]/div/div[2]/ul/div/li"  # xpath for follower elements
    followers = extract_elements(driver, xpath)  # extract usernames

    # exit the modal
    driver.find_element_by_class_name("ckWGn").click()

    return followers


def scrape_following(driver: wd.Chrome, account: str) -> list:

    driver.find_element_by_partial_link_text("following").click()

    xpath = "/html/body/div[3]/div/div[2]/div"
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath)))

    SCROLL_PAUSE = 1

    modalbox = "followingbox"
    scroll_class = "j6cq2"
    scroll_modal(driver, SCROLL_PAUSE, modalbox, scroll_class)

    xpath = "/html/body/div[3]/div/div[2]/div/div[2]/ul/div/li"
    following = extract_elements(driver, xpath)

    driver.find_element_by_class_name("ckWGn").click()

    return following


def scrape_bio(driver: wd.Chrome) -> tuple:

    elements = driver.find_element_by_class_name("-vDIg")

    name = elements.find_element_by_tag_name("h1").text
    bio = elements.find_element_by_tag_name("span").text

    print(f"Name is {name}")
    print(f"Bio is {bio}")

    return (name, bio)


def scrape_posts_links(driver: wd.Chrome) -> list:

    SCROLL_PAUSE = 2  # Pause to allow loading of content
    all_posts_hash = []

    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:

        links = driver.find_elements_by_xpath("//a[@href]")  # get all links on current page
        post_links = [link.get_attribute("href").split("/p/")[1].split("/?")[0] for link in links
                      if "taken-by" in link.get_attribute("href")]

        all_posts_hash.extend(post_links)
        all_posts_hash = list(set(all_posts_hash))  # keep only unique values

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        time.sleep(SCROLL_PAUSE)

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break

        last_height = new_height

    print(f"Number of gathered post links {len(all_posts_hash)}")

    return all_posts_hash


def scrape_post(driver: wd.Chrome, account: str, post_hash: str) -> tuple:

    post_url = f"https://www.instagram.com/p/{post_hash}/?taken-by={account}"
    post_url = "https://www.instagram.com/p/Bda3Q0yhOIS/?taken-by=nakljucni_mimojdoci"  # For testing

    # load the page with post
    driver.get(post_url)

    likes = scrape_post_likes(driver)
    comments = scrape_post_comments(driver)

    return likes, comments


def scrape_post_likes(driver: wd.Chrome) -> list:

    driver.find_element_by_partial_link_text("likes").click()
    xpath = "/html/body/div[3]/div/div[2]/div"  # xpath for likes modal
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath)))

    SCROLL_PAUSE = 1

    modalbox = "postlikesbox"
    scroll_class = "wwxN2 GD3H5 "
    scroll_modal(driver, SCROLL_PAUSE, modalbox, scroll_class)

    xpath = "/html/body/div[3]/div/div[2]/div/div/div[2]/ul/div/li"
    likes = extract_elements(driver, xpath)

    # Close the modal
    driver.find_element_by_class_name("Gzt1P").click()

    return likes


def scrape_post_comments(driver: wd.Chrome) -> zip:

    SCROLL_PAUSE = 1

    modalbox = "postcommentsbox"
    scroll_class = "KlCQn EtaWk"
    scroll_modal(driver, SCROLL_PAUSE, modalbox, scroll_class)

    xpath = "//*[@id='react-root']/section/main/div/div/article/div[2]/div[1]/ul/li"
    # comments = driver.find_element_by_class_name("gElp9 ")
    comments = driver.find_elements_by_xpath(xpath)

    users = [element.find_element_by_tag_name("a").text for element in comments]
    comments = [element.find_element_by_tag_name("span").text.encode("utf-8") for element in comments]

    user_w_comment = zip(users, comments)

    for usr, cmt in user_w_comment:
        print(f"User :{usr} has said: {cmt}")

    return user_w_comment


def extract_elements(driver: wd.Chrome, xpath: str) -> list:

    elements = driver.find_elements_by_xpath(xpath)
    elements_txt = [e.text for e in elements]  # List of followers (username, full name, follow text)
    elements_list = []  # List of followers (usernames only)

    # Go through each entry in the list, append the username to the followers list
    for i in elements_txt:
        username, sep, name = i.partition('\n')
        elements_list.append(username)

    return elements_list


def scroll_modal(driver: wd.Chrome, SCROLL_PAUSE: int, modalbox: str, scroll_class: str) -> None:

    driver.execute_script(f"{modalbox} = document.getElementsByClassName('{scroll_class}')[0];")
    last_height = driver.execute_script(f"return {modalbox}.scrollHeight;")

    # We need to scroll the modal to ensure that all elements are loaded
    while True:

        driver.execute_script(f"{modalbox}.scrollTo(0, {modalbox}.scrollHeight);")

        # Wait for page to load
        time.sleep(SCROLL_PAUSE)

        # Calculate new scrollHeight and compare with the previous
        new_height = driver.execute_script(f"return {modalbox}.scrollHeight;")

        if new_height == last_height:
            break

        last_height = new_height

    return None


if __name__ == "__main__":

    account = "evatisnikar"
    options = wd.ChromeOptions()
    options.binary_location = r"/usr/bin/google-chrome"  # Linux
    # options.binary_location = r"C:/Program Files (x86)/Google/Chrome/Application/chrome.exe"  # Windows'
    driver_binary = r"/home/leon/Projects/instascrape/chromedriver"
    driver = wd.Chrome(driver_binary, chrome_options=options)

    try:
        login(driver, "", "")  # login to you instagram account
        # scrape_post(driver, account, "sgsgg")
        load_account(driver, account)

        post_info = scrape_post(driver, "etst", "ssdgs")
        print(post_info)

    finally:
        driver.quit()
