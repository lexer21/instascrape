from instagram_driver import InstagramDriver
from instagram_scraper import InstagramAccount
from neo4j_exporter import MakeNetwork
from instagram_img_scraper import InstagramImage
import concurrent.futures
import os

users = ["nakljucni_mimojdoci", "jfs3d", "laurajuvancic", "recyclableart", "mable3d", "vupalmo"]

# autorization not necessary


def scrape(account: str):
    temp_driver = InstagramDriver(username="", password="")
    temp_account = InstagramImage(driver=temp_driver.driver, account=account)
    temp_account.extract_all()


os.mkdir("accounts")

with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:

    future_to_post = {executor.submit(scrape, account_name): account_name for account_name in users}

    for future in concurrent.futures.as_completed(future_to_post):

        post = future_to_post[future]

        try:
            data = future.result()
        except Exception as exc:
            print(f"Generated an exception: >> {exc}")



