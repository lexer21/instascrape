
from instagram_driver import InstagramDriver
from instagram_scraper_class import InstagramAccount
from export_to_neo4j import MakeNetwork

test_driver1 = InstagramDriver(username="", password="")

#
# account = InstagramAccount(driver=test_driver1.driver, account="sabrinacalcina")
# account.extract_all()
#
# test_graph1 = MakeNetwork(account)
# test_graph1.delete_graph()
#
# test_graph1.create_connections()


account2 = InstagramAccount(driver=test_driver1.driver, account="sarraperic")
account2.extract_all()
test_graph2 = MakeNetwork(account2)
test_graph2.delete_graph()
test_graph2.create_connections()

# account.scrape_post_links()
# account.scrape_all_posts()

# print(f"Account followers: {account.followers}")
# print(f"Account followers: {account.following}")
# print(f"Account bio: {account.account_bio}")

# print(f"Post hashes: {account.post_hash}")





