# -*- coding: utf-8 -*-

import time
from selenium import webdriver as wd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re


class InstagramAccount:

    def __init__(self, driver: wd.Chrome, account: str):

        self.account_name = account
        self.driver = driver

        self.followers = []
        self.following = []
        self.post_hash = []
        self.posts = []

        self.account_alias = ""
        self.account_bio = ""

        self.SCROLL_PAUSE = 1

    def load_account(self):

        # Load account page
        account_url = f"https://www.instagram.com/{self.account_name}/"
        print(account_url)
        self.driver.get(account_url)

    def scrape_followers(self):

        # Click the 'Follower(s)' link
        self.driver.find_element_by_partial_link_text("follower").click()

        # Wait for the followers modal to load
        xpath = "/html/body/div[3]/div/div[2]/div"
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath)))

        SCROLL_PAUSE = 1  # Pause to allow loading of content

        modalbox = "followersbox"
        scroll_class = "j6cq2"
        self.scroll_modal(modalbox, scroll_class)

        xpath = "/html/body/div[3]/div/div[2]/div/div[2]/ul/div/li"  # xpath for follower elements
        self.followers = self.extract_elements(xpath)  # extract followers usernames

        # exit the modal
        self.driver.find_element_by_class_name("ckWGn").click()

    def scrape_following(self):

        self.driver.find_element_by_partial_link_text("following").click()

        xpath = "/html/body/div[3]/div/div[2]/div"
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath)))

        self.SCROLL_PAUSE = 1

        modalbox = "followingbox"
        scroll_class = "j6cq2"
        self.scroll_modal(modalbox, scroll_class)

        xpath = "/html/body/div[3]/div/div[2]/div/div[2]/ul/div/li"
        self.following = self.extract_elements(xpath)

        self.driver.find_element_by_class_name("ckWGn").click()

    def scrape_bio(self):

        elements = self.driver.find_element_by_class_name("-vDIg")
        self.account_alias = elements.find_element_by_tag_name("h1").text
        self.account_bio = elements.find_element_by_tag_name("span").text.encode("utf-8")

    def scrape_post_links(self):

        SCROLL_PAUSE = 2  # Pause to allow loading of content
        all_posts_hash = []

        last_height = self.driver.execute_script("return document.body.scrollHeight")

        while True:

            links = self.driver.find_elements_by_xpath("//a[@href]")  # get all links on current page
            post_links = [link.get_attribute("href").split("/p/")[1].split("/?")[0] for link in links
                          if "taken-by" in link.get_attribute("href")]

            all_posts_hash.extend(post_links)
            all_posts_hash = list(set(all_posts_hash))  # keep only unique values

            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            time.sleep(SCROLL_PAUSE)

            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break

            last_height = new_height

        print(f"Number of gathered post links {len(all_posts_hash)}")

        self.post_hash = all_posts_hash

    def scrape_all_posts(self):

        temp = 0
        for hash in self.post_hash:

            temp += 1
            self.scrape_post(hash)

            if temp == 5:
                break

    def scrape_post(self, post_hash: str):

        post_url = f"https://www.instagram.com/p/{post_hash}/?taken-by={self.account_name}"
        # post_url = "https://www.instagram.com/p/Bda3Q0yhOIS/?taken-by=nakljucni_mimojdoci"  # For testing

        self.driver.get(post_url)

        likes = self.scrape_post_likes()
        comments = self.scrape_post_comments()

        #extract hashtags over all comments

        hashtags = self.extract_hashtags(comments)
        tags = self.extract_tags(comments)
        # print(comments)

        self.posts.append([post_hash, likes, comments, hashtags, tags])

        # print(self.posts)

    def scrape_post_likes(self) -> list:

        self.driver.find_element_by_partial_link_text("likes").click()
        xpath = "/html/body/div[3]/div/div[2]/div"  # xpath for likes modal
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath)))

        SCROLL_PAUSE = 1

        modalbox = "postlikesbox"
        scroll_class = "wwxN2 GD3H5 "
        self.scroll_modal(modalbox, scroll_class)

        xpath = "/html/body/div[3]/div/div[2]/div/div/div[2]/ul/div/li"
        likes = self.extract_elements(xpath)

        # Close the modal
        self.driver.find_element_by_class_name("Gzt1P").click()

        return likes

    def scrape_post_comments(self) -> list:

        SCROLL_PAUSE = 1

        modalbox = "postcommentsbox"
        scroll_class = "KlCQn EtaWk"
        self.scroll_modal(modalbox, scroll_class)

        xpath = "//*[@id='react-root']/section/main/div/div/article/div[2]/div[1]/ul/li"
        # comments = driver.find_element_by_class_name("gElp9 ")
        comments = self.driver.find_elements_by_xpath(xpath)

        users = [element.find_element_by_tag_name("a").text for element in comments]
        comments = [element.find_element_by_tag_name("span").text.encode("utf-8") for element in comments]

        user_w_comment = list(map(list, zip(users, comments)))
        # for usr, cmt in user_w_comment:
        #     print(f"User :{usr} has said: {cmt}")

        return user_w_comment

    def extract_tags(self, comments: str) -> list:

        tags = []

        for comment in comments:

            decode_cmt = comment[1].decode("utf-8")
            tag_words = re.findall(r"\@\w+", decode_cmt)

            for tag in tag_words:
                tags.append(tag[1:])

        return tags

    def extract_all(self):

        self.load_account()
        self.scrape_followers()
        self.scrape_following()
        self.scrape_bio()
        self.scrape_post_links()
        self.scrape_all_posts()
        self.driver.quit()

    def extract_elements(self, xpath: str) -> list:

        elements = self.driver.find_elements_by_xpath(xpath)
        elements_txt = [e.text for e in elements]  # List of followers (username, full name, follow text)
        elements_list = []  # List of followers (usernames only)

        # Go through each entry in the list, append the username to the followers liusernamesst
        for i in elements_txt:
            username, sep, name = i.partition('\n')
            elements_list.append(username)

        return elements_list

    def extract_hashtags(self, comments: list) -> list:

        hashtags = []
        for comment in comments:

            decode_cmt = comment[1].decode("utf-8")
            cmts_words = re.findall(r"\#\w+", decode_cmt)

            for cmt in cmts_words:
                hashtags.append(cmt)

        return hashtags

    def scroll_modal(self, modalbox: str, scroll_class: str):

        try:
            self.driver.execute_script(f"{modalbox} = document.getElementsByClassName('{scroll_class}')[0];")
            last_height = self.driver.execute_script(f"return {modalbox}.scrollHeight;")

            # We need to scroll the modal to ensure that all elements are loaded
            while True:

                self.driver.execute_script(f"{modalbox}.scrollTo(0, {modalbox}.scrollHeight);")

                # Wait for page to load
                time.sleep(self.SCROLL_PAUSE)

                # Calculate new scrollHeight and compare with the previous
                new_height = self.driver.execute_script(f"return {modalbox}.scrollHeight;")

                if new_height == last_height:
                    break

                last_height = new_height
        except Exception as e:
            print(f"Generated an exception : {e}")
