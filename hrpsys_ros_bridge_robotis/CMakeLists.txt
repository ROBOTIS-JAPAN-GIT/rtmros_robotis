cmake_minimum_required(VERSION 2.8.3)
project(hrpsys_ros_bridge_robotis)
#find_package(catkin REQUIRED COMPONENTS hrpsys_ros_bridge hrpsys openhrp3)
find_package(catkin REQUIRED COMPONENTS hrpsys_ros_bridge_tutorials hrpsys_ros_bridge euscollada rostest
  euslisp xacro control_msgs roseus)

find_package(robotis_models QUIET)
if(NOT "${robotis_models_FOUND}")
  string(ASCII 27 Esc)
  message(WARNING "${Esc}[1;33mPackage robotis_models is not found, please include source code in catkin workspace${Esc}[m")
endif()

include(FindPkgConfig)
pkg_check_modules(openhrp3 REQUIRED openhrp3.1)
set(OPENHRP_SAMPLE_DIR ${openhrp3_PREFIX}/share/OpenHRP-3.1/sample)
pkg_check_modules(hrpsys hrpsys-base REQUIRED)
catkin_python_setup()

catkin_package(
    DEPENDS
    CATKIN_DEPENDS hrpsys_ros_bridge_tutorials hrpsys_ros_bridge euscollada
    INCLUDE_DIRS # TODO include
    LIBRARIES # TODO
    )

### convert model for closed models
macro(compile_model_for_robotis_robots _robot_wrl_file _OpenHRP2_robot_name)
  if(EXISTS ${_robot_wrl_file})
    compile_openhrp_model(
      ${_robot_wrl_file}
      ${_OpenHRP2_robot_name}
      ${ARGN})
  else()
    message(STATUS "\n\n\n\n ${_robot_wrl_file} is not found..\n\n\n\n")
  endif()
endmacro()
macro(compile_robotis_model_for_robotis_robots _OpenHRP2_robot_vrml_name _OpenHRP2_robot_dir _OpenHRP2_robot_name)
  compile_model_for_robotis_robots(
    ${robotis_models_MODEL_DIR}/${_OpenHRP2_robot_dir}/${_OpenHRP2_robot_vrml_name}main.wrl
    ${_OpenHRP2_robot_name}
    ${ARGN})
endmacro()

macro(gen_minmax_table_for_robotis_robots _OpenHRP2_robot_vrml_name _OpenHRP2_robot_dir _OpenHRP2_robot_name)
  if (EXISTS ${robotis_models_MODEL_DIR}/${_OpenHRP2_robot_dir}/${_OpenHRP2_robot_vrml_name}main.wrl)
    string(TOLOWER ${_OpenHRP2_robot_name} _sname)
    set(_workdir ${PROJECT_SOURCE_DIR}/models)
    set(_gen_jointmm_command_arg "\"\\(write-min-max-table-to-robot-model-file \\(${_sname}\\) \\\"${_workdir}/${_sname}.l\\\" :margin 1.0\\)\"")
    set(_gen_jointmm_conf_command_arg "\"\\(write-min-max-table-to-conf-file \\(${_sname}\\) \\\"${_workdir}/${_OpenHRP2_robot_name}.conf\\\"\\)\"")

    find_program(euslisp_exe irteusgl)
    if(NOT EXISTS ${euslisp_exe})
      message(FATAL_ERROR "failed to find euslisp, skipping generating min max table")
    else()
      message(STATUS "find euslisp on ${euslisp_exe}")
      add_custom_command(OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/${_sname}_joint_minmax_done
      COMMAND DISPLAY= ${euslisp_exe} ${PROJECT_SOURCE_DIR}/euslisp/make-joint-min-max-table.l ${_workdir}/${_sname}.l "\"${_gen_jointmm_command_arg}\"" "\"(exit)\"" && touch ${CMAKE_CURRENT_BINARY_DIR}/${_sname}_joint_minmax_done
      DEPENDS ${_workdir}/${_sname}.l)
      add_custom_command(OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/${_sname}_joint_minmax_conf_done
      COMMAND DISPLAY= ${euslisp_exe} ${PROJECT_SOURCE_DIR}/euslisp/make-joint-min-max-table.l ${_workdir}/${_sname}.l "\"${_gen_jointmm_conf_command_arg}\"" "\"(exit)\"" && touch ${CMAKE_CURRENT_BINARY_DIR}/${_sname}_joint_minmax_conf_done
      DEPENDS ${_workdir}/${_sname}.l ${_workdir}/${_OpenHRP2_robot_name}.xml ${CMAKE_CURRENT_BINARY_DIR}/${_sname}_joint_minmax_done)
    add_custom_target(${_sname}_${PROJECT_NAME}_compile_joint_minmax DEPENDS ${CMAKE_CURRENT_BINARY_DIR}/${_sname}_joint_minmax_done ${CMAKE_CURRENT_BINARY_DIR}/${_sname}_joint_minmax_conf_done)
    add_dependencies(${_sname}_${PROJECT_NAME}_compile ${_sname}_${PROJECT_NAME}_compile_joint_minmax)
    endif()
  endif()
endmacro()

