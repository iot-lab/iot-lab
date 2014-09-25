function create_robot(id) {
	var e = document.createElement("span");
	e.id = id;
	e.style = "position: absolute";
	e.innerHTML = '<svg height="32" width="32" transform="scale(0.2)">'
	+ '<circle cx="80" cy="80" r="78" '
	+ 'style="stroke:black;stroke-width:2;fill:#AAA;"/>'
	+ '<polygon points="80,3 55,103 80,83 105,103"'
	+ 'style="fill:lime;stroke:purple;stroke-width:1"/>'
	+ '</svg>';
	document.body.appendChild(e);
	return e;
}

function set_orientation(id, rotation) {
	var e = document.getElementById(id).firstChild.children[1];
	e.setAttribute("transform", "rotate(" + rotation + ", 80, 80)");
}

function set_position(id, x, y) {
	var e = document.getElementById(id);
	e.style.top = y;
	e.style.left = x;
}

function robots_init() {
	var id = "m3-381";
	create_robot(id);
	set_orientation(id, 20);
	set_position(id, 1200, 100);
}
