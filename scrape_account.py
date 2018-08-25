from instagram_driver import InstagramDriver
from instagram_scraper import InstagramAccount
from neo4j_exporter import MakeNetwork
import concurrent.futures
from py2neo import Graph


# Clean previus graph
graph = Graph(user="neo4j", password="test1")
graph.delete_all()

users = ["sarraperic", "evafurlanb"]


def scrape(account: str):

    # scrape
    temp_driver = InstagramDriver(username="", password="")
    temp_account = InstagramAccount(driver=temp_driver.driver, account=account)
    temp_account.extract_all()

    # export to Neo4j
    temp_graph = MakeNetwork(temp_account)
    temp_graph.delete_graph()
    temp_graph.create_connections()


with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:

    future_to_post = {executor.submit(scrape, account_name): account_name for account_name in users}

    for future in concurrent.futures.as_completed(future_to_post):

        post = future_to_post[future]

        try:
            data = future.result()
        except Exception as exc:
            print(f"Generated an exception: >> {exc}")


