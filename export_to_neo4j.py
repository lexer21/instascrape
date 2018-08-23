from py2neo import Graph
from py2neo import Node, Relationship, NodeMatcher
from instagram_scraper import InstagramAccount


class MakeNetwork:

    def __init__(self, account: InstagramAccount):

        self.graph = Graph(user="neo4j", password="test1")

        self.account = account

        self.root_node = Node("account", username=self.account.account_name, alias_name=self.account.account_name)

    def delete_graph(self):
        self.graph.delete_all()

    def create_connections(self):

        for follower in self.account.followers:

            follower_node = Node("account", username=follower, alias_name=follower)
            follower_relationship = Relationship(follower_node, "follows", self.root_node)
            self.graph.create(follower_relationship)

        for following in self.account.following:
            following_node = Node("account", username=following, alias_name=following)
            following_relationship = Relationship(self.root_node, "follows", following_node)
            self.graph.create(following_relationship)

        for post in self.account.posts:
            post_node = Node("post", post_hash=post[0])

            owner_relation = Relationship(self.root_node, "owner", post_node)
            self.graph.create(owner_relation)

            for like in post[1]:

                matcher = NodeMatcher(self.graph)
                m = matcher.match("account", username=like).first()

                if not m:
                    like_user = Node("account", username=like, alias_name=like)
                    like_relation = Relationship(like_user, "likes", post_node)
                else:
                    like_relation = Relationship(m, "like", post_node)

                self.graph.create(like_relation)

            for comment in post[2]:

                matcher = NodeMatcher(self.graph)
                m = matcher.match("account", username=comment[0]).first()

                if not m:
                    comment_user = Node("account", username=comment[0], alias_name=comment[0])
                    comment_relation = Relationship(comment_user, "comment", post_node, usr_message=str(comment[1]))
                else:
                    comment_relation = Relationship(m, "comment", post_node, usr_message=str(comment[1]))

                self.graph.create(comment_relation)
