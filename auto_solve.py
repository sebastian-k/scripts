bl_info = {
"name": "Spike Eraser",
"author": "Sebastian Koenig, Andreas Schuster",
"version": (1, 0),
"blender": (2, 7, 2),
"location": "Clip Editor > Auto Solve",
"description": "Filter out spikes in tracker curves",
"warning": "",
"wiki_url": "",
"tracker_url": "",
"category": "Movie Tracking"}





import bpy

from bpy.props import *



def auto_solve(context):

    scene = bpy.context.scene
    frameStart = scene.frame_start
    frameEnd = scene.frame_end
    sc = context.space_data
    clip = sc.clip
    clp = bpy.ops.clip
    length =clip.frame_duration
    camera = clip.tracking.camera
    
    clip.tracking.objects.active.keyframe_a=scene.frame_start
    clip.tracking.objects.active.keyframe_b=scene.frame_start+60
    clip.tracking.settings.refine_intrinsics = 'FOCAL_LENGTH_RADIAL_K1_K2'
    bpy.ops.clip.clean_tracks(frames=10, action='DELETE_TRACK')

    clp.solve_camera()
    if camera.focal_length > 100 or abs(camera.k1) > 1:
        clip.tracking.settings.use_keyframe_selection= True

    clip.tracking.settings.use_keyframe_selection= False
    bpy.ops.clip.clean_tracks(error=2, action='DELETE_TRACK')

    clp.solve_camera()
    bpy.ops.clip.clean_tracks(error=1, action='DELETE_TRACK')

    clp.solve_camera()
    

class CLIP_OT_filter_tracks(bpy.types.Operator):
    bl_idname="clip.auto_solve"
    bl_label="Auto Solve"

    @classmethod
    def poll(cls, context):
        sc = context.space_data
        return (sc.type == 'CLIP_EDITOR') and sc.clip


    def execute(self, context):
        scn = bpy.context.scene
        auto_solve(context)
        return {'FINISHED'}


class CLIP_PT_filter_tracks(bpy.types.Panel):
    bl_idname = "clip.filter_track_panel"
    bl_label = "Auto Solve"  
    bl_space_type = "CLIP_EDITOR"
    bl_region_type = "TOOLS"
    bl_category = "Solve"

    

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.operator("clip.auto_solve")





def register():

    bpy.utils.register_class(CLIP_OT_filter_tracks)
    bpy.utils.register_class(CLIP_PT_filter_tracks)
   


def unregister():
    bpy.utils.unregister_class(CLIP_OT_filter_tracks)
    bpy.utils.unregister_class(CLIP_PT_filter_tracks)


if __name__ == "__main__":
    register()
