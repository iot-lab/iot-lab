var sTestEventType = 'mousedown';

var phi = -100, theta = 0, distance = 130;

var height=500;

var mouseX = 0, mouseY = 0, renderer, scene, camera, projector;

var infobox, container;

var objects;

var window3DWidth, window3DHeight;
var offX, offY;

// list of selected nodes
var selectedNodes = [];

//list of nodes used in sonar function
var sonarNodes = [];

var cpt=0;

//list of nodes in json file
var all_nodes = [];

//final list used 3D vue.
var final_nodes = [];


/*
*Fonction qui récupère la liste de tous les noeuds de la vue
*
*/
function loadNodes(liste){
    for (var i=0;i<(liste.length);i++){
        final_nodes[i]=new Array();
        final_nodes[i]=liste[i];
    }
}

function unselect(){
    selectedNodes=[];
}

/*
*Fonction qui génère la liste finale de noeud grâce aux données de l'experience en cours
*
*/
function upgradeNodes(data){
    for(var i=0;i<final_nodes.length;i++) {
        //on les met en unreachable de base
        final_nodes[i][5]="Unreachable";
        for(var j=0;j<data.length;j++) {
            //si le noeud est un noeud de l'expérience il est mis a jour
            if(final_nodes[i][0]==data[j])
            {
                console.log(final_nodes[i][0] + " -> Busy");
                final_nodes[i][5]="Busy";
            }
        }
    }
}

/*
*Fonction d'initialisation de la scene 3D
*
*/

function init_3d() {

    container= document.getElementById('div3d');
    infobox= document.getElementById('infobox');

    objects=new Array();

    renderer= new THREE.CanvasRenderer();
    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(75, window3DWidth/window3DHeight,1,10000);

    //Projecteur utiliser pour la selection de noeuds.
    projector = new THREE.Projector();

    infobox.innerHTML = 'Node info : ';


    offY = container.offsetTop;
    offX = container.offsetLeft;

    container.appendChild(renderer.domElement);

    window.addEventListener('resize', set3dsize, false);
    scene.add(camera);
    set3dsize();

    create_particle(final_nodes);

    camera.lookAt(scene.position);

    //création des 3 axes pour s'orienter.
    debugaxis(10);  

    //Gestion des actions de la souris.
    container.onmousedown = OnMouseDown;
    container.onmouseup = OnMouseUp;
    container.onmousemove = displayNodeInfo;

    if (container.addEventListener)
        /** DOMMouseScroll is for mozilla. */
        container.addEventListener('DOMMouseScroll', wheel, false);
    /** IE/Opera. */
    container.onmousewheel = container.onmousewheel = wheel;

    //Mise à jour de l'affichage
    myrender();
}

function set3dsize() {
    offY = container.offsetTop;
    offX = container.offsetLeft;
    window3DWidth = container.offsetWidth;
    window3DHeight = container.offsetHeight;
    renderer.setSize(window3DWidth, window3DHeight);

    camera.aspect = window3DWidth / window3DHeight;
    camera.updateProjectionMatrix();

    myrender();
}

