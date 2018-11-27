# -*- coding: utf-8 -*-

import configparser
import random
import re
import time
from functools import wraps
from queue import Queue
from threading import Thread

from selenium import webdriver as wd
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


# TODO poenoti pridobivanje podatkov iz html-ja, probaj naredit da bo čim manj vzdrževanja potrebno, imena v config dat
# TODO add better exception handling
# TODO add maximum amount for post, likes, comments, ...
# TODO add random scrolling up and down to load followers and following elements, seems like new scraping protection

def timing(f):
    @wraps(f)
    def wrap(*args, **kw):
        ts = time.time()
        result = f(*args, **kw)
        te = time.time()
        print('func:%r args:[%r, %r] took: %2.4f sec' % (f.__name__, args, kw, te - ts))
        return result

    return wrap


# LOADING CONFIGURATION PARAMETERS

config = configparser.ConfigParser()
config.read("scrapers/scraper_config.ini")

# num_threads = 2
process_queue = Queue()

# Maybe move to another file

MAX_SCROLL_RETRY = int(config["scraper"]["MAX_SCROLL_RETRY"])
SCROLL_PAUSE = float(config["scraper"]["SCROLL_PAUSE"])
SCROLL_PAUSE_LINK = float(config["scraper"]["SCROLL_PAUSE_LINK"])
MAX_SCROLL_ELEMENTS = int(config["scraper"]["MAX_SCROLL_ELEMENTS"])


# END OF CONFIGURATION

