
from instagram_driver import InstagramDriver
from instagram_scraper_class import InstagramAccount


test_driver1 = InstagramDriver(username="", password="")


account = InstagramAccount(driver=test_driver1.driver, account="sarraperic")

account.load_account()

# account.scrape_following()
# account.scrape_followers()
# account.scrape_bio()
account.scrape_post_links()
account.scrape_all_post()

# print(f"Account followers: {account.followers}")
# print(f"Account followers: {account.following}")
# print(f"Account bio: {account.account_bio}")

print(f"Post hashes: {account.post_hash}")





