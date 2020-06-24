from statics import Statics
import pprint


class Extractor:
    """ Class to perform get requests to Reddit API then parse out useful info """
    def __init__(self, reddit, username):
        """ Constructor takes in params:
            reddit: non-null instance of praw.Reddit
            username: string which is username whose stats are of interest """

        self.reddit = reddit
        self.username = username

        # Which get function (and hence get request) to use depending on the activity whose stats we want to view
        self.activity_action = {Statics.UPVOTES_KW: self.get_upvotes_stats,
                                Statics.COMMENTS_KW: self.get_comments_stats,
                                Statics.SUBMISSIONS_KW: self.get_submissions_stats}

        # Which function used to extract info from response of get request depending on mode of stats
        self.mode_action = {Statics.AWARD_COUNT_KW: self.get_award_count_from_list,
                            Statics.AWARD_FREQ_KW: self.get_award_freqs_from_list,
                            Statics.SUBREDDIT_KW: self.get_subreddit_count_from_list}

    def extract(self, activity, mode):
        """ All summons, regardless of specified activity and mode call this function
            Takes params:
            activity: string indicating activity type
            mode: string indicating mode of stats """

        listing = self.activity_action[activity]()
        # print(type(listing))
        return self.mode_action[mode](listing)  # Extracted info

    def get_upvotes_stats(self):
        """ Make get request to server to query posts upvoted by username, return result (type praw's Listing) """

        return self.reddit.get(path=f"/user/{self.username}/upvoted?limit=100")  # Max limit = 100 for all gets in class
        # pprint.pprint(vars(upvotes[0]))

    def get_comments_stats(self):
        """ Make get request to server to query comments made by username, return result (type praw's Listing) """

        return self.reddit.get(path=f"/user/{self.username}/comments?limit=100")
        # pprint.pprint(vars(comments[0]))

    def get_submissions_stats(self):
        """ Make get request to server & query submissions made by username, return result (type praw's Listing) """

        return self.reddit.get(path=f"/user/{self.username}/submitted?limit=100")
        # pprint.pprint(vars(submissions[0]))

    def get_subreddit_count_from_list(self, listing):
        """ Return the frequency that unique subreddits show up in the listing returned by any get request above
            Takes in params:
            listing: praw's Listing object

            Return type is dict{subreddit: frequency} """

        subreddits = {}
        for item in listing:
            if str(item.subreddit) not in subreddits:
                subreddits[str(item.subreddit)] = 0
            subreddits[str(item.subreddit)] += 1

        # for subreddit in subreddits:
        #     print(subreddit + " " + str(subreddits[subreddit]))
        return subreddits

    def get_award_count_from_list(self, listing):
        """ Return the number of awards the user earned for each item in the listing returned by any get request above
            (but will only be called for submissions & comments)
            Takes in params:
            listing: praw's Listing object

            Return type is dict{submission/comment url: award count} """

        counts = {}
        for item in listing:
            # pprint.pprint(vars(item))
            url = "https://reddit.com" + str(item.permalink)  # Make clickable in comment
            if url not in counts:
                counts[url] = 0
            for award in item.all_awardings:
                counts[url] += award["count"]

        # for count in counts:
        #     print(count + " " + str(counts[count]))
        return counts

    def get_award_freqs_from_list(self, listing):
        """ Return the frequency of awards earned by user in the listing returned by any get request above
            (but will only be called for submissions & comments)
            Takes in params:
            listing: praw's Listing object

            Return type is dict{award name: award count} """

        awards = {}
        for item in listing:
            for award in item.all_awardings:
                if str(award["name"]) not in awards:
                    awards[str(award["name"])] = 0
                awards[str(award["name"])] += award["count"]

        # for award in awards:
        #     print(award + " " + str(awards[award]))
        return awards
