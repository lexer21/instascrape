from instagram_scraper import InstagramAccount
from urllib import request
import os
import re

class InstagramImage(InstagramAccount):

    def __init__(self, *args, **kwargs):
        super(InstagramImage, self).__init__(*args, **kwargs)

    def scrape_post(self, post_hash: str):

        """
        Here we scrape comments and extract the hashtags and download the images
        :param post_hash:
        :return:
        """
        post_url = f"https://www.instagram.com/p/{post_hash}/?taken-by={self.account_name}"

        self.driver.get(post_url)

        image = self.driver.find_element_by_class_name("FFVAD")
        image_url = str(image.get_attribute("src"))

        self.download_image(post_hash, image_url)

        comments = self.scrape_post_comments()

        hashtags = self.extract_hashtags(comments)

        if hashtags:
            self.write_hashtags(hashtags, post_hash)

    def scrape_all_images(self):

        for hash in self.post_hash:
            self.scrape_post(hash)

    def extract_all(self):

        try:
            os.mkdir(self.account_name)
        except Exception as e:
            print(e)

        self.load_account()
        self.scrape_post_links()
        self.scrape_all_images()

    def download_image(self, post_hash: str, image_url: str):

        f = open(f"{self.account_name}/{post_hash}.jpg", "wb")
        f.write(request.urlopen(image_url).read())
        f.close()

    # def extract_hashtags(self, comments:list) -> list:
    #
    #     hashtags = []
    #     for comment in  comments:
    #
    #         decode_cmt = comment[1].decode("utf-8")
    #         cmts_words = re.findall(r"\#\w+", decode_cmt)
    #
    #         for cmt in cmts_words:
    #             hashtags.append(cmt)
    #
    #     return hashtags

    def write_hashtags(self, hashtags: list, post_hash: str):

        with open(f"{self.account_name}/{post_hash}.txt", "w") as f:

            for hashtag in hashtags:
                f.write(f"{hashtag}\n")