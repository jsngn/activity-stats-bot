import praw
import prawcore.exceptions
import pyconfig
import requests
from statics import Statics
from extractor import Extractor
import time


def run_bot(reddit):
    """ Gets 1000 comments in subreddit, checks whether bot is summoned, if yes then verify good formatting to display
        stats or error message (as reply to comment with summon)
        Takes params:
        reddit: instance of praw.Reddit """

    for comment in reddit.subreddit("PPeachTesting").comments(limit=1000):
        if Statics.ERROR_KW not in comment.body and Statics.BOT_KW in comment.body:  # Bot summoned
            print(f"Bot summoned for {comment.id}")
            if not has_replied(comment.id):  # Don't repeatedly reply to a comment
                # Some sanitizing, put into array for easier reference later on
                comment_str = comment.body.strip()
                comment_arr = comment_str.split()

                if len(comment_arr) != Statics.COMMENT_WORD_NO:
                    comment.reply(Statics.FORMAT_ERROR)
                    add_comment(comment.id)
                else:
                    try:
                        reddit.redditor(comment_arr[1]).id  # Throws exception if non-existent user, we comment with err

                        extractor = Extractor(reddit, comment_arr[1])
                        print(comment_arr[2])
                        print(comment_arr[3])
                        # Ensure good formatting e.g. one of 'upvotes', 'comments', 'submissions' must be present
                        # or can't do 'upvotes awardcount'
                        if comment_arr[2] in extractor.activity_action \
                                and comment_arr[3] in Statics.CORRESPOND_MODE[comment_arr[2]]:
                            results = extractor.extract(comment_arr[2], comment_arr[3])  # Dictionary returned

                            # Sort so we only display highest stats
                            results_sorted = sorted(((value, key) for key, value in results.items()), reverse=True)

                            # Explanation of stats at start of comment & unit in stats dependent on activity & mode
                            cmt = format_comment(comment_arr[1], comment_arr[2], comment_arr[3])
                            unit = get_unit(comment_arr[2], comment_arr[3])

                            # Don't display too many subreddits/comments/submissions
                            i = 0
                            for count, item in results_sorted:
                                if i < Statics.STATS_LIMIT and i < len(results_sorted):
                                    cmt += f"{item}: {count} {unit}\n\n"
                                    i += 1
                                else:
                                    break
                            comment.reply(cmt)
                            print(comment.id)
                            add_comment(comment.id)
                            print(cmt)
                        else:
                            comment.reply(Statics.FORMAT_ERROR)
                            add_comment(comment.id)
                    except prawcore.exceptions.NotFound:
                        comment.reply(Statics.USERNAME_ERROR)
                        add_comment(comment.id)
            else:
                print(f"Already replied to comment ID {comment.id}")
    time.sleep(10)


def has_replied(id):
    """ Send get request to own API to see if comment ID exists (meaning we've replied to it)
        Takes in params:
        id: string of comment ID to query

        Returns boolean, whether we've replied to it """

    resp = requests.get(f"http://localhost:3000/comments/search/{id}")
    if resp.json()["status"] != 200:
        return True  # We don't know if comment already replied to, so be safe and don't reply to it
    if resp.json()["response"]:
        if resp.json()["response"][0]["COUNT(*)"]:  # If replied already
            return True
        else:
            return False  # We know we haven't replied
    else:
        return True  # We don't know if we've replied


def add_comment(id):
    """ Send post request to own API to add a comment ID we've just replied to
            Takes in params:
            id: string of comment ID to insert

            Prints error message if can't insert """

    resp = requests.post("http://localhost:3000/comments/add/", data={"id": id})
    if resp.json()["status"] != 200:  # Something went wrong
        print("DB FAILURE: Could not add comment ID to DB; bot may try to reply to this comment again")
        print("DB ERROR: " + resp.json()["error"])
    else:
        print("DB SUCCESS: Added comment ID to DB")


def format_comment(user, activity, mode):
    """ Returns explanation to put at start of comment depending on activity and mode chosen
        Takes in params:
        user: string of username to use in explanation
        activity: specified activity
        mode: specified mode

        Returns string """

    if mode == Statics.SUBREDDIT_KW:
        return f"{user}'s {activity} most commonly appear in these subreddits:\n\n"
    elif mode == Statics.AWARD_COUNT_KW:
        return f"{user} received most awards on these {activity}:\n\n"
    elif mode == Statics.AWARD_FREQ_KW:
        return f"{user} received these awards most commonly on their {activity}:\n\n"
    else:  # Shouldn't reach this case as we should've caught formatting errors in run_bot, but just in case
        return Statics.FORMAT_ERROR + " Results below may not be meaningful.\n\n"


def get_unit(activity, mode):
    """ Returns unit for stats in results in comment reply
        Takes in params:
        activity: specified activity
        mode: specified mode

        Returns string """

    if mode == Statics.AWARD_COUNT_KW or mode == Statics.AWARD_FREQ_KW:
        return "awards"
    elif mode == Statics.SUBREDDIT_KW:
        if activity == Statics.UPVOTES_KW:
            return "upvotes"
        elif activity == Statics.COMMENTS_KW:
            return "comments"
        elif activity == Statics.SUBMISSIONS_KW:
            return "submissions"

    # Shouldn't reach this case because formatting errors should've been caught in calling function, but just for safety
    return ""


if __name__ == '__main__':
    reddit = praw.Reddit(username=pyconfig.username, password=pyconfig.password, client_id=pyconfig.client_id,
                         client_secret=pyconfig.client_secret, user_agent="Activity stats comment bot by /u/swinii")
    print("PRAW Reddit instance ready.")

    while True:  # Run until interrupted
        run_bot(reddit)
