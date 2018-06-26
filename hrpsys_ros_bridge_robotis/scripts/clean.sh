#!/bin/bash

cd `rospack find hrpsys_ros_bridge_robotis`/ && rm -rf ./launch ./build
cd `rospack find hrpsys_ros_bridge_robotis`/models && rm -rf *.conf *.dae *.urdf *.xml *.yaml *.l *_meshes
