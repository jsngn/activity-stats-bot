import praw
import prawcore.exceptions
import config
from statics import Statics
from extractor import Extractor
import time


def run_bot(reddit):
    for comment in reddit.subreddit("test").comments(limit=1000):
        if Statics.BOT_KW in comment.body:  # Bot summoned
            print("Bot summoned")
            comment_str = comment.body.strip()
            comment_arr = comment_str.split()
            if len(comment_arr) != 4:
                comment.reply(Statics.FORMAT_ERROR)
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
                            if i < 5 and i < len(results_sorted):
                                cmt += f"{item}: {count}\n\n"
                                i += 1
                            else:
                                break
                        # for item in results_sorted:
                        #     if i < 5:
                        #         cmt += f"'''{item}: {results[item]}'''"
                        #         i += 1
                        #     else:
                        #         break
                        comment.reply(cmt)
                        print(cmt)
                    else:
                        comment.reply(Statics.ACTIVITY_ERROR)
                except prawcore.exceptions.NotFound:
                    comment.reply(Statics.USERNAME_ERROR)
    time.sleep(10)


if __name__ == '__main__':
    reddit = praw.Reddit(username=config.username, password=config.password, client_id=config.client_id,
                         client_secret=config.client_secret, user_agent="Activity stats comment bot by /u/swinii")
    print("PRAW Reddit instance ready.")

    while True:
        run_bot(reddit)

    # # get_upvoted_subreddits(reddit, username)
    # # print("---")
    # get_commented_subreddits(reddit, username)
    # print("---")
    # get_submitted_subreddits(reddit, username)
