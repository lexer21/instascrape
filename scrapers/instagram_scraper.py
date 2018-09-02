# -*- coding: utf-8 -*-

from selenium import webdriver as wd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import random
import time


# TODO add better exception handling
# TODO some problems with tags

# TODO add maximum amount for post, likes, comments, ...

class InstagramAccount:

    def __init__(self, driver: wd.Chrome, account: str):

        self.account_name = account
        self.driver = driver
        self.account_id = None  # Can be obtained
        self.account_private = False

        self.followers = []
        self.following = []
        self.post_hash = []
        self.posts = []

        self.account_alias = ""
        self.account_bio = ""

        self.SCROLL_PAUSE = .25
        self.SCROLL_PAUSE_LINK = 2.5

    def load_account(self):

        # Load account page
        account_url = f"https://www.instagram.com/{self.account_name}/"

        print(account_url)
        self.driver.get(account_url)

        self.check_if_private()


    def scrape_followers(self):

        # Get number of followers
        num_followers = int(self.driver.find_elements_by_class_name("g47SY")[1].text)
        print(f"Number of folowers: {num_followers}")

        # Click the 'Follower(s)' link
        self.driver.find_element_by_partial_link_text("follower").click()

        # Wait for the followers modal to load
        xpath = "/html/body/div[3]/div/div"
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath)))

        modalbox = "followersbox"
        scroll_class = "j6cq2"
        xpath = "/html/body/div[3]/div/div/div[2]/ul/div/li"

        print("Collecting user elements")
        self.scroll_modal(modalbox, scroll_class, num_followers, xpath)

        print("Extracting usernames")
        self.followers = self.extract_elements(xpath)  # extract followers usernames

        # exit the modal
        self.driver.find_element_by_xpath("/html/body/div[3]/div/div/div[1]/div[2]/button").click()

    def scrape_following(self):

        # get number of following
        num_following = int(self.driver.find_elements_by_class_name("g47SY")[2].text)
        print(f"Number of folowers: {num_following}")

        self.driver.find_element_by_partial_link_text("following").click()
        xpath = "/html/body/div[3]/div/div"
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath)))

        modalbox = "followingbox"
        scroll_class = "j6cq2"

        xpath = "/html/body/div[3]/div/div/div[2]/ul/div/li"
        self.scroll_modal(modalbox, scroll_class, num_following, xpath)

        self.following = self.extract_elements(xpath)

        self.driver.find_element_by_xpath("/html/body/div[3]/div/div/div[1]/div[2]/button").click()

    def scrape_bio(self):

        elements = self.driver.find_element_by_class_name("-vDIg")
        self.account_alias = elements.find_element_by_tag_name("h1").text
        try:
            self.account_bio = elements.find_element_by_tag_name("span").text
        except:
            print("Bio is empty")
            self.account_bio = None

    def scrape_post_links(self):

        all_posts_hash = []

        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:

            links = self.driver.find_elements_by_xpath("//a[@href]")  # get all links on current page
            post_links = [link.get_attribute("href").split("/p/")[1].split("/?")[0] for link in links
                          if "taken-by" in link.get_attribute("href")]

            all_posts_hash.extend(post_links)
            all_posts_hash = list(set(all_posts_hash))  # keep only unique values

            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            time.sleep(self.SCROLL_PAUSE_LINK + random.random())

            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break

            last_height = new_height

        print(f"Number of gathered post links {len(all_posts_hash)}")

        self.post_hash = all_posts_hash

    def scrape_all_posts(self):

        for i, hash in enumerate(self.post_hash):
            print(f"Scraping post :: {i}")
            self.scrape_post(hash)

    def scrape_post(self, post_hash: str = "sgsdggsg"):

        post_url = f"https://www.instagram.com/p/{post_hash}/?taken-by={self.account_name}"

        # Loads the post
        self.driver.get(post_url)
        time.sleep(0.1)

        # If video, skip scraping post, else continue
        try:
            if self.driver.find_element_by_class_name("jNBsH"):
                print("Video found")
                return None
        except:
            print("")

        likes = self.scrape_post_likes()
        comments = self.scrape_post_comments()

        hashtags = self.extract_hashtags(comments)
        tags = self.extract_tags(comments)

        self.posts.append([post_hash, likes, comments, hashtags, tags])

    def scrape_post_likes(self) -> list:

        # Get number of likes
        element = self.driver.find_element_by_class_name("zV_Nj")

        num_of_likes = int((element.find_element_by_tag_name("span").text.replace(",", "")))

        print(f"Number of likes is: {num_of_likes}")

        self.driver.find_element_by_partial_link_text("likes").click()
        xpath = "/html/body/div[3]/div/div[2]/div"  # xpath for likes modal
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath)))

        modalbox = "postlikesbox"
        scroll_class = "wwxN2 GD3H5 "
        xpath = "/html/body/div[3]/div/div[2]/div/div/div[2]/ul/div/li"

        self.scroll_modal(modalbox, scroll_class, num_elements=num_of_likes, xpath=xpath)

        time.sleep(.25)
        likes = self.extract_elements(xpath)

        # Close the modal
        self.driver.find_element_by_class_name("Gzt1P").click()

        return likes

    def scrape_post_comments(self) -> list:

        modalbox = "commentsbox"
        scroll_class = "KlCQn EtaWk"

        while True:
            try:
                self.driver.find_element_by_class_name("lnrre").find_element_by_tag_name("button").click()
                time.sleep(1)
                self.scroll_to_top(modalbox, scroll_class)
            except:
                print("No more comments found")
                break

        xpath = "//*[@id='react-root']/section/main/div/div/article/div[2]/div[1]/ul/li"
        comments = self.driver.find_elements_by_xpath(xpath)
        users = [element.find_element_by_tag_name("a").text for element in comments]
        comments = [element.find_element_by_tag_name("span").text for element in comments]

        user_w_comment = list(map(list, zip(users, comments)))
        # for usr, cmt in user_w_comment:
        #     print(f"User :{usr} has said: {cmt}")

        return user_w_comment

    def scroll_to_top(self, modalbox: str, scroll_class: str):

        self.driver.execute_script(f"{modalbox} = document.getElementsByClassName('{scroll_class}')[0];")
        self.driver.execute_script(f"{modalbox}.scrollTo(0, 0);")

    @staticmethod
    def extract_tags(comments: list) -> list:

        tags = []

        for comment in comments:

            decode_cmt = comment[1]
            tag_words = re.findall(r"\@\w+", decode_cmt)

            for tag in tag_words:
                tags.append(tag[1:])

        return tags

    def extract_all(self):

        self.load_account()

        if not self.account_private:

            self.scrape_followers()
            self.scrape_following()
            self.scrape_bio()
            self.scrape_post_links()
            self.scrape_all_posts()

        # self.scrape_post()  # za testirat
        self.driver.quit()

    def extract_elements(self, xpath: str) -> list:

        elements = self.driver.find_elements_by_xpath(xpath)
        elements_txt = [e.text for e in elements]  # List of followers (username, full name, follow text)
        elements_list = []  # List of followers (usernames only)

        # Go through each entry in the list, append the username to the followers liusernamesst
        for i in elements_txt:
            username, sep, name = i.partition('\n')
            elements_list.append(username)

        print(elements_list)

        return elements_list

    @staticmethod
    def extract_hashtags(comments: list) -> list:

        hashtags = []
        for comment in comments:

            decode_cmt = comment[1]
            cmts_words = re.findall(r"\#\w+", decode_cmt)

            for cmt in cmts_words:
                hashtags.append(cmt)

        return hashtags

    def scroll_modal(self, modalbox: str, scroll_class: str, num_elements: int, xpath: str):

        try:
            self.driver.execute_script(f"{modalbox} = document.getElementsByClassName('{scroll_class}')[0];")
            last_height = self.driver.execute_script(f"return {modalbox}.scrollHeight;")
            delta_time = 0
            # We need to scroll the modal to ensure that all elements are loaded

            non_increase = 0
            relative_dif = 0

            while True:

                # This triggers the loading
                self.driver.execute_script(f"{modalbox}.scrollTo(0, {modalbox}.scrollHeight);")

                nums1 = len(self.driver.find_elements_by_xpath(xpath))

                # Wait for page to load
                time.sleep(self.SCROLL_PAUSE + delta_time)
                print(f"Time for sleep: {self.SCROLL_PAUSE + delta_time}")

                nums2 = len(self.driver.find_elements_by_xpath(xpath))
                print(f"{nums1} -- {nums2} // {num_elements}")

                if relative_dif == (num_elements - nums2):
                    non_increase += 1

                if nums2 == num_elements:
                    print("We are at the end")
                    break

                elif nums1 == nums2:
                    print("Need more time to load elements!")
                    delta_time += 0.05

                    if non_increase > 5:
                        break

                    relative_dif = num_elements - nums2
                    continue

        except Exception as e:

            print(f"Generated an exception : {e}")

    def check_if_private(self):

        try:
            if self.driver.find_elements_by_xpath("//*[contains(text(), 'This Account is Private')]"):
                print(f"Account: {self.account_name} is PRIVATE, cannot access information, quitting!")
                self.account_private = True
        except:
            pass
