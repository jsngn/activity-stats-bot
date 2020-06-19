import praw
import config
import pprint

def get_upvoted_subreddits(reddit):
    upvotes = reddit.get(path="/user/yDezy/upvoted?limit=100")  # Replace username with actual username
    pprint.pprint(vars(upvotes[0]))
    get_award_count_from_list(upvotes)
    # get_subreddit_stats_from_list(upvotes)


def get_commented_subreddits(reddit):
    comments = reddit.get(path="/user/yDezy/comments?limit=100")
    # pprint.pprint(vars(comments[0]))
    get_award_count_from_list(comments)
    # get_subreddit_stats_from_list(comments)


def get_submitted_subreddits(reddit):
    submissions = reddit.get(path="/user/yDezy/submitted?limit=100")
    # pprint.pprint(vars(submissions[0]))
    get_award_count_from_list(submissions)
    # get_subreddit_stats_from_list(submissions)


def get_subreddit_count_from_list(list):
    subreddits = {}
    for item in list:
        if str(item.subreddit) not in subreddits:
            subreddits[str(item.subreddit)] = 0
        subreddits[str(item.subreddit)] += 1

    for subreddit in subreddits:
        print(subreddit + " " + str(subreddits[subreddit]))


def get_award_count_from_list(list):
    counts = {}
    for item in list:
        if str(item.permalink) not in counts:
            counts[str(item.permalink)] = 0
        for award in item.all_awardings:
            counts[str(item.permalink)] += award["count"]

    for count in counts:
        print(count + " " + str(counts[count]))


if __name__ == '__main__':
    reddit = praw.Reddit(username=config.username, password=config.password, client_id=config.client_id,
                         client_secret=config.client_secret, user_agent="Activisualizer")
    print("Logged in")
    get_upvoted_subreddits(reddit)
    print("---")
    get_commented_subreddits(reddit)
    print("---")
    get_submitted_subreddits(reddit)

