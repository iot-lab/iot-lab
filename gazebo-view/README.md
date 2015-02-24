Gazebo-View
===========

Provides 3D view of a turtlebot trajectory in IoT-LAB.


Prerequisites
-------------
-  you need [gazebo-5.0.1](http://gazebosim.org/)
-  you need gcc 4.8.2 


Installation
-------------

- Install Gazebo using Ubuntu packages
[see details](http://gazebosim.org/tutorials?tut=install_ubuntu&ver=5.0&cat=install)

- Compile the iot-lab plugin (located in `mypath`):

 `$ cd my_path/gazebo-view/worlds/`
 
 `$ mkdir build & cd build`
 
 `$ cmake ..`
 
 `$ make`

- Customize Gazebo shell variable path:

  GAZEBO_MODEL_PATH = $GAZEBO_MODEL_PATH:my_path/gazebo-view/models/

Some details
------------

The plugin comes with an example of visualisation of a Turtlebot2 used
in IoT-LAB Grenoble site. The 3D world
[worlds/iot-lab_corridorJ.world](https://github.com/iot-lab/iot-lab/blob/master/gazebo-view/worlds/iot-lab_corridorJ.world)
contains :

- the transparent walls of the corridor J :
  [models/corridorJ](https://github.com/iot-lab/iot-lab/blob/master/gazebo-view/models/corridorJ)

- the docks of the Turtlebot2
  [models/turtlebot2_dock/](https://github.com/iot-lab/iot-lab/blob/master/gazebo-view/models/cturtlebot2_dockJ/)
  located in this corridor

- the M3 IoT-LAB nodes located in the corridor J 

- the Turtlebot2 :
[models/turtlebot2/](https://github.com/iot-lab/iot-lab/blob/master/gazebo-view/models/turtlebot2)
calling the c++ plugin to load and follow the trajectory of a real
IoT-LAB experiment saved in `robot.oml`

Running Visualization
---------------------

 `$ cd my_path/gazebo-view/worlds/`
 
 `$ gazebo iot-lab_corridorJ.world`

See a [video](http://youtu.be/A6DYpzkhvjI)

Create a new world
------------------

You can use our own experiment results copying oml file produced as robot.oml.

You can also defined a world file, for example `worlds/mysite.world`,
to visualize an other IoT-LAB site or part of a site. All the
description files respect the [sdf format](http://sdformat.org)

A template file, `words/template_site.world`, can help you to write
your own file. Then, you need to:

- Describe turtlebot2_dock pose (x y z roll pitch yaw) in worlds/mysite.world

- Describe an other 3D environnement, like `models/corridorJ/`, using the [building editor of gazebo](http://gazebosim.org/tutorials?tut=building_editor&cat=build_world)

- Describe the M3 IoT-LAB pose. An example of python generator in
  [grenoble.py](https://github.com/iot-lab/iot-lab/blob/master/qualif/geo/grenoble.py)

- Be careful with the offset pose between the 3D environnement, the nodes and the robot trajectories.

Todo
----
- filename oml trajectory parametrization
- multi-robot visualization
- real-time turtlebot2 pose monitoring





