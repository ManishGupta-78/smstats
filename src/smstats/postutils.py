"""
Utility methods to parse and summarize posts
"""
from datetime import datetime
from statistics import fmean
from smstats.custom import PostDetails

def get_post_details(post):
    """
    Summarize a subset of user posts
    """
    summary = PostDetails()

    # Param 1: Post Length
    summary.length = len(post['message'])

    # Param 2: Post month
    created_time = datetime.fromisoformat(post['created_time'])
    summary.month = f'{created_time.month}-{created_time.year}'

    # Param 3: Post Week
    summary.week = created_time.date().isocalendar().week

    # Param 4: User
    summary.user = post['from_id']

    return summary

def build_posts_summary(summary, posts):
    """
    Incremently build posts summary
    """

    for post in posts:
        details = get_post_details(post)

        # isummary is interval summary
        # Update monthly and weekly stats
        for isummary in [summary.monthly[details.month],
                         summary.weekly[details.week]]:
            # Total posts
            isummary.users[details.user].total += 1

            # Longest post so far
            longest = isummary.users[details.user].longest
            isummary.users[details.user].longest = max(longest, details.length)

            # Total Length
            isummary.users[details.user].sum_length += details.length

def get_stats(summary):
    """
    Generate reports from collected data
    """
    # Will store result in a dictionary. Will be easily translated to json
    stats = {
        'avg_postlen_per_month': {},
        'longest_post_per_month': {},
        'total_posts_by_week': {},
        'avg_post_per_user_per_month': {}
    }

    # isummary is interval summary
    # psummary is post summary
    for month, isummary in summary.monthly.items():
        # Stat 1: Average Length of Posts per month
        total_length = sum([psummary.sum_length for psummary in isummary.users.values()])
        month_posts = sum([psummary.total for psummary in isummary.users.values()])
        stats['avg_postlen_per_month'][month] = round(total_length/month_posts, 2)

        # Stat 2: Longest post per month
        stats['longest_post_per_month'][month] = \
        max([psummary.longest for psummary in isummary.users.values()])

        stats['avg_post_per_user_per_month'][month] = \
        fmean([psummary.total for psummary in isummary.users.values()])

    # isummary is interval summary
    # psummary is post summary
    for week, isummary in summary.weekly.items():
        # Stat 3: Total posts per week
        stats['total_posts_by_week'][str(week)] = \
        sum([psummary.total for psummary in isummary.users.values()])

    return stats