class InstagramAccount:

    def __init__(self, driver: wd.Chrome, account: str):

        self.account_name = account
        self.driver = driver
        self.account_id = None  # Can be obtained via html
        self.account_private = False

        self.followers = []
        self.following = []
        self.post_hash = []
        self.posts = []

        self.account_alias = ""
        self.account_bio = ""

        self.SCROLL_PAUSE = SCROLL_PAUSE
        self.SCROLL_PAUSE_LINK = SCROLL_PAUSE_LINK

    def load_account(self):

        account_url = f"https://www.instagram.com/{self.account_name}/"

        # Load account page
        print(f"Loading {account_url}")
        self.driver.get(account_url)
        self.check_if_private()

    def check_if_private(self):

        try:
            if self.driver.find_elements_by_xpath("//*[contains(text(), 'This Account is Private')]"):
                print(f"Account: {self.account_name} is PRIVATE, cannot access information, quitting!")
                self.account_private = True
        except:
            print("Account is public")
            pass

    def scrape_followers(self, click_link: str, modalbox: str, str_index: int, save_location):

        class_name = "g47SY"
        xpath = "/html/body/div[3]/div/div"
        scroll_class = "isgrP"
        scroll_xpath = "/html/body/div[3]/div/div/div[2]/ul/div/li"

        # Extract number of followers
        follow = self.driver.find_elements_by_class_name(class_name)[str_index].text
        num_followers = self.extract_number(follow)

        # Click the 'Follower(s)' link to load modal
        self.driver.find_element_by_partial_link_text(click_link).click()

        # Wait for the modal to load
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath)))

        print("Scrolling and collecting elements")

        self.scroll_modal(modalbox, scroll_class, num_followers, scroll_xpath, save_location)

        # exit the modal, but wait little bit before that
        time.sleep(1)
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

            # We actuall extracted post hashes, which in turn give us the links
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

    @timing
    def scrape_post(self, post_hash: str):

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

    def anti_scrape(self, modalbox: str, scroll_class: str):

        # self.driver.execute_script(f"{modalbox} = document.getElementsByClassName('{scroll_class}')[0];")

        for i in range(5):
            print("Scroll up")
            self.driver.execute_script(f"{modalbox}.scrollTo(0, 0);")
            time.sleep(1)
            print("Scroll Down")
            self.driver.execute_script(f"{modalbox}.scrollTo(0, {modalbox}.scrollHeight/2);")

    @timing
    def scrape_post_likes(self) -> list:

        class_name = "zV_Nj"
        xpath = "/html/body/div[3]/div/div[2]/div"
        scroll_class = "wwxN2 GD3H5 "
        scroll_xpath = "/html/body/div[3]/div/div[2]/div/div/div[2]/ul/div/li"

        # Get number of likes
        element = self.driver.find_element_by_class_name(class_name)

        num_of_likes = int((element.find_element_by_tag_name("span").text.replace(",", "")))

        print(f"Number of likes is: {num_of_likes}")

        self.driver.find_element_by_partial_link_text("likes").click()
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath)))

        modalbox = "postlikesbox"

        likes = []
        self.scroll_modal(modalbox, scroll_class, num_of_likes, scroll_xpath, likes)

        time.sleep(.25)

        # Close the modal
        self.driver.find_element_by_class_name("Gzt1P").click()

        print(f"Gathered likes are {likes}")

        return likes

    @timing
    def scrape_post_comments(self) -> list:

        modalbox = "commentsbox"
        scroll_class = "KlCQn EtaWk"

        while True:
            try:
                self.driver.find_element_by_class_name("lnrre").find_element_by_tag_name("button").click()
                time.sleep(1)
                self.scroll_to_top(modalbox, scroll_class)
            except:
                # print("No more comments found")
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
    @timing
    def extract_tags(comments: list) -> list:

        tags = []
        for comment in comments:

            decode_cmt = comment[1]
            tag_words = re.findall(r"\@\w+", decode_cmt)

            for tag in tag_words:
                tags.append(tag[1:])

        return tags

    def extract_all_information(self):

        self.load_account()

        if not self.account_private:

            testvar = 154
            self.scrape_followers(click_link="follower", modalbox="followersbox", str_index=1,
                                  save_location=self.followers)

            import pdb
            pdb.set_trace()

            self.scrape_followers(click_link="following", modalbox="followingbox", str_index=2,
                                  save_location=self.following)

            print(f"Number of unique followers: {len(set(self.followers))}")
            print(f"Number of unique following: {len(set(self.following))}")
            #
            #
            # self.scrape_bio()
            # self.scrape_post_links()
            # self.scrape_all_posts()

            # TODO queue does not exit somehow??
            process_queue.join()

        # self.scrape_post()  # za testirat

        self.driver.quit()

    @staticmethod
    def extract_elements(id, q):
        while True:
            # Problem is that we leave the modal before we can extract them
            elements, save_loc = q.get()

            print(f"Extracting elements in thread {id}")
            # print(elements)
            elements_txt = [e.text for e in elements]

            elements_list = []  # List of followers (usernames only)

            # Go through each entry in the list, append the username to the followers liusernamesst
            for i in elements_txt:
                username, sep, name = i.partition('\n')
                elements_list.append(username)

            print(elements_list)
            print("Thead process finished")

            # Extend extracted elements to specified array
            save_loc.extend(elements_list)

            q.task_done()

    @staticmethod
    @timing
    def extract_hashtags(comments: list) -> list:

        hashtags = []
        for comment in comments:

            decode_cmt = comment[1]
            cmts_words = re.findall(r"\#\w+", decode_cmt)

            for cmt in cmts_words:
                hashtags.append(cmt)

        return hashtags

    @staticmethod
    def extract_number(followers: str) -> int:
        # TODO implement less error prone conversion, excepting also formatis in k, m..
        return int(followers.replace(",", ""))

    def scroll_modal(self, modalbox: str, scroll_class: str, max_num_elements: int, xpath: str, save_location):

        self.driver.execute_script(f"{modalbox} = document.getElementsByClassName('{scroll_class}')[0];")
        # last_height = self.driver.execute_script(f"return {modalbox}.scrollHeight;")

        # Wait for the modal to load
        time.sleep(0.5)

        for i in range(4):
            self.driver.execute_script(f"{modalbox}.scrollTo(0, {modalbox}.scrollHeight);")
            time.sleep(2)
            print("Scrolling")
            self.driver.execute_script(f"{modalbox}.scrollTo(0, 300);")
            time.sleep(2)

        time.sleep(3)

        # self.driver.execute_script(f"{modalbox}.scrollTo(0, 0);")
        # time.sleep(2)
        # self.driver.execute_script(f"{modalbox}.scrollTo(0, 100);")

        # TODO explain variables
        delta_time = 0
        current_num_elements = 0
        non_increase = 0  # For keeping track how many times we did not load any new elements
        temp = 0

        while True:

            # Scrolls the the bottom of the modal and triggers loading of new elements
            self.driver.execute_script(f"{modalbox}.scrollTo(0, {modalbox}.scrollHeight);")

            # Wait for new scrolled elements to load
            time.sleep(self.SCROLL_PAUSE + delta_time)

            new_num_elements = len(self.driver.find_elements_by_xpath(xpath)) - current_num_elements
            current_num_elements = len(self.driver.find_elements_by_xpath(xpath))

            start_index = current_num_elements - new_num_elements
            end_index = current_num_elements

            # print([element.text for element in self.driver.find_elements_by_xpath(xpath)[start_index:end_index-1]])

            if current_num_elements > MAX_SCROLL_ELEMENTS:
                print("Scraped all elements")
                break

            # Check if we got new elements, if not increase the load time
            if new_num_elements == 0:
                # print("Increasing the time to load elements!")
                non_increase += 1
                delta_time += 0.15

                if non_increase > MAX_SCROLL_RETRY:
                    print(f"{start_index} ... {end_index} // {max_num_elements} ...quiting")

                    # Put the last one in
                    # process_queue.put(
                    #     (self.driver.find_elements_by_xpath(xpath)[end_index], save_location))
                    # print("Exceeded the maximum retry amount, quiting")

                    break
                else:
                    continue

            if current_num_elements == max_num_elements:
                # process_queue.put(
                #     (self.driver.find_elements_by_xpath(xpath)[end_index], save_location))
                # print("We scraped all elements of the modal... exiting!")
                break

            # Minus one at the index becuase it takes one more element that it actualy findd and then crashes the scraping
            # TODO explore more the exact couse of the problem
            process_queue.put(
                (self.driver.find_elements_by_xpath(xpath)[start_index - temp:end_index - 1], save_location))

            if temp == 0:
                temp = 1


worker = Thread(target=InstagramAccount.extract_elements, args=(1, process_queue,))
worker.start()
