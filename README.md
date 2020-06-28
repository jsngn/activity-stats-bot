# activisualizer
Activity visualizer for Reddit

## Comment format
`!activitystatsbot username [("upvotes" "subreddit") | (("comments"|"submissions") ("awardcount"|"awardfreq"|"subreddit"))]`

### Database connection
If you get a 'Too many connections' error for the MySQL connection (visible in log), try restarting the API and possibly the database.