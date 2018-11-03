import bpy

# track a marker
# define as guide [button]
# --> get keyframes and add to list
# set frame limit until first keyfame


#def define_clip(context, track):
#   print("guided track ist:", track)

#def get_keyed_frame(track):
scene = bpy.context.scene
frame_start = scene.frame_start
frame_end = scene.frame_end
clip = bpy.data.movieclips['MVI_4005.MOV']


key_list=[]

for i in range(frame_start, frame_end):
    if clip.tracking.tracks.active.markers.find_frame(i):
        if clip.tracking.tracks.active.markers.find_frame(i).is_keyed:
            key_list.append(i)
print (key_list)


for i in key_list:
    print(i)
    for t in clip.tracking.tracks:
        if t.select:
            t.frames_limit=i
            print(t)
    # set frame limit to i
    # track


def guided_track(context):
    scene = bpy.context.scene
    frame_start = scene.frame_start
    frame_end = scene.frame_end
    clip = bpy.data.movieclips['MVI_4005.MOV']

    clip.tracking.tracks.active.frames_limit=5
    print("set 5")
    bpy.ops.clip.track_markers(backwards=False, sequence=True)
    print("tracked")
    clip.tracking.tracks.active.frames_limit=10
    print("set 10")
    bpy.ops.clip.track_markers(backwards=False, sequence=True)
    print("tracked")


class CLIP_OT_setup_tracking_guide(bpy.types.Operator):
    bl_idname="clip.setup_tracking_guide"
    bl_label="Guide Track"

    @classmethod
    def poll(cls, context):
        sc = context.space_data
        return (sc.type == 'CLIP_EDITOR') and sc.clip

    def execute(self, context):
        guided_track(context)
        guided_track(context)
        return {'FINISHED'}

class CLIP_PT_filter_tracks(bpy.types.Panel):
    bl_idname = "clip.guided_tracks"
    bl_label = "Guided Tracks"  
    bl_space_type = "CLIP_EDITOR"
    bl_region_type = "TOOLS"
    bl_category = "Track"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.operator("clip.setup_tracking_guide")

def register():
    bpy.utils.register_class(CLIP_OT_setup_tracking_guide)
    bpy.utils.register_class(CLIP_PT_filter_tracks)

def unregister():
    bpy.utils.unregister_class(CLIP_OT_setup_tracking_guide)
    bpy.utils.unregister_class(CLIP_PT_filter_tracks)

if __name__ == "__main__":
    register()