/*
*Fonction permettant de paser la liste de noeuds reçue et de créer des particules
*et de les ajouter à la scene.
*
*/
function create_particle(nodes_list){
    // let's find the center of the nodes
    var xmin,xmax,ymin,ymax,zmin,zmax;
    xmin = ymin = zmin = 0;
    xmax = ymax = zmax = 0;

    for (var i = 0; i < nodes_list.length; i++) {
        if (parseFloat(nodes_list[i][1]) > xmax) xmax = parseFloat(nodes_list[i][1]);
        if (parseFloat(nodes_list[i][1]) < xmin) xmin = parseFloat(nodes_list[i][1]);
        if (parseFloat(nodes_list[i][2]) > ymax) ymax = parseFloat(nodes_list[i][2]);
        if (parseFloat(nodes_list[i][2]) < ymin) ymin = parseFloat(nodes_list[i][2]);
        if (parseFloat(nodes_list[i][3]) > zmax) zmax = parseFloat(nodes_list[i][3]);
        if (parseFloat(nodes_list[i][3]) < zmin) zmin = parseFloat(nodes_list[i][3]);
    }

    var xcenter = (xmax + xmin) / 2;
    var ycenter = (ymax + ymin) / 2;
    var zcenter = (zmax + zmin) / 2;

    for (var i=0;i<nodes_list.length;i++)
    {
        var couleur = 0xffffff;
        var particle = new THREE.Particle( new THREE.ParticleCanvasMaterial({

            color: couleur,
            opacity: 1,
            program: function(context){
                context.beginPath();
                context.arc(0,0,1,0,Math.PI*2,true);
                context.closePath();
                context.fill();
            }
        }));
        particle.name = nodes_list[i][0];
        particle.position.x=(parseFloat(nodes_list[i][1])-xcenter);
        particle.position.y=(parseFloat(nodes_list[i][2])-ycenter);
        particle.position.z=(parseFloat(nodes_list[i][3])-zcenter);
        particle.position.multiplyScalar(10);
        particle.archi = nodes_list[i][4];
        particle.state = nodes_list[i][5];
        particle.scale.x=particle.scale.y=1;
        objects.push(particle);
        scene.add(particle);

    }
    init_color();
}

function sonar(node){
    for (var i = 0; i < objects.length; i++) {
        if (objects[i].name == node){
            var col = 0xff8400;//(Math.abs(parseFloat(sonarlist[j][1]))/100);
            objects[i].material.color.setHex(col);
        }
    }
    myrender();
}



function init_color() {
    sonarNodes=[];
    for (var i = 0; i < objects.length; i++) {

        if (selectedNodes.indexOf(objects[i].name) != -1) {
            //bleu clair
            objects[i].material.color.setHex(0x0099CC);
        }
        else if (objects[i].state == "Unreachable") {
                //gris
                objects[i].material.color.setHex(0x393939);
            }
            else if (objects[i].state == "Busy") {
                //violet
                objects[i].material.color.setHex(0x9943BE);
            }
            else if (objects[i].state == "Alive") {
                //vert
                objects[i].material.color.setHex(0x7FFF00);
            }
            else {
                //rouge
                objects[i].material.color.setHex(0xFF3030);
            }
    }
}

/*
*Fonction permettant d'actualiser la scene
*(fonction d'affichage)
*
*/
function myrender() {
    //infobox.innerHTML = " Cam Pos = " + camera.position.x + "," + camera.position.y + "," + camera.position.z
    //                + " - " + theta + "," + phi + ","+ distance;
    //infobox.innerHTML = selectedNodes;
    camera.position.x = distance * Math.sin(theta * Math.PI / 360) * Math.cos(phi * Math.PI / 360);
    camera.position.y = distance * Math.sin(phi * Math.PI / 360);
    camera.position.z = distance * Math.cos(theta * Math.PI / 360) * Math.cos(phi * Math.PI / 360);
    camera.lookAt(scene.position);
    camera.updateMatrix();
    renderer.render(scene, camera);
}



/*
*Fonction permettant de trouver le noeud situé en dessous de la souris
*
*/

function findNodeUnderMouse(event) {

    var target = event.target;
    pos_x = event.clientX;
    pos_y = event.clientY;
    var rect = target.getBoundingClientRect();
    var left = pos_x - rect.left - target.clientLeft + target.scrollLeft;
    var top = pos_y - rect.top - target.clientTop + target.scrollTop;
    var deviceX = left / target.clientWidth * 2 - 1;
    var deviceY = -top / target.clientHeight * 2 + 1;
    var vector = new THREE.Vector3(deviceX, deviceY, 0.5);
    projector.unprojectVector(vector, camera);
    var ray = new THREE.Raycaster(camera.position, vector.sub(camera.position).normalize());
    var intersects = ray.intersectObjects(objects);
    if (intersects.length > 0) {
        //if a retirer pour un simple test
        if(isNaN(intersects[0].object.position.x)) {
            return null;
        }
        else {
            return intersects[0];
        }
    } else return null;
}

/*
*Fonction permettant de selectionner un noeud
*
*/
function toggleNode(obj) {
    nodeId = obj.object.name;
    var i = selectedNodes.indexOf(nodeId);
    if (i == -1) {
        selectedNodes.push(nodeId);
        handle_selected(obj);
    }
    else {
        selectedNodes.splice(i, 1);
    }
    init_color();
    myrender();

}

