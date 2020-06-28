""" Josephine Nguyen, 2020 """


class Statics:
    """ Class with constant values across project """

    # Summon bot with this
    BOT_KW = "!activitystatsbot "

    # Activity type
    UPVOTES_KW = "upvotes"
    COMMENTS_KW = "comments"
    SUBMISSIONS_KW = "submissions"

    # Mode of stats to view
    SUBREDDIT_KW = "subreddit"
    AWARD_COUNT_KW = "awardcount"
    AWARD_FREQ_KW = "awardfreq"

    # Detect error message (one error message has BOT_KW so need this to not reply to error messages)
    ERROR_KW = "Whoops"

    # Ensure bad user request e.g. "upvotes award_count" not allowed
    CORRESPOND_MODE = {UPVOTES_KW: {SUBREDDIT_KW: None},
                       COMMENTS_KW: {SUBREDDIT_KW: None, AWARD_COUNT_KW: None, AWARD_FREQ_KW: None},
                       SUBMISSIONS_KW: {SUBREDDIT_KW: None, AWARD_COUNT_KW: None, AWARD_FREQ_KW: None}}

    # Error message if formatting of summon is wrong (BOT_KW still must be correct)
    FORMAT_ERROR = "Whoops - that's the incorrect comment format! Please do: '!activitystatsbot username [('upvotes' " \
                   "'subreddit') | (('comments'|'submissions') ('awardcount'|'awardfreq'|'subreddit'))]' "
    # User doesn't exist
    USERNAME_ERROR = "Whoops - this user doesn't appear to exist!"
    # Message for forbidden exception from praw
    PRIVATE_ERROR = "Whoops - this user didn't make the required details publicly available. Likely their upvotes " \
                    "are not public. If you're querying yourself, please visit Old Reddit to make your upvotes info " \
                    "public first!"

    COMMENT_WORD_NO = 4  # Num of words in a good summon (still need more verification)
    EXCEPTION_KW = "error"  # For passing around exception details internally
