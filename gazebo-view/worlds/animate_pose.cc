/*
 * Copyright (C) 2012-2014 Open Source Robotics Foundation
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
*/
#include <string>
#include <fstream>
#include <sstream>
#include "gazebo/common/CommonTypes.hh"
#include "gazebo/common/Animation.hh"
#include "gazebo/common/KeyFrame.hh"
#include "gazebo/physics/Model.hh"
#include "gazebo/gazebo.hh"

#define BAD_VAL -9999.0

using namespace std;

namespace gazebo
{
  class AnimatePose : public ModelPlugin
  { 

  private : common::PoseAnimationPtr _anim;

  public: void read_omlfile(const char* filename) {

    ifstream filein(filename, ios::in); 
    string line;
    int irow, icol;
    float t, t_us, x, y, th;
     
    common::PoseAnimationPtr animx(
				   new common::PoseAnimation("iot-lab", 1.0, true));
    _anim = animx;
    common::PoseKeyFrame *key;

    irow = 0;

    // Skip header oml file
    while( (getline(filein, line).good()) &&  (irow < 10) ) {
      irow++;
    }
    // Read lines
    while( getline(filein, line).good() ) {
      istringstream s(line);
      string entree;
      t=BAD_VAL; x=BAD_VAL, y=BAD_VAL, th=BAD_VAL;
      icol = 0;
      while( getline(s, entree, '\t').good() ) {
	switch(icol) {
	case 0:
	  t = atof(entree.c_str());
	  break;
	case 5:
	  x = atof(entree.c_str());
	  break;
	case 6:
	  y = atof(entree.c_str());
	  break;
	case 7:
	  th = atof(entree.c_str());
	  break;
	}
	icol++;
      }
      // Read last row
      if (icol == 7) {
	getline(s, entree, '\n').good();
	th = atof(entree.c_str());
      }
	
      if ((icol!=7) || (x == BAD_VAL)|| (y == BAD_VAL) || (th == BAD_VAL)) {
	cout << "Error:: bad line " << irow << " on " << filename << endl;
      }
      else {
	//	cout <<"Point "<<irow<<" "<<t<<" "<< x <<" "<< y <<" " << th <<" "<<endl;
	key = _anim->CreateKeyFrame(t);
	key->SetTranslation(math::Vector3(x, y, 0));
	key->SetRotation(math::Quaternion(0, 0, th));
      }
      irow++;
    }
    _anim->SetLength(t+1.0);
    
  }

   public: void Callback()
    {
      printf("Animation complete\n");
    }

    public: void Load(physics::ModelPtr _parent, sdf::ElementPtr /*_sdf*/)
    {
      read_omlfile("robot.oml");
      _parent->SetAnimation(_anim,
			    boost::bind(&AnimatePose::Callback, this));
    }
  };

  // Register this plugin with the simulator
  GZ_REGISTER_MODEL_PLUGIN(AnimatePose)
}
