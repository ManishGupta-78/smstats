"""
Unit test to verify Supermetrics stats package
"""
import unittest
import unittest.mock
from unittest.mock import patch, ANY
import json
from requests import Response
from smstats import PostManager, Config, DataGetError

class TestSMStats(unittest.TestCase):
    """
    Test stats gatherer from Supermetrics stats package
    """

    @staticmethod
    def get_valid_token(*_, **__):
        """
        Mock registering a token with Supermetrics
        """
        post_response = Response()
        post_response.status_code = 200
        with open('resources/token_response.json', 'rb') as resp:
            post_response._content = resp.read() # pylint: disable=W0212

        return post_response

    @staticmethod
    def get_invalid_token(*_, **__):
        """
        Mock getting a token from Supermetrics which will be treated as expired/invalid
        """
        post_response = Response()
        post_response.status_code = 200
        with open('resources/invalid_token_response.json', 'rb') as resp:
            post_response._content = resp.read() # pylint: disable=W0212

        return post_response

    @staticmethod
    def get_no_token_response(*_, **__):
        """
        Mock failed attempt to register a token with Supermetrics
        """
        post_response = Response()
        post_response.status_code = 500
        return post_response

    @staticmethod
    def get_valid_posts(*_, **kwargs):
        """
        Mock getting user post from Supermetrics
        """
        token = kwargs['params']['sl_token']
        page = kwargs['params']['page']
        get_response = Response()

        if token != 'invalid':
            get_response.status_code = 200
            with open(f'resources/post_response_p{page}.json', 'rb') as resp:
                get_response._content = resp.read() # pylint: disable=W0212
        else:
            get_response.status_code = 500
            with open('resources/post_invalid_token.json', 'rb') as resp:
                get_response._content = resp.read() # pylint: disable=W0212

        return get_response

    @staticmethod
    def get_empty_posts(*_, **__):
        """
        Mock getting user post from Supermetrics (but posts not found)
        """
        get_response = Response()
        get_response.status_code = 200
        with open('resources/post_response_empty.json', 'rb') as resp:
            get_response._content = resp.read() # pylint: disable=W0212

        return get_response

    @staticmethod
    def get_posts_error(*_, **__):
        """
        Mock getting error when getting user post from Supermetrics
        """
        get_response = Response()
        get_response.status_code = 503

        return get_response

    @staticmethod
    def get_posts_no_body(*_, **__):
        """
        Mock getting response with no body when getting user post from Supermetrics
        """
        get_response = Response()
        get_response.status_code = 200
        get_response._content = b'{' # pylint: disable=W0212

        return get_response

    @staticmethod
    def get_posts_param_missing(*_, **__):
        """
        Mock getting response with missing expected parameters when getting user post
        from Supermetrics
        """
        get_response = Response()
        get_response.status_code = 200
        get_response._content = b'{}' # pylint: disable=W0212

        return get_response

    @staticmethod
    def get_posts_invalid_body(*_, **__):
        """
        Mock getting response with malformed json when getting user post from Supermetrics
        """
        get_response = Response()
        get_response.status_code = 200

        return get_response

    @patch('smstats.manager.requests.post')
    @patch('smstats.manager.requests.get')
    def test_gather(self, mock_get, mock_post):
        """
        Test if we are able to gather and present stats
        """
        # Mock Token registration
        mock_post.side_effect = self.get_valid_token

        # Mock get posts
        mock_get.side_effect = self.get_valid_posts

        config = Config()
        config.max_page = 4
        manager = PostManager(config)
        stats = manager.get_posts_stats()
        with open('resources/stats.json', 'r') as stat_file:
            expected_stats = json.load(stat_file)
        self.assertEqual(stats, expected_stats)

    @patch('smstats.manager.requests.post')
    def test_custom_config(self, mock_post):
        """
        Test if custom parameters are being used to register token
        """
        # Mock Token registration
        mock_post.side_effect = self.get_valid_token

        config = Config()
        config.client_id = 'demo_cl'
        config.name = 'abc'
        config.email = 'abc@gmail.com'
        config.max_page = 4
        PostManager(config)
        expected_body = {'client_id': 'demo_cl',
                         'email': 'abc@gmail.com',
                         'name': 'abc'}
        mock_post.assert_called_with(url=ANY, json=expected_body)

    @patch('smstats.manager.requests.post')
    @patch('smstats.manager.requests.get')
    def test_gather_no_posts(self, mock_get, mock_post):
        """
        Test if we are able to present stats even when no post are found
        """
        # Mock Token registration
        mock_post.side_effect = self.get_valid_token

        # Mock get posts
        mock_get.side_effect = self.get_empty_posts

        config = Config()
        config.max_page = 4
        manager = PostManager(config)
        stats = manager.get_posts_stats()
        with open('resources/stats_no_post.json', 'r') as stat_file:
            expected_stats = json.load(stat_file)
        self.assertEqual(stats, expected_stats)

    @patch('smstats.manager.requests.post')
    def test_token_reg_failed(self, mock_post):
        """
        Test if we throw the right exception when token registration failed
        """
        # Mock Token registration
        mock_post.side_effect = self.get_no_token_response

        with self.assertRaises(DataGetError) as err_cntx:
            PostManager()

        self.assertEqual('Error during stage: Get Token. Unexpected reponse status: 500',
                         str(err_cntx.exception))

    @patch('smstats.manager.requests.post')
    @patch('smstats.manager.requests.get')
    def test_token_expired(self, mock_get, mock_post):
        """
        Test if an expired token is refreshed with getting posts
        """
        # Mock Token registration
        mock_post.side_effect = [self.get_invalid_token(), self.get_valid_token()]

        # Mock get posts
        mock_get.side_effect = self.get_valid_posts

        config = Config()
        config.max_page = 4
        manager = PostManager(config)
        stats = manager.get_posts_stats()
        with open('resources/stats.json', 'r') as stat_file:
            expected_stats = json.load(stat_file)
        self.assertEqual(stats, expected_stats)

    @patch('smstats.manager.requests.post')
    @patch('smstats.manager.requests.get')
    def test_token_invalid(self, mock_get, mock_post):
        """
        Test exception when a token is reported as invalid even after it is refreshed
        """
        # Mock Token registration
        mock_post.side_effect = self.get_invalid_token

        # Mock get posts
        mock_get.side_effect = self.get_valid_posts

        config = Config()
        config.max_page = 4
        manager = PostManager(config)

        with self.assertRaises(DataGetError) as err_cntx:
            manager.get_posts_stats()

        self.assertEqual('Error during stage: Get Posts. Unexpected reponse status: 500',
                         str(err_cntx.exception))

    @patch('smstats.manager.requests.post')
    @patch('smstats.manager.requests.get')
    def test_post_error(self, mock_get, mock_post):
        """
        Test exception when a request to get post received an error response
        """
        # Mock Token registration
        mock_post.side_effect = self.get_valid_token

        # Mock get posts
        mock_get.side_effect = self.get_posts_error

        config = Config()
        config.max_page = 4
        manager = PostManager(config)

        with self.assertRaises(DataGetError) as err_cntx:
            manager.get_posts_stats()

        self.assertEqual('Error during stage: Get Posts. Unexpected reponse status: 503',
                         str(err_cntx.exception))

    @patch('smstats.manager.requests.post')
    @patch('smstats.manager.requests.get')
    def test_post_no_body(self, mock_get, mock_post):
        """
        Test exception when a request to get post received a response with missing body
        """
        # Mock Token registration
        mock_post.side_effect = self.get_valid_token

        # Mock get posts
        mock_get.side_effect = self.get_posts_no_body

        config = Config()
        config.max_page = 4
        manager = PostManager(config)

        with self.assertRaises(DataGetError) as err_cntx:
            manager.get_posts_stats()

        self.assertEqual('Error during stage: Get Posts. Could not read json from response',
                         str(err_cntx.exception))

    @patch('smstats.manager.requests.post')
    @patch('smstats.manager.requests.get')
    def test_post_malformed(self, mock_get, mock_post):
        """
        Test exception when a request to get post received a response with malformed json
        """
        # Mock Token registration
        mock_post.side_effect = self.get_valid_token

        # Mock get posts
        mock_get.side_effect = self.get_posts_invalid_body

        config = Config()
        config.max_page = 4
        manager = PostManager(config)

        with self.assertRaises(DataGetError) as err_cntx:
            manager.get_posts_stats()

        self.assertEqual('Error during stage: Get Posts. Could not read json from response',
                         str(err_cntx.exception))

    @patch('smstats.manager.requests.post')
    @patch('smstats.manager.requests.get')
    def test_post_missing_param(self, mock_get, mock_post):
        """
        Test exception when a request to get post received a
        response with missing expected parameter
        """
        # Mock Token registration
        mock_post.side_effect = self.get_valid_token

        # Mock get posts
        mock_get.side_effect = self.get_posts_param_missing

        config = Config()
        config.max_page = 4
        manager = PostManager(config)

        with self.assertRaises(DataGetError) as err_cntx:
            manager.get_posts_stats()

        self.assertEqual(\
        ('Error during stage: Get Posts.'
        " Parameter ('data', 'posts') not found in received json response"),
        str(err_cntx.exception))

if __name__ == '__main__':
    unittest.main()
