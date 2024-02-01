import praw
import prawcore
import argparse
import datetime
import json
import time

# Create the parser
parser = argparse.ArgumentParser(description="Search Reddit for posts matching given keywords.")

# Add arguments
parser.add_argument('-k', '--keywords', required=True, nargs='+', help='Keywords to search for')
parser.add_argument('-s', '--subreddits',required=True, nargs='+', help='Indicate which subreddit to search in, use \'all\' for site-wide searching')
parser.add_argument('-d', '--depth', required=True, help='Depth of comments to retrieve. Use a number or "max" for full depth. E.g.: 0 indicates only \
    top level comments, 1 indicates one addtional reply to the top comments to include. -1 to skip all comments.')

# Parse the arguments
args = parser.parse_args()
if args.depth.lower() == 'max':
    comment_depth = None  # Indicates no limit on depth
elif args.depth == '-1':
    comment_depth = -1  # Indicates no comments should be included
else:
    comment_depth = int(args.depth)

def fetch_and_process_comments(comment, max_depth=None, depth=0):
    # Base case for recursion
    if max_depth is not None and depth > max_depth:
        return None

    comment_data = {
        'author': str(comment.author),
        'body': comment.body,
        'replies': []
    }

    if hasattr(comment, 'replies'):
        for reply in comment.replies:
            if isinstance(reply, praw.models.MoreComments):
                continue
            processed_reply = fetch_and_process_comments(reply, max_depth, depth + 1)
            if processed_reply:
                comment_data['replies'].append(processed_reply)

    return comment_data

def __main__():

    reddit = praw.Reddit(
        client_id = 'g0QHbtWFPnBkDRau0iBuRw',
        client_secret = 'WIdtHXoFU02IogeeOLn8IXBE5KBEcQ',
        user_agent='product comments',
        username='ChemistryBeautiful28',
        password='Letgo2020'
    )
    
    # Join keywords with OR
    search_query = " OR ".join(args.keywords)
    posts_data = []

    for subreddit_name in args.subreddits:
        for submission in reddit.subreddit(subreddit_name).search(search_query):
            post_data = {
                'Title': submission.title,
                'Author': str(submission.author),
                'Reddit Post URL': f"https://www.reddit.com{submission.permalink}",
                'External URL': submission.url,
                'Score': submission.score,
                'Upvote Ratio': submission.upvote_ratio,
                'Body': submission.selftext,
                'Created': datetime.datetime.fromtimestamp(submission.created_utc).strftime('%Y-%m-%d %H:%M:%S'),
                'Flair': submission.link_flair_text,
                'Comments': []
            }

            if comment_depth != -1:  # If comments are to be included
                try:
                    submission.comments.replace_more(limit=0)  # Limit the additional comments loaded
                    for comment in submission.comments:
                        post_data['Comments'].append(fetch_and_process_comments(comment, comment_depth))
                except prawcore.exceptions.TooManyRequests as e:
                    print(f"Rate limit exceeded, sleeping for 60 seconds.Error:{e}")
                    time.sleep(60)  # Sleep for 60 seconds

            posts_data.append(post_data)

    with open('reddit_search_results.json', 'w', encoding='utf-8') as file:
        json.dump(posts_data, file, ensure_ascii=False, indent=4)

__main__()