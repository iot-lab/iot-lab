socket.on('message',handle_broadcast);

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

//if broadcast message received, nodes in orange

function broadcast(node){
    for (var i = 0; i < objects.length; i++) {
        if (objects[i].name == node){
            var col = 0xff8400;
            objects[i].material.color.setHex(col);
        }
} 
     myrender();
}

//if unicast message received, nodes in gray  

function unicast(node){
    for (var i = 0; i < objects.length; i++){
 	if (objects[i].name == node){ 
	   var col  =  0xA9A9A9;
	   objects[i].material.color.setHex(col);
	}
   }  
   myrender();
}


//Broadcast
$('#broadcast').click(function () {
    socket.emit('message', selectedNodes[0]+';b');
    
})

