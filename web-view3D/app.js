var express = require('express');
var app = express();
var http = require('http').Server(app);
var https = require('https');
var io = require('socket.io')(http);
var net = require('net');

var aggregator = null;

function aggregator_client(socket) {
    aggregator = net.connect({port: 9000},function() {
      console.log('Connected to aggregator [localhost:9000]');
    });
    aggregator.on('data', function(data) {
        data = data.toString();
        console.log("Received data from aggregator: " + data);
        //iterates over messages separated by '\n'
        var messages = data.split("\n");
        for(message in messages) {
            var val = messages[message];
            if(val != "") {
                var index = val.indexOf(";")
                if(index >= 0) {
                    var index2 = val.indexOf(";",index+1);
                    socket.emit('message', { timestamp: val.slice(0, index), node: val.slice(index+1, index2), message: val.slice(index2+1,val.length) });
                }
            }
        }
    });
}

function getResources(site, callback) {
    var options = {
        host : 'www.iot-lab.info',
        auth : '<login>:<password>',
        port : 443,
        path : '/rest/experiments?resources&site=' + site,
        method : 'GET'
    };
    var data = "";
    console.log("Requesting resources for " + site + "...");
    var req = https.request(options, function(res){
        res.on('data', function(chunk) {
            data += chunk;
        });
        res.on('end', function() {
            var result = JSON.parse(data);
            console.log(result.items.length + " nodes");
            callback(result);
        });
    });
    req.end();
    req.on('error', function(e) {
      console.error("Error requesting resources:" + e);
    });
}

function send(data){
    aggregator.write(data + "\n");
}

// ======

app.use(express.static(__dirname+'/static'));
app.get('/', function(req, res) {
    res.sendFile(__dirname + '/index.html');
});
http.listen(3000, function(){
    console.log('listening on *:3000');
});

io.on('connection', function(socket) {
    console.log('Client connected.');
    socket.emit('welcome', {message: 'salut les amis'});
    socket.on('resources', getResources);
    socket.on('message',send);
    
    aggregator_client(socket);
});


