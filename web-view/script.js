
function init() {
	createSensors();
	createButtons();
	initRegionSelector();
	initUpdateState();
	robots_init();
	webcam_init();
}

function createSensors() {
	sensors.gui = {};
	for (var i in sensors.xy) {
		var d = createSensorGui(i);
		d.setSelected = function (selected) {
			this.selected = selected;
			this.style.backgroundColor = selected ? "red" : "";
		}
		d.className = "_ sensor selectable";
		setSensorClickHandler(d);
		setSensorHoverHandler(d);
		document.body.appendChild(d);
		sensors.gui[i] = d;
	}
}

function createSensorGui(i) {
	var d = document.createElement("div");
	var s = sensors.get(i);
	d.style.left = s.x + "px";
	d.style.top =  s.y + "px";
	d.name = s.name;
	return d;
}

function setSensorClickHandler(s) {
	s.onclick = function(ev) {
		if (this.className.match(/dead|reserved/))
			return;
		this.setSelected(!this.selected);
		animateBoldBorder(this);
	};
}

function setSensorHoverHandler(s) {
	s.onmouseover = function() {
		var x = parseInt(this.style.left);
		var y = parseInt(this.style.top);
		x += (x < 1190 ? 25 : -70);
		y += (y < 500  ? 20 : -30);
		this.tooltip = createTooltip(x, y, getTooltipText(this));
		document.body.appendChild(this.tooltip);
	};
	s.onmouseout = function() { this.tooltip.remove() };
}

function getTooltipText(elt) {
	var text  = elt.name + (elt.text ? "<br/>" + elt.text : "");
	var state = elt.className.match(/dead|reserved|failed/);
	if (state)
		text += "<br>" + state[0];
	if (elt.owned)
		text += "<br>exp: " + elt.owned;
	return text;
}

function createTooltip(x, y, text) {
	var d = document.createElement("div");
	d.className = "tooltip";
	d.innerHTML = text;
	d.style.left = x + "px";
	d.style.top = y + "px";
	d.timer = setTimeout(function() { d.remove() }, 2000);
	d.remove = function() {
		clearTimeout(this.timer);
		this.parentNode.removeChild(this);
		this.remove = function() {};
	};
	return d;
}

function animateBoldBorder(elt, timeout) {
	var s = elt.style;
	s.borderWidth = "2px";
	s.borderColor = "black";
	s.marginTop = s.marginLeft = "-1px";
	setTimeout(function() {
		s.borderWidth = "";
		s.borderColor = "";
		s.marginTop = s.marginLeft = "";
	}, timeout || 2000);
}

function createButtons() {
	document.toolbox = document.createElement("div");
	document.toolbox.className = "toolbox";
	document.toolbox.onmouseover = function(ev) {
		document.dragOn = false;
	}
	document.toolbox.onmouseout = function(ev) {
		document.dragOn = true;
	}
	document.body.appendChild(document.toolbox);
	var actions = {
		start: 300, stop: 350, reset: 400, update: 450, grab: 510,
		load: 60, save: 100, clear: 140, owned: 187, target: 610 };
	for (var key in actions)
		createActionButton(actions[key], 10, key);
}

var action_buttons = {
	start: startSensors,
	stop: stopSensors,
	reset: resetSensors,
	update: updateSensors,
	grab: grabSensors,
	load: loadSensorsSet,
	save: saveSensorsSet,
	clear: clearSelectedSensors,
	owned: selectOwnedSensors,
	target: selectTargetSite,
};

function createActionButton(x, y, actionName) {
	var b = createButton(x, y, actionName);
	b.action = action_buttons[actionName];
	b.onclick = b.action;
	document.toolbox.appendChild(b);
}

function createButton(x, y, text) {
	var b = document.createElement("div");
	b.setAttribute("class", "button");
	b.style.left = x + "px";
	b.style.top = y + "px";
	b.innerHTML = text;
	return b;
}

function initUpdateState() {
	updateOwnedState();
	updateSystemState();
	updateUserState();
	setInterval(updateSystemState, 60000);
	setInterval(updateUserState, 100);
}

function updateOwnedState() {
	callServer("get_owned_nodes?site=" + sensors.site
			+ "&archi=" + sensors.archi,
	function(state) {
		for (var i in state) {
			sensors.gui[i].owned = state[i];
			state[i] = "owned";
		}
		setSensorsState(state);
	});
}

