var socket = io();
console.log("connected to websocket");
socket.on('welcome', function(data) {
    console.log('Got welcome from the server');
});
socket.on('message', handle_message);

function handle_message(data) {
    $("#messages").prepend("<li><strong>" + data.node + ":</strong>" + data.message + "</li>");
    // si message de type addr;addr;rssi, c'est que le noeud a recu le ping
    if(data.message.split(";").length == 3)
        sonar(data.node);
}

// init power panels visibility
function init_panel_powers() {
    $('#power_none').show();
    $('#power_1101').hide();
    $('#power_2420').hide();
    $('#power_m3').hide();
}

// deals with node seletion in 3D view
function handle_selected(obj) {
    var archi = obj.object.archi;
    init_panel_powers();

    var radio = '';
    if (archi.indexOf("m3") >= 0) radio='m3';
    else if (archi.indexOf("1101") >= 0) radio='1101';
    else if (archi.indexOf("2420") >= 0) radio='2420';
    if(radio != ''){
        $('#power_none').hide();
        $('#power_'+radio).show();
    }
}

init_panel_powers();

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
    $('#power_none').show();
    $('#power_1101').hide();
    $('#power_2420').hide();
    $('#power_m3').hide();
});


$('#send').on("click", function() {
    console.log("envoi");
    socket.emit('message', $("#command").val());
});

// power button click sends corresponding character by serial
$('.serial_a').click(function () {
    socket.emit('message', selectedNodes[0]+';a');
})
$('.serial_b').click(function () {
    socket.emit('message', selectedNodes[0]+';b');
})
$('.serial_c').click(function () {
    socket.emit('message', selectedNodes[0]+';c');
})
$('.serial_d').click(function () {
    socket.emit('message', selectedNodes[0]+';d');
})    
$('.serial_e').click(function () {
    socket.emit('message', selectedNodes[0]+';e');
}) 
$('.serial_f').click(function () {
    socket.emit('message', selectedNodes[0]+';f');
})    
$('.serial_g').click(function () {
    socket.emit('message', selectedNodes[0]+';g');
})
$('.serial_h').click(function () {
    socket.emit('message', selectedNodes[0]+';h');
})
