[![Supported Versions](https://img.shields.io/pypi/pyversions/smstats.svg)](https://pypi.org/project/smstats)

# SmStats: Get Searchmetric User Posts Statistics (Assignment)

**SmStats** is a simple library to get statistics about user posts.
 
## Installing SmStats and Supported Versions
SmStats is available on PyPI:
```console

$ python -m pip install smstats

```
Smstats officially supports Python 3+.  

## Usage
SmStats get posts of users from Supermetrics and return statistics.

```console
from smstats import PostManager, Config, DataGetError

# Optional configuration
config = Config()
config.client_id = 'demo_cl'
config.name = 'abc'
config.email = 'abc@gmail.com'
config.max_page = 4

try:
    manager = PostManager(config)
    stats = manager.get_posts_stats()
    print(stats)
except DataGetError as ex:
    print(ex)
```
```console
{
  'avg_postlen_per_month': {
     '10-2021': 378.51,
     '9-2021': 391.81,
   },
   'longest_post_per_month': {
     '10-2021': 734,
     '9-2021': 732
   }, 
   'total_posts_by_week': {
     '42': 1,
     '41': 39,
     '40': 38,
     '39': 38
   },
   'avg_post_per_user_per_month': {
     '10-2021': 4.7,
     '9-2021': 8.05
   }
}
```
## Defaults

Parameter | Value
--------- | -------------------------
client_id | ju16a6m81mhid5ue1z3v2g0uh
email     | manish@gmail.com
name      | manish

## Development

This package can be easily extended in few simple steps
1. New post descriptor can be added to **PostDetails** dataclass in custom.py
2. Code to get this new post descriptor can be added to **get_post_details** function in postdetails.py
3. Cumulative summary creation can be controlled through **build_posts_summary** function in postdetails.py
4. New statistics could be extracted from the summary by extending **get_stats** function in postdetails.py

### Running unit tests
```console
python test.py
```
### Other considerations
This project seeks to keep a perfect pylint score. It is advised to run pylint before every commit. If an exception is needed, specific pylint warnings must be explicitly disabled.