function updateSystemState() {
	callServer("get_system_state?site=" + sensors.site
			+ "&archi=" + sensors.archi,
	function(sys) {
		var state = {};
		parseNodesList(sys.Busy, "reserved", state);
		parseNodesList(sys.Alive, "available", state);
		parseNodesList(sys.Suspected, "dead", state);
		for (var i in sensors.gui) {
			var sensor = sensors.gui[i];
			if (!state[i])
				state[i] = "dead";
			if (state[i] == "reserved" && sensor.owned)
				state[i] = "owned"
			if (state[i].match(/reserved|dead/))
				sensor.setSelected(false);
			if (state[i] == "available" && sensor.owning)
				delete(state [i]);
			if (state[i] == "available" && sensor.owned)
				sensor.owned = false;
			if (sensor.failed)
				delete(state[i]);
		}
		setSensorsState(state);
	});
}

function updateUserState() {
	callServer("user-state.json" + nocache(),
	function(state) {
		setSensorsUserState(state);
	});
}

function setSensorsUserState(state) {
	var curr = sensors.userState || {};
	for (var i in curr) {
		var e = curr[i];
		if (i in state) {
			e.update(state[i]);
			delete(state[i]);
		}
		else {
			e.parentNode.removeChild(e);
			delete(curr[i]);
		}
	}
	for (var i in state) {
		var e = createSensorGui(i);
		setSensorHoverHandler(e);
		e.update = function(state) {
			this.className = "sensor " + state.style;
			this.text = state.text;
			this.style.zIndex = -1;
			eval(state.call);
		};
		e.update(state[i]);
		document.body.appendChild(e);
		curr[i] = e;
	}
	sensors.userState = curr;
}

function parseNodesList(str, val, state) {
	if (!str) return;
	var l = str.split("+");
	for (var i=0; i < l.length; i++) {
		var range = l[i].split("-");
		var start = parseInt(range[0]);
		var stop  = parseInt(range[1]) || start;
		for (var j=start; j <= stop; j++)
			state[j] = val;
	}
}

function setSensorsState(state) {
	for (var i in state)
		sensors.gui[i].className =
			sensors.gui[i].className
			.replace(/^.* sensor /, state[i] + ' sensor ');
}

function callServer(path, callback) {
	var req = new XMLHttpRequest();
	req.onreadystatechange = function() {
		if (this.readyState != 4)
			return;
		try {
			eval("this.json=" + this.responseText);
		}
		catch (e) {
			console.log(this);
			return;
		}
		callback(this.json);
	}
	req.path = path;
	req.open('GET', path, true);
	req.send(null);
}

function mockCallServer(path, callback) {
	var state = {};
	state[252] = "reserved";
	state[258] = state[262] = state[252];
	state[271] = "owned";
	state[272] = state[273] = state[271];
	callback(state);
}

function startSensors() {
	var sel = deselectNotOwned();
	startBlinker(sel);
	callEntryPoint("start_nodes", {}, stopBlinkerShowResult);
}

function stopSensors() {
	var sel = deselectNotOwned();
	startBlinker(sel);
	callEntryPoint("stop_nodes", {}, stopBlinkerShowResult);
}

function resetSensors() {
	var sel = deselectNotOwned();
	startBlinker(sel);
	callEntryPoint("reset_nodes", {}, stopBlinkerShowResult);
}

function nocache() {
	return "?"+new Date().getMilliseconds();
}

function startBlinker(sel, delay) {
	delay = delay || 250;
	sel.forEach(function (id) {
		var sensor = sensors.gui[id];
		sensor.blinker = setInterval(function() {
			animateBoldBorder(sensor, delay);
		}, delay*2);
	});
}

function stopBlinkerShowResult(result) {
	var res = resultAsDict(result);
	var failed = {};
	for (var id in res) {
		var sensor = sensors.gui[id];
		clearInterval(sensor.blinker);
		if (sensor.failed = res[id])
			failed[id] = true;
		res[id] = sensor.failed ? "owned failed" : "owned";
	}
	setSensorsState(res);
	startBlinker(Object.keys(failed), 100);
	setTimeout(function() {
		for (id in failed)
			clearInterval(sensors.gui[id].blinker);
	}, 2000);
}

function idFromName(nodeName) {
	return nodeName.replace(/\..*/, '').replace(/.*-/, '');
}

function resultAsDict(result) {
	var res = {};
	for (var st in result) {
		result[st].forEach(function(nodeName) {
			res[idFromName(nodeName)] = parseInt(st);
		});
	}
	return res;
}

