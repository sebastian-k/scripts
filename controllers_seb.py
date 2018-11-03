import sys
import time
import openvr
import bpy, math
import bmesh
import mathutils
import numpy as np
import pprint
from random import random
from bpy.types import Panel
import bmesh
from mathutils import Vector, Matrix
import copy
from bpy.props import BoolProperty, FloatVectorProperty


openvr.init(openvr.VRApplication_Scene)
poses_t = openvr.TrackedDevicePose_t * openvr.k_unMaxTrackedDeviceCount
poses = poses_t()


vert_start = bpy.data.objects["Suzanne"].data.vertices
print(vert_start)

class ModalTimerOperator(bpy.types.Operator):
    """Operator which runs its self from a timer"""
    bl_idname = "wm.modal_timer_operator"
    bl_label = "Modal Timer Operator"

    _timer = None
    wm = bpy.context.window_manager

    #wm.controller_location_start = bpy.data.objects['VR_Controller_l'].location
    #print(wm.controller_location_start)

    wm['selected_verts'] = []

    print(wm['selected_verts'])
    #sel_verts = wm['selected_verts']
    
    def __init__(self):
        self.openvrEvent = openvr.VREvent_t()
        self.space = bpy.data.objects['VR_Space']
        self.leftController = bpy.data.objects['VR_Controller_l']
        self.rightController = bpy.data.objects['VR_Controller_r']
        self.leftTractorBeam = bpy.data.objects['VR_Tractor_Beam_l']
        self.rightTractorBeam = bpy.data.objects['VR_Tractor_Beam_r']
        self.camera = bpy.data.objects['VR_Camera']
        
        self.leftControllerRestMatrix = self.leftController.matrix_world.copy()
        self.rightControllerRestMatrix = self.rightController.matrix_world.copy()
        
        self.leftTractorBeamActive = False
        self.rightTractorBeamActive = False
        
        self.leftTractorBeamTarget = None
        self.rightTractorBeamTarget = None
        
    def resetControllers(self):
        self.leftController.matrix_world = self.leftControllerRestMatrix
        self.leftTractorBeam.hide = True
        self.rightController.matrix_world = self.rightControllerRestMatrix
        self.rightTractorBeam.hide = True
    
    def poseToBlenderMatrix(self, pose):
        t = pose.mDeviceToAbsoluteTracking
        # TODO: use mathutils.Matrix() instead
        # Currently the matrix misses the translation part
        return [
            [t[0][0], -t[2][0], t[1][0], 0.0],
            [t[0][1], -t[2][1], t[1][1], 0.0],
            [t[0][2], -t[2][2], t[1][2], 0.0],
            [t[0][3], -t[2][3], t[1][3], 1.0,]
        ]
    
    def alignController(self, controller, matrix):
        # TODO: once we have a real matrix object we can enable this
        '''
        transform = matrix.decompose()
        controller.location = transform[0]
        controller.rotation_quaternion = transform[1]
        '''
        controller.matrix_world = matrix
    
    def updateControllerWithPose(self, controller, pose):
        e = self.poseToBlenderMatrix(pose)
        self.alignController(controller, e)
    
    def handleOpenvrEvent(self):
        if openvr.VRSystem().pollNextEvent(self.openvrEvent):
            eventDevice = self.openvrEvent.trackedDeviceIndex
            eventType = self.openvrEvent.eventType
            eventData = self.openvrEvent.data
            eventButton = None
            
            if (eventData.controller and eventData.controller.button):
                eventButton = eventData.controller.button
            
            if eventType == openvr.VREvent_ButtonPress:
                if eventButton == openvr.k_EButton_SteamVR_Trigger:
                    self.handleTriggerPressed(eventDevice)

                if eventButton == openvr.k_EButton_SteamVR_Touchpad:
                    self.handleTouchpadPressed(eventDevice)
                    
            if eventType == openvr.VREvent_ButtonUnpress:
                if eventButton == openvr.k_EButton_SteamVR_Trigger:
                    self.handleTriggerUnpressed(eventDevice)
                    
                if eventButton == openvr.k_EButton_SteamVR_Touchpad:
                    self.handleTouchpadUnpressed(eventDevice)
    
    def handleTriggerPressed(self, deviceIndex):
        wm = bpy.context.window_manager
        print('trigger pressed on %d' % deviceIndex)
        if (deviceIndex == 1):    
            wm.grab_trigger = True
            wm['selected_verts'] = [v.index for v in bpy.data.objects['Suzanne'].data.vertices if v.select]
    
    
    def handleTriggerUnpressed(self, deviceIndex):
        print('trigger unpressed on %d' % deviceIndex)

        if (deviceIndex == 1):    
            bpy.context.window_manager.grab_trigger = False 
    
    
    def grab(self, controller_location_start):
        if not bpy.context.object.mode == "EDIT":
            bpy.ops.object.mode_set(mode="EDIT")

        controller_mesh = bpy.context.scene.objects['VR_Controller_l'].data
        bm1 = bmesh.new()
        bm1.from_mesh(controller_mesh)

        bm1.verts.ensure_lookup_table()

        # Convert local coorinates to world coordinates before assignment
        vertCoordinates = bpy.data.objects['VR_Controller_l'].matrix_world * bm1.verts[5182].co.xyz


        # Set the coordinates of the first vertices of 'Cube' object
        target_mesh = bpy.context.scene.objects['Suzanne'].data
        bm2 = bmesh.from_edit_mesh(target_mesh)
        bm2.verts.ensure_lookup_table()

        verts = []
        for v in bm2.verts:            
            if v.select == True:
                verts.append(v)
        print(verts[0]) 
        master_vert = verts[0]


            # Convert world coorinates to local coordinates before assignment
        master_vert.co.xyz = bpy.data.objects['Suzanne'].matrix_world.inverted() * vertCoordinates 
        
        for v in bm2.verts:
            print(v)
            if not v == master_vert:
                print("ma: ", master_vert)
                old_pos = copy.copy(v.co)
                print(old_pos)
                v.co = old_pos + master_vert.co

        #bm2.to_mesh(target_mesh)




    def handleTouchpadPressed(self, deviceIndex):
        if (deviceIndex == 1):
            self.leftTractorBeam.hide = False
            self.leftTractorBeamActive = True
            bpy.ops.object.parent_set(type='OBJECT')
            '''
            # Get the coordinates of the first vertices of 'Plane' object
            firstObjData = bpy.context.scene.objects['VR_Controller_l'].data
            bm1 = bmesh.new()
            bm1.from_mesh(firstObjData)

            bm1.verts.ensure_lookup_table()

            # Convert local coorinates to world coordinates before assignment
            vertCoordinates = bpy.data.objects['VR_Controller_l'].matrix_world * bm1.verts[0].co.xyz

            print(vertCoordinates)

            # Set the coordinates of the first vertices of 'Cube' object
            secondObjData = bpy.context.scene.objects['AF'].data
            bm2 = bmesh.new()
            bm2.from_mesh(secondObjData)

            bm2.verts.ensure_lookup_table()

            # Convert world coorinates to local coordinates before assignment
            bm2.verts[0].co.xyz = bpy.data.objects['AF'].matrix_world.inverted() * vertCoordinates 

            bm2.to_mesh(secondObjData)
            '''
            max = 100000 #max distance

            if not bpy.context.object.mode == "EDIT":
                bpy.ops.object.mode_set(mode="EDIT")

            #print (point)
            result = [] #stores the results

            controller = bpy.data.objects["VR_Controller_l"].location.xyz #reference point from which we seek the distances (set your reference vertex in global coordinates here)
            obj = bpy.data.objects['Suzanne']
            pos = obj.matrix_world.inverted() * controller #converts the reference to local space
            shortest = None
            shortestDist = max

            mesh = bmesh.from_edit_mesh(obj.data)
            mesh.verts.ensure_lookup_table()
            for v in mesh.verts: #go through all vertices
                dist = (Vector(v.co) - pos).length  #calculate the distance
                if dist < shortestDist : #test if better so far
                    shortest = v
                    shortestDist = dist

            result.append([obj, shortest, shortestDist]) #append the result
            mesh.verts[shortest.index].select = True
   
    def handleTouchpadUnpressed(self, deviceIndex):
        if (deviceIndex == 1):
            self.leftTractorBeam.hide = True
            self.leftTractorBeamActive = False
            bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
        if (deviceIndex == 4):
            self.rightTractorBeam.hide = True
            self.rightTractorBeamActive = False
    
    #def handleTractorBeams():
    #    if self.rightTractorBeamActive:
            # TODO: iterate through all scene objects (expect VR objects)
            # and find out it the tractor beam object intersects with it
            # if yes, store this object in self.rightTractorBeamTarget
            # after releasing the trigger button select self.rightTractorBeamTarget
    
    def modal(self, context, event):
        wm = bpy.context.window_manager
        if event.type in {'ESC'}:
            self.cancel(context)
            return {'CANCELLED'}
 
        if event.type == 'TIMER':
            # get all poses
            openvr.VRCompositor().waitGetPoses(poses, len(poses), None, 0)

            
            self.updateControllerWithPose(self.leftController, poses[1])
            self.updateControllerWithPose(self.rightController, poses[4])

            if wm.grab_trigger == True:
                wm.controller_location_start = bpy.data.objects['VR_Controller_l'].location
                self.grab(wm.controller_location_start)
            self.handleOpenvrEvent()
            
            #self.handleTractorBeams()
            
        return {'PASS_THROUGH'}

    def execute(self, context):
        wm = context.window_manager
        self._timer = wm.event_timer_add(1.0 / 75.0, context.window)
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)
        self.resetControllers()
        # openvr.shutdown()


def register():
    bpy.utils.register_class(ModalTimerOperator)

    bpy.types.WindowManager.grab_trigger = BoolProperty(
        name = "Grab trigger",
        description = "Is the trigger pressed or not",
        default=False
        )
    bpy.types.WindowManager.controller_location_start = FloatVectorProperty(
        name = "Controller Start Position",
        description = "Which position the controller was perviously",
        default=(0.0,0.0,0.0),
        subtype = 'XYZ'
        )

def unregister():
    bpy.utils.unregister_class(ModalTimerOperator)


if __name__ == "__main__":
    register()


