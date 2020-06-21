import praw
import prawcore.exceptions
import pyconfig
import requests
from statics import Statics
from extractor import Extractor
import time


def run_bot(reddit):
    for comment in reddit.subreddit("test").comments(limit=1000):
        if Statics.ERROR_KW not in comment.body and Statics.BOT_KW in comment.body:  # Bot summoned
            print(f"Bot summoned for {comment.id}")
            if not has_replied(comment.id):
                comment_str = comment.body.strip()
                comment_arr = comment_str.split()
                if len(comment_arr) != Statics.COMMENT_WORD_NO:
                    comment.reply(Statics.FORMAT_ERROR)
                    add_comment(comment.id)
                else:
                    try:
                        reddit.redditor(comment_arr[1]).id
                        extractor = Extractor(reddit, comment_arr[1])
                        if comment_arr[2] in extractor.activity_action and comment_arr[3] in extractor.mode_action:
                            results = extractor.extract(comment_arr[2], comment_arr[3])  # Dictionary
                            results_sorted = sorted(((value, key) for key, value in results.items()), reverse=True)
                            cmt = f"{comment_arr[2]}'s {comment_arr[3]} of {comment_arr[1]}:\n\n"
                            i = 0
                            for count, item in results_sorted:
                                if i < Statics.STATS_LIMIT and i < len(results_sorted):
                                    cmt += f"{item}: {count}\n\n"
                                    i += 1
                                else:
                                    break
                            # comment.reply(cmt)
                            print(comment.id)
                            add_comment(comment.id)
                            print(cmt)
                        else:
                            comment.reply(Statics.ACTIVITY_ERROR)
                            add_comment(comment.id)
                    except prawcore.exceptions.NotFound:
                        comment.reply(Statics.USERNAME_ERROR)
                        add_comment(comment.id)
            else:
                print(f"Already replied to comment ID {comment.id}")
    time.sleep(10)


def has_replied(id):
    resp = requests.get(f"http://localhost:3000/comments/search/{id}")
    if resp.json()["status"] != 200:
        return True  # We don't know if comment already replied to, so be safe and don't reply to it
    if resp.json()["response"]:
        if resp.json()["response"][0]["COUNT(*)"]:  # If replied already
            return True
        else:
            return False  # We know we haven't replied
    else:
        return True


def add_comment(id):
    resp = requests.post("http://localhost:3000/comments/add/", data={"id": id})
    if resp.json()["status"] != 200:
        print("DB FAILURE: Could not add comment ID to DB; bot may try to reply to this comment again")
        print("DB ERROR: " + resp.json()["error"])
    else:
        print("DB SUCCESS: Added comment ID to DB")


if __name__ == '__main__':
    reddit = praw.Reddit(username=pyconfig.username, password=pyconfig.password, client_id=pyconfig.client_id,
                         client_secret=pyconfig.client_secret, user_agent="Activity stats comment bot by /u/swinii")
    print("PRAW Reddit instance ready.")

    while True:
        run_bot(reddit)