function selectTargetSite() {
	callServer("sites.json" + nocache(), function (data) {
	modalListSelection({
		x: 610, y: 60,
		title: "Target Sensors",
		items: Object.keys(data),
		onsel: function(item) {
			callServer("set_target_sensors" +
				"?file_name=" + encodeURIComponent(data[item]),
				function () { location.reload() }
			);
		}
	});
	});
}

function updateSensors() {
	var sel = deselectNotOwned();
	if (!getSensorsSelection().length)
		return;
	callServer("firmwares.json" + nocache(), function (data) {
	modalListSelection({
		x: 450, y: 60,
		title: "Firmwares",
		items: Object.keys(data),
		onsel: function(item) {
			startBlinker(sel);
			callEntryPoint("update_nodes",
				{ firmware: data[item] },
				stopBlinkerShowResult);
		}
	});
	});
}

function grabSensors() {
	var sel = deselectOwned();
	if (!sel.length)
		return;
	modalInput({
		x: 500, y: 60, w: 3,
		title: "Duration:",
		onval: function(duration) {
			startBlinker(sel);
			sel.forEach(function (id) {
				sensors.gui[id].owning = true;
				sensors.gui[id].owned = "in progress";
			});
			callEntryPoint("grab_nodes",
				{ duration: duration },
			function(res) {
				var expId = res["id"];
				sel.forEach(function (id) {
					sensors.gui[id].owned = expId;
				});
				initOwningPoller(expId);
			});
		}
	});
}

function initOwningPoller(expId) {
	setTimeout(function() {
		callServer("get_exp_status?exp_id=" + expId,
		function (state) {
			if (!updateDeploymentStatus(state))
				initOwningPoller(expId);
		});
	}, 300);
}

function updateDeploymentStatus(expInfo) {
	if (expInfo.state == "Error")
		expInfo.deploymentresults = { 1: expInfo.nodes };

	var dr = expInfo["deploymentresults"];
	if (!dr) return false;

	stopBlinkerShowResult(dr);
	for (var id in resultAsDict(dr))
		sensors.gui[id].owning = false;
	return true;
}

function deselectOwned() {
	deselectSensors(function(s) { return s.owned });
	return getSensorsSelection();
}

function deselectNotOwned() {
	deselectSensors(function(s) { return ! s.owned });
	return getSensorsSelection();
}

function deselectSensors(func) {
	for (var i in sensors.gui) {
		var s = sensors.gui[i];
		if (s.selected && func(s))
			s.onclick();
	}
}

function callEntryPoint(entry, params, callback) {
	params = params || {};
	params.site = sensors.site;
	params.archi = sensors.archi;
	params = makeParamsString(params);
	var it = getSelectionExpIterator();
	for (var exp in it) {
		callServer(entry + "?" + params
			+ "&nodes=" + it[exp].join("+")
			+ "&exp_id=" + exp
		, callback || function() {});
	}
}

function makeParamsString(params) {
	var list = [];
	for (var x in params)
		list.push(x + "=" + encodeURIComponent(params[x]))
	return list.join("&");
}

function getSelectionExpIterator() {
	var it = {};
	var sel = getSensorsSelection();
	for (var exp, s, i=0; i < sel.length; i++) {
		s = sel[i];
		exp = sensors.gui[s].owned;
		if (!it[exp])
			it[exp] = [s];
		else
			it[exp].push(s);
	}
	return it;
}

function saveSensorsSet(spec) {
	modalInput({
		x: 60, y: 60, w: 10,
		title: "Nodes Set Name:",
		onval: function(value) {
			var set = getSensorsSelection().join(" ");
			callServer("save_node_set"
				+ "?name=" + encodeURIComponent(value)
				+ "&nodes=" + set,
				function() {});
		}
	});
}

function loadSensorsSet() {
	callServer("nodes-sets.json" + nocache(), function (data) {
	modalListSelection({
		x: 60, y: 60,
		title: "Nodes Sets",
		items: Object.keys(data),
		onsel: function(item) {
			var nodes = data[item].split(" ");
			setSensorsSelection(nodes);
		}
	});
	});
}

function clearSelectedSensors() {
	setSensorsSelection([]);
}

function selectOwnedSensors() {
	var sel = [];
	for (var i in sensors.gui) {
		if (sensors.gui[i].owned)
			sel.push(i);
	}
	setSensorsSelection(sel);	
}

function modalListSelection(p) {
	createListSelection(p).doModal();
}

