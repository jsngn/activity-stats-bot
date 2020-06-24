from statics import Statics
import pprint


class Extractor:
    def __init__(self, reddit, username):
        self.reddit = reddit
        self.username = username
        self.activity_action = {Statics.UPVOTES_KW: self.get_upvotes_stats,
                                Statics.COMMENTS_KW: self.get_comments_stats,
                                Statics.SUBMISSIONS_KW: self.get_submissions_stats}
        self.mode_action = {Statics.AWARD_COUNT_KW: self.get_award_count_from_list,
                            Statics.AWARD_FREQ_KW: self.get_award_freqs_from_list,
                            Statics.SUBREDDIT_KW: self.get_subreddit_count_from_list}

    def extract(self, activity, mode):
        listing = self.activity_action[activity]()
        return self.mode_action[mode](listing)

    def get_upvotes_stats(self):
        return self.reddit.get(path=f"/user/{self.username}/upvoted?limit=100")
        # pprint.pprint(vars(upvotes[0]))

    def get_comments_stats(self):
        return self.reddit.get(path=f"/user/{self.username}/comments?limit=100")
        # pprint.pprint(vars(comments[0]))

    def get_submissions_stats(self):
        return self.reddit.get(path=f"/user/{self.username}/submitted?limit=100")
        # pprint.pprint(vars(submissions[0]))

    def get_subreddit_count_from_list(self, listing):
        subreddits = {}
        for item in listing:
            if str(item.subreddit) not in subreddits:
                subreddits[str(item.subreddit)] = 0
            subreddits[str(item.subreddit)] += 1

        # for subreddit in subreddits:
        #     print(subreddit + " " + str(subreddits[subreddit]))
        return subreddits

    def get_award_count_from_list(self, listing):
        counts = {}
        for item in listing:
            pprint.pprint(vars(item))
            url = "https://reddit.com" + str(item.permalink)
            if url not in counts:
                counts[url] = 0
            for award in item.all_awardings:
                counts[url] += award["count"]

        # for count in counts:
        #     print(count + " " + str(counts[count]))
        return counts

    def get_award_freqs_from_list(self, listing):
        awards = {}
        for item in listing:
            for award in item.all_awardings:
                if str(award["name"]) not in awards:
                    awards[str(award["name"])] = 0
                awards[str(award["name"])] += award["count"]

        # for award in awards:
        #     print(award + " " + str(awards[award]))
        return awards