## below here, use only 2 methods: #1 compile models and #2 generate minmax table
# OP3
compile_robotis_model_for_robotis_robots(OP3 OP3 OP3
  --conf-dt-option "0.008"
  --simulation-timestep-option "0.008"
  --conf-file-option "abc_leg_offset: 0.0, 0.020, 0.0"
  --conf-file-option "end_effectors: rleg,r_ank_roll,body_link,0.0,-0.01,-0.115,0.0,0.0,0.0,0.0, lleg,l_ank_roll,body_link,0.0,-0.01,-0.115,0.0,0.0,0.0,0.0, rarm,r_el,body_link,0.0,0.0169,-0.174, larm,l_el,body_link,0.0,-0.0169,-0.174"
  --conf-file-option "collision_loop: 20"
  --conf-file-option "# in progress... "
  --conf-file-option "collision_pair: body_link:l_hip_pitch body_link:r_hip_pitch l_hip_roll:l_ank_roll l_hip_roll:r_hip_roll l_hip_roll:r_knee l_hip_roll:r_ank_roll l_knee:r_hip_roll l_knee:r_knee l_knee:r_ank_roll l_ank_roll:r_hip_roll l_ank_roll:r_knee l_ank_roll:r_ank_roll r_hip_roll:r_ank_roll head_tilt:l_el head_tilt:r_el"
  --conf-file-option "collision_model: convex hull"
  --conf-file-option "# SequencePlayer optional data (contactStates x 0 + controlSwingTime x 0 (OP3 has no sensor)"
  --conf-file-option "seq_optional_data_dim: 0"
  --conf-file-option "# OP3 gain parameters found in  op3_manager/config/dxl_init_OP3.yaml"
  --robothardware-conf-file-option "pdgains.file_name: ${PROJECT_SOURCE_DIR}/models/PDgains.sav"
  --conf-file-option "pdgains_sim_file_name: ${PROJECT_SOURCE_DIR}/models/OP3.PDgains.dat"
  )
gen_minmax_table_for_robotis_robots(OP3 OP3 OP3)

################################
## Generate default simulation launch files and euslisp interface files
################################
macro (generate_default_launch_eusinterface_files_for_robotis_robots ROBOT_DIR ROBOT_NAME)
  set(_arg_list ${ARGV})
  # remove arguments of this macro
  list(REMOVE_AT _arg_list 0 1)
  if(EXISTS ${robotis_models_MODEL_DIR}/${ROBOT_DIR}/${ROBOT_NAME}main.wrl)
    generate_default_launch_eusinterface_files("$(find robotis_models)/${ROBOT_DIR}/${ROBOT_NAME}main.wrl" hrpsys_ros_bridge_robotis ${ROBOT_NAME} ${_arg_list})
  endif()
endmacro ()

# --use-robot-hrpsys-config OR --use-unstable-hrpsys-config
generate_default_launch_eusinterface_files_for_robotis_robots(OP3 OP3 "--use-robot-hrpsys-config")

################################
## Generate and modify .urdf files
##   Org file : ROBOT.urdf, ROBOT.urdf.xacro
##   generate_hand_attached_xx_model : Generate ROBOT_body.urdf from ROBOT.urdf, ROBOT.urdf.xacro
##   run_xacro_for_hand_hrp2_model : Generate ROBOT_WH.urdf from ROBOT_body.urdf
##   attach_sensor_and_endeffector_to_hrp2jsk_urdf : Generate ROBOT_WH_SESNROS.urdf from ROBOT_WR.urdf
################################
# find xacro
find_package(xacro)
if(EXISTS ${xacro_SOURCE_PREFIX}/xacro.py)
  set(xacro_exe ${xacro_SOURCE_PREFIX}/xacro.py)
else()
  set(xacro_exe ${xacro_PREFIX}/share/xacro/xacro.py)
endif()

find_package(euscollada)
if (euscollada_SOURCE_PREFIX)
  set(euscollada_PACKAGE_PATH ${euscollada_SOURCE_PREFIX})
else ()
  set(euscollada_PACKAGE_PATH ${euscollada_PREFIX}/share/euscollada)
endif()

# Define dependency for urdf conversion to avoid parallel cmake problem (https://github.com/start-jsk/rtmros_tutorials/issues/373)
if (DEFINED compile_urdf_robots)
  add_custom_target(all_urdf_model_generate ALL DEPENDS ${compile_urdf_robots})
endif()

# Commonly used?
install(DIRECTORY euslisp launch scripts models test DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION} USE_SOURCE_PERMISSIONS)
install(CODE
  "execute_process(COMMAND echo \"fix \$ENV{DESTDIR}/${CMAKE_INSTALL_PREFIX}/${CATKIN_PACKAGE_SHARE_DESTINATION}/model/* ${CATKIN_DEVEL_PREFIX} -> ${CMAKE_INSTALL_PREFIX}\")
   file(GLOB _conf_files \"\$ENV{DISTDIR}/${CMAKE_INSTALL_PREFIX}/${CATKIN_PACKAGE_SHARE_DESTINATION}/model/*/*.conf\")
   foreach(_conf_file \${_conf_files})
     execute_process(COMMAND sed -i s@${CATKIN_DEVEL_PREFIX}@${CMAKE_INSTALL_PREFIX}@g \${_conf_file})
     execute_process(COMMAND sed -i s@${hrpsys_ros_bridge_robotis_SOURCE_DIR}@${CMAKE_INSTALL_PREFIX}/${CATKIN_PACKAGE_SHARE_DESTINATION}@g \${_conf_file})
  endforeach()
")

# add_rostest(test/test_hrpsys_pa10.launch)
# add_rostest(test/test_hrpsys_samplerobot.launch)
#add_rostest(test/samplerobot_hrpsys-ros-bridge_test.launch)

# enable... ?
# if(${robotis_models_FOUND})
#   add_rostest(test/test_robot_model.launch)
# endif()
