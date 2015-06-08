var socket = io();
console.log("connected to websocket");
socket.on('welcome', function(data) {
    console.log('Got welcome from the server');
});
socket.on('nodes',handle_nodes);
socket.on('message',handle_broadcast);
var prout = "";

function handle_nodes(data) {
    data = data.replace("nodes:","");
    $("#messages").prepend("<li><i><strong>nodes:</strong>" + data + "</i></li>");
    data = data.split(',');
}

//broadcast message reçu
var map = [];
var i = 1;

function handle_broadcast(data) {
    $("#messages").prepend("<li><strong>" + data.node + ":</strong>" + data.message + "</li>");

  	if(data.message.match("ping")){

           broadcast(data.node);
	   map.splice(1,0,data.node);
	   console.log(map);
	 }
	else if (data.message.match("pong")) {
	     unicast(map.slice(i-1,i));
	     console.log(map.slice(i-1,i));
	     i++;  
   }
}


var site = $("#site");
$("#resources").on("click", function() {
    if(site.val() != "")
        socket.emit('resources', site.val(), function(data){
            console.log("received response with " + data.items.length + " resources");
            var resources = data.items;
            var nodes = new Array();
            for(var i=0;i<resources.length;i++) {
                console.log(resources[i].network_address);
                node = new Array();
                n_addr = resources[i].network_address;
                node[0] = n_addr.substring(0,n_addr.indexOf("."));
                node[1] = resources[i].x;
                node[2] = resources[i].y;
                node[3] = resources[i].z;
                node[4] = resources[i].archi;
                node[5] = resources[i].state;
                nodes[i] = node;
	    }
            loadNodes(nodes);
            //upgradeNodes([]);
            init_3d();
   	    
        });

});

$('#sonar_M3').hide();
$('#sonar_WSN430_CC2420').hide();
$('#sonar_WSN430_CC1101').hide();

$('#reset').on("click", function () {
    unselect();
    init_color();
    myrender();

});

$('#nodes').on("click", function() {
    socket.emit('nodes');

});

//$('#send').on("submit", function() {
//    preventDefault();
$('#send').on("click", function() {
    console.log("envoi");
    socket.emit('message', $("#command").val());
});


//M3 buttons
//Sonar -17dBm
$('#sonar1').click(function () {
    socket.emit('message', selectedNodes[0]+';a');
    
})

//Sonar -12dBm
$('#sonar2').click(function (){
    socket.emit('message',selectedNodes[0]+';b');

})

//Sonar -7dBm
$('#sonar3').click(function () {
    socket.emit('message', selectedNodes[0]+';c');
    
})

//Sonar -3dBm
$('#sonar4').click(function () {
    socket.emit('message', selectedNodes[0]+';d');
    
})    

//Sonar 0dBm
$('#sonar5').click(function () {
    socket.emit('message', selectedNodes[0]+';e');
    
}) 

//Sonar 3dBm
$('#sonar6').click(function () {
    socket.emit('message', selectedNodes[0]+';f');
    
})    

//Sonar print_help
$('#sonar_help').click(function () {
    socket.emit('message', selectedNodes[0]+';h');
    
})

// WSN430 CC2420 buttons

//Sonar -25dBm
$('#sonar7').click(function () {
    socket.emit('message', selectedNodes[0]+';a');

})

//Sonar -15dBm
$('#sonar8').click(function (){
    socket.emit('message',selectedNodes[0]+';b');

})

//Sonar -10dBm
$('#sonar9').click(function () {
    socket.emit('message', selectedNodes[0]+';c');

})

//Sonar -5dBm
$('#sonar10').click(function () {
    socket.emit('message', selectedNodes[0]+';d');

})

//Sonar 0dBm
$('#sonar11').click(function () {
    socket.emit('message', selectedNodes[0]+';e');

})

// WSN430 CC1101 buttons


//Sonar -30dBm
$('#sonar12').click(function () {
    socket.emit('message', selectedNodes[0]+';a');

})

//Sonar -20dBm
$('#sonar13').click(function (){
    socket.emit('message',selectedNodes[0]+';b');

})

//Sonar -15dBm
$('#sonar14').click(function () {
    socket.emit('message', selectedNodes[0]+';c');

})

//Sonar -10dBm
$('#sonar15').click(function () {
    socket.emit('message', selectedNodes[0]+';d');

})

//Sonar -6dBm
$('#sonar16').click(function () {
    socket.emit('message', selectedNodes[0]+';e');

})

//Sonar 0dBm
$('#sonar17').click(function () {
    socket.emit('message', selectedNodes[0]+';f');

})


//Sonar -6dBm
$('#sonar18').click(function () {
    socket.emit('message', selectedNodes[0]+';g');

})

//Sonar 10dBm
$('#sonar19').click(function () {
    socket.emit('message', selectedNodes[0]+';h');

})





