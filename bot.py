""" Script to run activity stats bot
    Here is where we start connections to Reddit and our own APIs and reply to summons
    Josephine Nguyen, 2020 """

import praw
import prawcore.exceptions
import pyconfig
import requests
from statics import Statics
from extractor import Extractor
import time


def run_bot(reddit, replied_ids):
    """ Gets 1000 comments in subreddit, checks whether bot is summoned, if yes then verify good formatting to display
        stats or error message (as reply to comment with summon)
        Takes params:
        reddit: instance of praw.Reddit
        replied_ids: dictionary of comment IDs recently confirmed that we've replied """

    for comment in reddit.subreddit(pyconfig.subreddit).comments(limit=1000):

        if Statics.ERROR_KW not in comment.body and Statics.BOT_KW in comment.body:  # Bot summoned
            print(f"{comment.id}: Bot summoned")

            if comment.id not in replied_ids:
                print(f"{comment.id}: Querying database for ID")
                reply_status = has_replied(comment.id)

                if not reply_status:  # Don't repeatedly reply to a comment
                    # Some sanitizing, put into array for easier reference later on
                    comment_str = comment.body.strip()
                    comment_arr = comment_str.split()

                    if len(comment_arr) != Statics.COMMENT_WORD_NO:
                        reply_handler(comment, Statics.FORMAT_ERROR, replied_ids)
                    else:
                        try:
                            reddit.redditor(comment_arr[1]).id  # Throws exception if non-existent user, we comment err

                            extractor = Extractor(reddit, comment_arr[1])

                            # Ensure good formatting e.g. one of 'upvotes', 'comments', 'submissions' must be present
                            # or can't do 'upvotes awardcount'
                            if comment_arr[2] in extractor.activity_action \
                                    and comment_arr[3] in Statics.CORRESPOND_MODE[comment_arr[2]]:
                                results = extractor.extract(comment_arr[2], comment_arr[3])  # Dictionary returned

                                # Log and reply to summon (if applicable) then move onto next comment
                                if Statics.EXCEPTION_KW in results:
                                    print(f"{comment.id}: Error extracting stats: {results[Statics.EXCEPTION_KW]}")

                                    if type(results[Statics.EXCEPTION_KW]) is prawcore.exceptions.Forbidden:
                                        reply_handler(comment, Statics.PRIVATE_ERROR, replied_ids)
                                    continue

                                results = results[comment_arr[2] + "_" + comment_arr[3]]

                                # No exceptions thrown from extractor, proceed normally
                                # Sort so we only display highest stats
                                results_sorted = sorted(((value, key) for key, value in results.items()), reverse=True)

                                # Explanation of stats at start of comment & unit in stats dependent on activity & mode
                                cmt = format_comment(comment_arr[1], comment_arr[2], comment_arr[3])
                                unit = get_unit(comment_arr[2], comment_arr[3])

                                # Don't display too many subreddits/comments/submissions
                                i = 0
                                for count, item in results_sorted:
                                    if i < pyconfig.stats_limit and i < len(results_sorted):
                                        cmt += f"{item}: {count} {unit}\n\n"
                                        i += 1
                                    else:
                                        break
                                reply_handler(comment, cmt, replied_ids)
                            else:
                                reply_handler(comment, Statics.FORMAT_ERROR, replied_ids)
                        except prawcore.exceptions.NotFound:
                            reply_handler(comment, Statics.USERNAME_ERROR, replied_ids)
                elif reply_status == 1:
                    replied_ids[comment.id] = None
                    print(f"{comment.id}: Already replied to comment")
                else:
                    print(f"{comment.id}: DB error (see log lines immediately above)")
            else:
                print(f"{comment.id}: Already queried database for comment")
    time.sleep(10)


def has_replied(id):
    """ Send get request to own API to see if comment ID exists (meaning we've replied to it)
        Takes in params:
        id: string of comment ID to query

        Returns status code: 0=not replied, 1=replied, 2=error """

    resp = requests.get(f"http://localhost:3000/comments/search/{id}")
    if resp.json()["status"] != 200:
        print(f"{id}: DB error: " + str(resp.json()["error"]) + ". Bot will skip this comment.")
        return 2
    if resp.json()["response"]:
        if resp.json()["response"][0]["COUNT(*)"]:  # If replied already
            return 1
        else:
            return 0  # We know we haven't replied
    else:
        return 2


def add_comment(id):
    """ Send post request to own API to add a comment ID we've just replied to
            Takes in params:
            id: string of comment ID to insert

            Prints error message if can't insert """

    resp = requests.post("http://localhost:3000/comments/add/", data={"id": id})
    if resp.json()["status"] != 200:  # Something went wrong
        print(f"{id}: DB failure: Could not add comment ID to DB; bot may try to reply to this comment again")
        print(f"{id}: DB error: " + resp.json()["error"])
    else:
        print(f"{id}: DB success: Added comment ID to DB")


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


def reply_handler(comment, reply, replied_ids):
    """ Reply to comment on Reddit, add ID to db and dictionary of queried IDs (so don't need to waste a get request
        when we know we've replied--if we haven't, praw throws exception, we log it as below)

        Takes in params:
        comment = praw's object for a comment, call reply() method from this object
        reply = string making up body of reply
        replied_ids: dict of queried IDs in this run of bot.py """

    try:
        comment.reply(reply)
        add_comment(comment.id)
        replied_ids[comment.id] = None
    except Exception as e:
        print(f"{comment.id}: Error while replying or writing to DB: {e}")


if __name__ == '__main__':
    reddit = praw.Reddit(username=pyconfig.username, password=pyconfig.password, client_id=pyconfig.client_id,
                         client_secret=pyconfig.client_secret, user_agent="Activity stats comment bot by /u/swinii")
    print("PRAW Reddit instance ready.")

    # Dictionary of comment IDs in the 1000 comments retrieved from subreddit that we know we've replied by sending GET
    # to API. This means program won't repeatedly try to send get requests to API to confirm the same information we
    # should already know
    replied_ids = {}

    while True:  # Run until interrupted
        run_bot(reddit, replied_ids)
