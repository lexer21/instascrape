from py2neo import Node, Relationship, NodeMatcher, Graph
from scrapers.instagram_scraper import InstagramAccount


class MakeNetwork:

    def __init__(self, account: InstagramAccount):

        self.graph = Graph(user="neo4j", password="test1")

        self.account = account

        # TODO add bio and other info about account, but make sure doesnt create conflicts when making relationshis
        
        matcher = NodeMatcher(self.graph)
        m = matcher.match("account", username=self.account.account_name).first()

        if not m:
            self.root_node = Node("account", username=self.account.account_name, alias_name=self.account.account_name)
        else:
            self.root_node = m

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

            # post[0] -> post_hash
            # post[1] -> post_likes
            # post[2] -> post_comments
            # post[3] -> post_hashtags
            # post[4] -> post_tags

            post_node = Node("post", post_hash=post[0], post_hashtags=post[3])

            owner_relation = Relationship(self.root_node, "owner", post_node)
            self.graph.create(owner_relation)

            for like in post[1]:

                matcher = NodeMatcher(self.graph)
                m = matcher.match("account", username=like).first()

                if not m:
                    like_user = Node("account", username=like, alias_name=like)
                    like_relation = Relationship(like_user, "likes", post_node)
                else:
                    like_relation = Relationship(m, "likes", post_node)

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

            for tag in post[4]:

                matcher = NodeMatcher(self.graph)
                m = matcher.match("account", username=tag).first()

                if not m:
                    tagged_user = Node("account", username=tag, alias_name=tag)
                    tag_relation = Relationship(post_node, "taged", tagged_user)
                else:

                    tag_relation = Relationship(post_node, "taged", m)

                self.graph.create(tag_relation)
