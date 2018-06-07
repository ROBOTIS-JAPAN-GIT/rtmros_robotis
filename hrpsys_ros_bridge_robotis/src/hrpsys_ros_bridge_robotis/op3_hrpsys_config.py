#!/usr/bin/env python

pkg = 'hrpsys'
import imp
imp.find_module(pkg)

from hrpsys.hrpsys_config import *
import OpenHRP

class OP3HrpsysConfigurator(HrpsysConfigurator):
    def getRTCList (self):
        return self.getRTCListUnstable()
    # def init (self, robotname="OP3", url=""):
    def init (self, robotname="body_link", url=""):
        HrpsysConfigurator.init(self, robotname, url)
        print "initialize rtc parameters"
        self.setStAbcParameters()

    def defJointGroups (self):
        rleg_6dof_group = ['rleg', ['r_hip_roll', 'r_hip_pitch', 'r_hip_yaw', 'r_knee', 'r_ank_pitch', 'r_ank_roll']]
        lleg_6dof_group = ['lleg', ['l_hip_roll', 'l_hip_pitch', 'l_hip_yaw', 'l_knee', 'l_ank_pitch', 'l_ank_roll']]
        torso_group = ['torso', []]
        head_group = ['head', ['head_pan', 'head_tilt']]
        rarm_group = ['rarm', ['r_sho_pitch', 'r_sho_roll', 'r_el']]
        larm_group = ['larm', ['l_sho_pitch', 'l_sho_roll', 'l_el']]
        self.Groups = [rleg_6dof_group, lleg_6dof_group, torso_group, head_group, rarm_group, larm_group]

    # def OP3ResetPose (self):
    # def OP3InitPose (self):
    # def setResetPose (self):
    # def setResetManipPose (self):
    # def setInitPose (self):

    def setStAbcParameters (self):
        # ST parameters
        stp=self.st_svc.getParameter()
        stp.st_algorithm=OpenHRP.StabilizerService.EEFMQP
        #   eefm st params
        stp.eefm_leg_inside_margin=71.12*1e-3
        stp.eefm_leg_outside_margin=71.12*1e-3
        stp.eefm_leg_front_margin=182.0*1e-3
        stp.eefm_leg_rear_margin=72.0*1e-3
        stp.eefm_k1=[-1.39899,-1.39899]
        stp.eefm_k2=[-0.386111,-0.386111]
        stp.eefm_k3=[-0.175068,-0.175068]
        stp.eefm_rot_damping_gain=[[20*1.6*10, 20*1.6*10, 1e5]]*4 # Stiff parameter for simulation
        stp.eefm_pos_damping_gain=[[3500*50, 3500*50, 3500*1.0*5]]*4 # Stiff parameter for simulation
        #   tpcc st params
        stp.k_tpcc_p=[0.2, 0.2]
        stp.k_tpcc_x=[4.0, 4.0]
        stp.k_brot_p=[0.0, 0.0]
        stp.k_brot_tc=[0.1, 0.1]
        self.st_svc.setParameter(stp)

    def __init__(self, robotname=""):
        HrpsysConfigurator.__init__(self)
        self.defJointGroups()

if __name__ == '__main__':
    hcf = OP3HrpsysConfigurator()
    if len(sys.argv) > 2 :
        hcf.init(sys.argv[1], sys.argv[2])
    elif len(sys.argv) > 1 :
        hcf.init(sys.argv[1])
    else :
        hcf.init()