function modalInput(p) {
	p.input = document.createElement("input");
	p.input.setAttribute("size", p.w);
	p.input.onkeydown = function(ev) {
		if (ev.keyCode == 13) this.nextSibling.click();
	}
	p.items = [ "ok" ];
	p.title += "<br>";
	p.onsel = function() { p.onval(p.input.value) };
	var e = createListSelection(p);
	e.insertBefore(p.input, e.firstChild.nextSibling);
	e.doModal(p.input);
}

function createListSelection(p) {
	var e = createButton(p.x, p.y, "<u>" + p.title + "</u>");
	for (var i=0; i < p.items.length; i++) {
		var b = document.createElement("p");
		b.className = "list-item";
		b.innerHTML = p.items[i];
		b.onclick = function() {
			p.onsel(this.innerHTML);
			this.parentNode.parentNode.click();
		};
		e.appendChild(b);
	}
	e.onclick = function(ev) { ev.stopPropagation(); };
	e.doModal = function(focusElt) { doModal(this, focusElt); }
	return e;
}

function doModal(dialog, focusElt) {
	var blinder = document.createElement("div");
	blinder.appendChild(dialog);
	blinder.className = "blinder";
	blinder.setAttribute("tabindex", "0"); // get keydown events
	document.dragOn = false;
	blinder.onclick = function() {
		this.parentNode.removeChild(this);
		document.dragOn = true;
	}
	blinder.onkeydown = function(ev) {
		if (ev.keyCode == 27) this.onclick();
	}
	document.body.appendChild(blinder);
	(focusElt || blinder).focus();
}

function getSensorsSelection() {
	var selection = [];
	for (var i in sensors.gui) {
		if (sensors.gui[i].selected)
			selection.push(i);
	}
	return selection;
}

function setSensorsSelection(list) {
	for (var i in sensors.gui) {
		var s = sensors.gui[i];
		if (list.indexOf(i) != -1)
			animateBoldBorder(s);
		if (s.className.match(/dead|reserved/))
			continue;
		s.selected = list.indexOf(i) != -1;
		s.setSelected(s.selected);
	}	
}

function initRegionSelector() {
	var e = document.createElement("script");
	e.src = "lib-drag-drop.js";
	e.onload = function() {
		setupRegionSelector();
	}
	document.head.appendChild(e);
}

function setupRegionSelector() {
jQuery(function($){
	document.dragOn = true;
	$( document )
		.drag("start",function( ev, dd ){
			if (!document.dragOn)
				return false;
			$(dd.counter = document.createElement("div"))
				.addClass("selection-counter")
				.appendTo(document.body);
			dd.counter.added = dd.counter.removed = 0;
			updateSelectionCount(dd, dd.counter, 0);
			return $(document.createElement("div"))
				.addClass("selector")
				.appendTo(document.body);
		})
		.drag(function( ev, dd ){
			$( dd.proxy ).css({
				top: Math.min( ev.pageY, dd.startY ),
				left: Math.min( ev.pageX, dd.startX ),
				height: Math.abs( ev.pageY - dd.startY ),
				width: Math.abs( ev.pageX - dd.startX )
			});
			updateSelectionCount(dd, dd.counter, 0);
		})
		.drag("end",function( ev, dd ){
			$( dd.proxy ).remove();
			$( dd.counter ).remove();
		});
	$('.selectable')
		.drop("start",function(ev, dd){
			$( this ).addClass("active");
			updateSelectionCount(dd, this, +1);
		})
		.drop(function( ev, dd ){
			$( this ).click();
		})
		.drop("end",function(ev, dd){
			$( this ).removeClass("active");
			updateSelectionCount(dd, this, -1);
		});
	$.drop({ multi: true });	
});
}

function updateSelectionCount(dd, elt, inc) {
	if (elt.className.match(/dead|reserved/))
		return;

	dd.counter.removed += elt.selected ? inc : 0;
	dd.counter.added   += elt.selected ? 0 : inc;
	dd.counter.total = getSensorsSelection().length
				+ dd.counter.added - dd.counter.removed;
	dd.counter.innerHTML =
		"+" + dd.counter.added +
		" -" + dd.counter.removed +
		" = " + dd.counter.total;
	//updateCounterPosition(dd);
}

function updateCounterPosition(dd) {
	dd.counter.style.left = (dd.startX + dd.deltaX/2
				- parseInt(dd.counter.clientWidth)/2) + "px";
	dd.counter.style.top  = (dd.startY + dd.deltaY/2
				- parseInt(dd.counter.clientHeight)/2) + "px";
}
