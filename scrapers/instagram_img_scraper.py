from scrapers.instagram_scraper import InstagramAccount
from urllib import request
import os

# TODO option to also download videos

class InstagramImage(InstagramAccount):

    def __init__(self, *args, **kwargs):
        super(InstagramImage, self).__init__(*args, **kwargs)

    def scrape_post(self, post_hash: str):

        post_url = f"https://www.instagram.com/p/{post_hash}/?taken-by={self.account_name}"

        self.driver.get(post_url)

        try:
            images = self.driver.find_elements_by_class_name("FFVAD")
        except Exception as e:
            print(e)
            return

        images_url = []
        for src_attr in images:
            print(str(src_attr.get_attribute("src")))

            images_url.append(str(src_attr.get_attribute("src")))

        for i, url in enumerate(images_url):
            self.download_image(post_hash, url, i)

        comments = self.scrape_post_comments()

        hashtags = self.extract_hashtags(comments)

        if hashtags:
            self.write_hashtags(hashtags, post_hash)

    def scrape_all_images(self):

        for p_hash in self.post_hash:
            self.scrape_post(p_hash)

    def extract_all(self):

        try:
            os.mkdir(f"accounts/{self.account_name}")
        except Exception as e:
            print(e)

        self.load_account()
        self.scrape_post_links()
        self.scrape_all_images()
        self.driver.quit()

    def download_image(self, post_hash: str, image_url: str, img_num: int):

        f = open(f"accounts/{self.account_name}/{post_hash}_{img_num}.jpg", "wb")
        f.write(request.urlopen(image_url).read())
        f.close()

    def write_hashtags(self, hashtags: list, post_hash: str):

        with open(f"accounts/{self.account_name}/{post_hash}.txt", "w") as f:

            for hashtag in hashtags:
                f.write(f"{hashtag}\n")
