import json

from scrapers.instagram_scraper import InstagramAccount


class MakeJson:

    def __init__(self, account: InstagramAccount):
        self.account = account

    def export_to_json(self):
        post_list = []

        for post in self.account.posts:
            # Adding src url may be redundant?
            post_dict = {
                "post_hash": post[0],
                "post_likes": [like for like in post[1]],
                "post_tag": [tag for tag in post[2]],
                "post_hashtags": [hashtags for hashtags in post[3]],
                "comments": [{"cmt_usr": comment[0], "message": comment[1]} for comment in post[2]]
            }

            post_list.append(post_dict)

        # print(self.account.posts)

        user_data = {
            "username": self.account.account_name,
            "account_alias": self.account.account_alias,
            "account_bio": self.account.account_bio,
            "followers:": self.account.followers,
            "following:": self.account.following,
            "posts": post_list
        }

        # pprint(user_data)

        with open(f"data/json/{self.account.account_name}", 'w') as outfile:
            json.dump(user_data, outfile, sort_keys=True, indent=4)
