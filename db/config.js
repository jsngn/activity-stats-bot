var config = {
local: {
	database: {
		host     : '', // localhost or any other host (in which case you might want to change name of 'local' object)
		user     : '', // Username of account with necessary privileges on host
		password : '', // Password of account with necessary privileges on host
		schema : '' // Schema which API will provide access for; should be activity_stats_bot if sql script unmodified
	},
	port: 3000 // Port number for API to run on, choose something that nothing else is using
}
};
module.exports = config;
