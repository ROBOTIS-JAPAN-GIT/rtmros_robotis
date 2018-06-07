(load "package://hrpsys_ros_bridge/euslisp/rtm-ros-robot-interface.l")
(require :op3 "package://hrpsys_ros_bridge_robotis/models/op3.l")
(when (probe-file (ros::resolve-ros-path "package://hrpsys_ros_bridge_robotis/euslisp/op3-utils.l"))
  (require :op3-utils "package://hrpsys_ros_bridge_robotis/euslisp/op3-utils.l"))

(defclass op3-interface
  :super rtm-ros-robot-interface
  :slots ())
(defmethod op3-interface
  (:init (&rest args)
         (send-super* :init :robot op3-robot args)))

(defun op3-init (&rest args)
  (if (not (boundp '*ri*))
      (setq *ri* (instance* op3-interface :init args)))
  (if (not (boundp '*op3*))
      (setq *op3* (instance op3-robot :init))))
