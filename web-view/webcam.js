function webcam_init() {
	create_video_button();
}

function create_video_button() {
	var but = create_button("1180px", "10px", "V: OFF", function() {
		this.value.match("OFF") ? show_webcam() : hide_webcam();
		this.value = "V: " + (this.value.match("OFF") ? "ON" : "OFF");
	});
	but.style.width = "";
	document.body.appendChild(but);
}

function show_webcam() {
	build_webcam_widget();
	build_webcam_video();
	build_webcam_buttons();
}

function hide_webcam() {
	document.body.removeChild(document.webcam_widget);
}

function build_webcam_widget() {
	var div = document.createElement("div");
	div.style.top = "150px";
	div.style.left = "700px";
	div.style.position = "absolute";
	document.body.appendChild(div);
	document.webcam_widget = div;
}

function build_webcam_video() {
	var vid = document.createElement("img");
	vid.src = "http://webcam-grenoble.iot-lab.info/mjpg/video.mjpg"
	vid.style.width = "400px";
	vid.style.position = "absolute";
	document.webcam_widget.appendChild(vid);
}

function build_webcam_buttons() {
	create_webcam_button("500px", "0px", "+", zoom_in);
	create_webcam_button("500px", "30px", "-", zoom_out);
	create_webcam_button("500px", "60px", "J", corridor_J);
	create_webcam_button("500px", "90px", "F", corridor_F);
	create_webcam_button("500px", "120px", "K", corridor_K);
}

function create_webcam_button(x, y, text, onclick) {
	var but = create_button(x, y, text, onclick);
	document.webcam_widget.appendChild(but);
}

function create_button(x, y, text, onclick) {
	var but = document.createElement("input");
	but.type = "button";
	but.value = text;
	but.onclick = onclick;
	but.style.position = "absolute";
	but.style.top = y;
	but.style.left = x;
	but.style.width = "30px";
	return but;
}

function zoom_in() {
	webcam_call("rzoom=+2500");
}

function zoom_out() {
	webcam_call("rzoom=-2500");
}

function corridor_J() {
	webcam_call("tiltbar=194,vertical&barcoord=?15,5", function() {
	webcam_call("panbar=194,horisontal&barcoord=?45,0", function() {
	webcam_call("zoombar=178,horisontal&barcoord=40,0") })});
}

function corridor_F() {
	webcam_call("tiltbar=194,vertical&barcoord=?13,5", function() {
	webcam_call("panbar=194,horisontal&barcoord=?95,0", function() {
	webcam_call("zoombar=178,horisontal&barcoord=30,0") })});
}

function corridor_K() {
	webcam_call("tiltbar=194,vertical&barcoord=?15,5", function() {
	webcam_call("panbar=194,horisontal&barcoord=?145,0", function() {
	webcam_call("zoombar=178,horisontal&barcoord=50,0") })});
}

function webcam_call(cmd_str, callback) {
	/* call a webcam primitive via a temporary img tag,
	 * remove img when the img eventually fails to load
	 * (expected, since primitive does not return a valid image).
	 */
	var img = document.createElement("img");
        img.onerror = function () {
		document.body.removeChild(this);
		if (callback) callback();
	}
	img.src = "http://webcam-grenoble.iot-lab.info/axis-cgi/com/ptz.cgi?" +
			"camera=1&" + cmd_str;
	img.style.display = "none";
	document.body.appendChild(img);
}
