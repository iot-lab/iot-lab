socket.on('message',handle_sonar);

function handle_sonar(data) {
    $("#messages").prepend("<li><strong>" + data.node + ":</strong>" + data.message + "</li>");
    if(data.message.split(";").length == 3)
        sonar(data.node);
}


$('#sonar_M3').hide();
$('#sonar_WSN430_CC2420').hide();
$('#sonar_WSN430_CC1101').hide();

$("#site").on("change", function() {
    if( site.val() == "euratech" || site.val()=="rennes")
    $("#sonar_WSN430_CC2420").hide();
    else 
      $("#sonar_WSN430_CC1101").hide();    
});


function sonar(node){
    for (var i = 0; i < objects.length; i++) {
        if (objects[i].name == node){
            var col = 0xff8400;
            objects[i].material.color.setHex(col);
        }
} 
     myrender();
}

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
