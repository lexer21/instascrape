
from instagram_driver import InstagramDriver
from instagram_scraper import InstagramAccount
from export_to_neo4j import MakeNetwork
from instagram_img_scraper import InstagramImage

test_driver1 = InstagramDriver(username="", password="")

account2 = InstagramAccount(driver=test_driver1.driver, account="sarraperic")
account2.extract_all()
test_graph2 = MakeNetwork(account2)
test_graph2.delete_graph()
test_graph2.create_connections()



# Hastags and image extraction
# account3 = InstagramImage(driver=test_driver1.driver, account="nakljucni_mimojdoci")
# account3.extract_all()


# TODO try to make this process run in parallel.