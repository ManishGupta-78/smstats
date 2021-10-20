"""
Get and Summarize Posts
"""
import requests
from smstats import config
from smstats import utils
from smstats.custom import Summary
from smstats import postutils

class PostManager:
    """
    Publishes information about posts
    """

    def __init__(self, settings=config.Config()):
        """
        Prepare to get posts
        """
        self.settings = settings
        self.get_token()

    def get_token(self):
        """
        Register a token with supermetrics service
        """
        response = requests.post(url=config.TOKEN_URL,
                                json={
                                    'client_id': self.settings.client_id,
                                    'email': self.settings.email,
                                    'name': self.settings.name})
        self.token = utils.get_resp_param('Get Token', response, 200, config.TOKEN_KEY)

    def get_posts(self, page):
        """
        Get a page of user posts
        """
        return requests.get(url=config.POSTS_URL,
                            params= {
                                'sl_token': self.token,
                                'page': page
                            })

    def get_posts_stats(self):
        """
        Get cumulative stats of user posts
        """
        summary = Summary()

        for page in range(1, self.settings.max_page+1):
            response = self.get_posts(page)

            # Token may have expired, try again
            if utils.match_resp_param(response, config.INVALID_TOKEN_RESPONSE):
                self.get_token()
                response = self.get_posts(page)

            posts = utils.get_resp_param('Get Posts', response, 200, config.POSTS_KEY)
            postutils.build_posts_summary(summary, posts)

        return postutils.get_stats(summary)
