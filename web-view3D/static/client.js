var socket = io();
console.log("connected to websocket");
socket.on('welcome', function(data) {
    console.log('Got welcome from the server');
});
socket.on('nodes',handle_nodes);

var prout = "";

function handle_nodes(data) {
    data = data.replace("nodes:","");
    $("#messages").prepend("<li><i><strong>nodes:</strong>" + data + "</i></li>");
    data = data.split(',');
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
$('#reset').on("click", function () {
    unselect();
    init_color();
    myrender();

});

$('#nodes').on("click", function() {
    socket.emit('nodes');
});

$('#send').on("click", function() {
    console.log("envoi");
    socket.emit('message', $("#command").val());
});







