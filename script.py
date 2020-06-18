import praw
import config

if __name__ == '__main__':
    reddit = praw.Reddit(username=config.username, password=config.password, client_id=config.client_id,
                         client_secret=config.client_secret, user_agent="Activisualizer")
    print("Logged in")
    upvotes = reddit.get(path="/user/username/upvoted?limit=100")  # Replace username with actual username
    subreddits = {}
    for vote in upvotes:
        if str(vote.subreddit) not in subreddits:
            subreddits[str(vote.subreddit)] = 0
        subreddits[str(vote.subreddit)] += 1

    for subreddit in subreddits:
        print(subreddit + " " + str(subreddits[subreddit]))
