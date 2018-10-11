from drivers.instagram_driver import InstagramDriver
from scrapers.instagram_scraper import InstagramAccount
from exporters.json_exporter import MakeJson

# TODO add command line interface (CLI)
# TODO add some configuration file for the scraper


# Clean previous graph
# graph = Graph(user="neo4j", password="test1")
# graph.delete_all()

users = ["mijaumer", "sarabiondic", "pozarkim", "soraya.b__", "aganovicnensi", "masamihalic","poberajeva", "bitchfacenatalie"]

# scrape
temp_driver = InstagramDriver(username="xov71474", password="kolo1234")
temp_account = InstagramAccount(driver=temp_driver.driver, account="elisa.bianc")
temp_account.extract_all()

if not temp_account.account_private:
    temp_json = MakeJson(temp_account)
    temp_json.export_to_json()

# export to JSON


# export to Neo4j
# temp_graph = MakeNetwork(temp_account)
# temp_graph.create_connections()

#
# def scrape(account: str):
#
#     # scrape
#     temp_driver = InstagramDriver(username="nakljucni_mimojdoci", password="ektimo.4455")
#     temp_account = InstagramAccount(driver=temp_driver.driver, account=account)
#     temp_account.extract_all()
#
#     # export to Neo4j
#     temp_graph = MakeNetwork(temp_account)
#     temp_graph.create_connections()
#

# with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
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
