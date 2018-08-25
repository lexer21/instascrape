
from instagram_driver import InstagramDriver
from instagram_scraper import InstagramAccount
from export_to_neo4j import MakeNetwork
from instagram_img_scraper import InstagramImage
import concurrent.futures

test_driver = InstagramDriver(username="", password="")
account2 = InstagramAccount(driver=test_driver.driver, account="sarraperic")
account2.extract_all()
test_graph2 = MakeNetwork(account2)
test_graph2.delete_graph()
test_graph2.create_connections()

# users = ["nakljucni_mimojdoci", "jfs3d", "laurajuvancic", "recyclableart", "mable3d", "vupalmo"]


def scrape(account: str):
    temp_driver = InstagramDriver(username="", password="")
    temp_account = InstagramAccount(driver=temp_driver.driver, account=account)
    temp_account.extract_all()

# TODO try to make this process run in parallel.


# with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
#
#     future_to_post = {executor.submit(scrape, account_name): account_name for account_name in users}
#
#     for future in concurrent.futures.as_completed(future_to_post):
#
#         post = future_to_post[future]
#
#         try:
#             data = future.result()
#         except Exception as exc:
#             print(f"Generated an exception: >> {exc}")
#
#
# # Hastags and image extraction
# account3 = InstagramImage(driver=test_driver.driver, account="jfs3d")
# account3.extract_all()
#
