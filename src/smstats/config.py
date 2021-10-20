"""
Supermetrics REST service details
"""
from dataclasses import dataclass
from smstats.custom import ExpectedResponse

# Default configuration to register token
TOKEN_URL = 'https://api.supermetrics.com/assignment/register'
TOKEN_REG_REQUEST = {
    'client_id': 'ju16a6m81mhid5ue1z3v2g0uh',
    'email': 'manish@gmail.com',
    'name': 'manish'
}
TOKEN_KEY = ('data', 'sl_token')

# Default configuration to get posts
POSTS_URL = 'https://api.supermetrics.com/assignment/posts'
MAX_POST_PAGE = 10
INVALID_TOKEN_RESPONSE = ExpectedResponse(status=500,
                                          key=('error', 'message'),
                                          value='Invalid SL Token')
POSTS_KEY = ('data', 'posts')

# User editable configuration
@dataclass
class Config:
    """user editable configuration"""
    client_id: str = TOKEN_REG_REQUEST['client_id']
    email: str = TOKEN_REG_REQUEST['email']
    name: str = TOKEN_REG_REQUEST['name']
    max_page: int = MAX_POST_PAGE
