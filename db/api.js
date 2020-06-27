// API for bot.py to communicate with db of comment IDs which bot has replied to
// Request handling by Josephine Nguyen, 2020

var express=require('express');
let mysql = require('mysql');
const bodyParser = require('body-parser');
var app=express();

var env = process.argv[2] || 'local'; // Use localhost if enviroment not specified
var config = require('./config')[env]; // Read credentials from config.js


//Database connection
app.use(function(req, res, next){
	global.connection = mysql.createConnection({
		host     : config.database.host, 
		user     : config.database.user, 
		password : config.database.password, 
		database : config.database.schema 
	});
	connection.connect();
	next();
});

app.use(bodyParser.urlencoded({extended:true}));
app.use(bodyParser.json());

var router = express.Router();

router.use(function (req,res,next) {
	console.log("/" + req.method); // Log request verb
	next();
});

// Get count of rows in db for a comment ID, for checking whether bot has replied to comment
router.get("/comments/search/:id", function(req, res){
	global.connection.query('SELECT COUNT(*) FROM comments WHERE CommentID = ?', [req.params.id], function(error, results, fields){
		if (error) {
			res.send(JSON.stringify({"status": 500, "error": error, "response": null}));
			return;
		}
		res.send(JSON.stringify({"status": 200, "error": null, "response": results}));
	});
});

// Add comment ID to db, id must be in body of request
router.post("/comments/add/", function(req, res){
	global.connection.query('INSERT INTO comments(CommentID) VALUES(?)', [req.body.id], function(error, results, fields){
		if (error) {
			res.send(JSON.stringify({"status": 500, "error": error, "response": null}));
			return;
		}
		res.send(JSON.stringify({"status": 200, "error": null, "response": results}));
	});
});

app.use(express.static(__dirname + '/'));
app.use("/",router);
app.set( 'port', ( process.env.PORT || config.port || 3000 ));

app.listen(app.get( 'port' ), function() {
	console.log( 'Node server is running on port ' + app.get( 'port' ));
	console.log( 'Environment is ' + env);
});