/*
*Fonction permettant de créer un vecteur
*
*/
function v(x, y, z) {
    return new THREE.Vector3(x,y,z);
}

/*
*Fonction qui crée des axes et les ajoute à la scène
*
*/
function createAxis(p1, p2, color) {
    var line, lineGeometry = new THREE.Geometry(),
        lineMat = new THREE.LineBasicMaterial({ color: color, lineWidth: 2 });
    lineGeometry.vertices.push(p1, p2);
    line = new THREE.Line(lineGeometry, lineMat);
    scene.add(line);
}

/*
*Fonction permettant de créer le repère de la figure 3D
*(en créant 3 axes)
*
*/
function debugaxis(axisLength) { 
    createAxis(v(0, 0, 0), v(axisLength, 0, 0), 0xFF0000);
    createAxis(v(0, 0, 0), v(0, axisLength, 0), 0x00FF00);
    createAxis(v(0, 0, 0), v(0, 0, axisLength), 0x0000FF);
}



/*
*Fonction permettant une action après un clic
*traite les deux cas clic droit et clic gauche
*/
function OnMouseDown(e) {
    var clickType = 'LEFT';
    if (e.type != sTestEventType) return true;
    if (e.which) {
        if (e.which == 3) clickType = 'RIGHT';
        if (e.which == 2) clickType = 'MIDDLE';
    }
    mouseX = e.clientX;
    mouseY = e.clientY;
    if (clickType == 'RIGHT') {
        document.onmousemove = onDocumentMouseMoveRot;
    }
    if (clickType == 'LEFT') {
        obj = findNodeUnderMouse(e);
        if (obj != null) toggleNode(obj);
    }
}

/*
*Fonction permettant une action lors de l'arrêt d'un clic
*
*/
function OnMouseUp(e) {
    document.onmousemove = displayNodeInfo;
}

/*
* display some info of the node under the mouse
*
*/
function displayNodeInfo(e) {
   // display some info of the node under the mouse
    obj = findNodeUnderMouse(e);
    if (obj) {
        infobox.innerHTML = 'Node info : '+ String(obj.object.name) + ' with archi ' + String(obj.object.archi);
    }

   // else infobox.innerHTML ='Node info 2: '+ e.clientX + "," + e.clientY + " - " + offX + "," + offY;

}

/*
*Fonction permettant la rotation de la camera lors d'un clic droit
*
*/
function onDocumentMouseMoveRot(event) {
    NewmouseX = event.clientX;
    NewmouseY = event.clientY;
    DeltaX = NewmouseX - mouseX;
    DeltaY = NewmouseY - mouseY;

    mouseX = NewmouseX;
    mouseY = NewmouseY;

    theta -= DeltaX;
    phi += DeltaY;
    if (phi > 180) phi = 180;
    if (phi < -180) phi = -180;
    myrender();
}


/*
* This function was taken here : http://www.adomas.org/javascript-mouse-wheel/
* Event handler for mouse wheel event.
* Permet l'interaction avec le scroll de la souris
*/
function wheel(event) {
    var delta = 0;
    if (!event) /* For IE. */
        event = window.event;
    if (event.wheelDelta) { /* IE/Opera. */
        delta = event.wheelDelta / 120;
    } else if (event.detail) { /** Mozilla case. */
        /** In Mozilla, sign of delta is different than in IE.
         * Also, delta is multiple of 3.
         */
        delta = -event.detail / 3;
    }
    /** If delta is nonzero, handle it.
     * Basically, delta is now positive if wheel was scrolled up,
     * and negative, if wheel was scrolled down.
     */
    if (delta)
        Zoom(delta);
    /** Prevent default actions caused by mouse wheel.
     * That might be ugly, but we handle scrolls somehow
     * anyway, so don't bother here..
     */
    if (event.preventDefault)
        event.preventDefault();
    event.returnValue = false;
}          


/*
*Fonnction utilisé pour le zoom de la souris
*
*/
function Zoom(delta) {
    distance += delta * 5;
    myrender();
}


