#!/usr/bin/nodejs


// -------------- load packages -------------- //
var express = require('express')
var path = require('path');
var hbs = require('hbs');
var fs = require('fs');

var app = express();


// -------------- express initialization -------------- //
app.set('port', process.env.PORT || 8080 );

// tell express that the view engine is hbs
app.set('view engine', 'hbs');


// -------------- express endpoint definition -------------- //

app.use('/css', express.static(path.join(__dirname, 'css')));
app.use('/js', express.static(path.join(__dirname, 'js')));
app.use('/images', express.static(path.join(__dirname, 'images')));
const {PythonShell} = require('python-shell');

hbs.registerPartials(__dirname + "/partials");

app.get('/', function(req, res){
    console.log("about anon()");
    res.render("about", {
        "session": req.session,
    });
});

app.get('/solver_worker', function(req, res){
    console.log("solver_worker anon()");

    var options = {
        "args": [req.query.puzzle],
    }

    PythonShell.run("./src/wordhunt_online.py", options, function (err, results) {
        if (err) {
            throw err;
        };
        res.send(results);
    });
});

app.get('/helper', function(req, res){
    console.log("helper anon()");
    res.render("helper", {
        "session": req.session,
    });
});

// WILDCARD HANDLERS MUST COME AFTER ALL OTHER EXPLICIT ENDPOINTS
app.get('/:stuff', function(req, res){
    res.render("notfound", {
        "session": req.session,
        "url": req.params.stuff
    });
});

// -------------- listener -------------- //
// The listener is what keeps node 'alive.'

var listener = app.listen(app.get('port'), function() {
  console.log('Express server started on port: '+listener.address().port);
});
