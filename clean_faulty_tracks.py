bl_info = {
"name": "Spike Eraser",
"author": "Sebastian Koenig",
"version": (1, 0),
"blender": (2, 7, 2),
"location": "Clip Editor > Spike Eraser",
"description": "Filter out spikes in tracker curves",
"warning": "",
"wiki_url": "",
"tracker_url": "",
"category": "Tracking"}



import bpy
import numpy
from bpy.props import *




def find_speed(track, framenumber, axisnumber):
    # if marker has data then generate the speed
    marker = track.markers

    if not (marker.find_frame(framenumber) and marker.find_frame(framenumber+1)):
        pass
    else:
        a_marker = marker.find_frame(framenumber)
        b_marker = marker.find_frame(framenumber+1)
        a_vector = a_marker.co[axisnumber]
        b_vector =b_marker.co[axisnumber]
        speed = 1000*abs((a_vector-b_vector)/(b_marker.frame-a_marker.frame))
        return speed




def filter_values(threshold, context):

    framerange = bpy.context.scene.frame_end
    sc = context.space_data
    clip = sc.clip
    

    clean_up_list=[]

    for i in range(1,framerange):
        speedlist_x =[]
        speedlist_y = []
        tracklist =[]
        speed_dict_x = {}
        speed_dict_y = {}
        # go over every frame and check get the average speed

        for t in clip.tracking.tracks:
            t.select=False
            #get the speed of each marker and append to speedlist
          
            speed_dict_x[t]=find_speed(t, i, 0)
            speed_dict_y[t]=find_speed(t, i, 1)


        # still on frame(i) we get the average speed of all markers
        speedlist_x=speed_dict_x.values()
        speedlist_y=speed_dict_y.values()
        speedlist_x_clean = [x for x in speedlist_x if x is not None]
        speedlist_y_clean = [x for x in speedlist_y if x is not None]

        average_speed_x = numpy.mean(speedlist_x_clean)
        average_speed_y = numpy.mean(speedlist_y_clean)

        for track, speed in speed_dict_y.items():
            if speed is not None:
                if speed > average_speed_y*threshold:
                    print(i, track, "y:", speed, "y_a:", average_speed_y)
                    if not track in clean_up_list:
                        clean_up_list.append(track)

                    track.select = True

        for track, speed in speed_dict_x.items():
            if speed is not None:
                if speed > average_speed_x*threshold:
                    print(i, track, speed, average_speed_x)
                    if not track in clean_up_list:
                        clean_up_list.append(track)

                    track.select = True

    for t in clean_up_list:
        t.select = True
    return (len(clean_up_list))
    






class CLIP_OT_filter_tracks(bpy.types.Operator):
    bl_idname="clip.filter_tracks"
    bl_label="Filter Tracks"

    @classmethod
    def poll(cls, context):
        sc = context.space_data
        return (sc.type == 'CLIP_EDITOR') and sc.clip


    def execute(self, context):
        scn = bpy.context.scene
        sc = context.space_data
        clip = sc.clip
        tracks = filter_values(scn.track_threshold, context)
        self.report({"INFO"}, "Identified %d faulty tracks" % tracks)
        return {'FINISHED'}



class CLIP_PT_filter_tracks(bpy.types.Panel):
    bl_idname = "clip.filter_track_panel"
    bl_label = "Filter Tracks"  
    bl_space_type = "CLIP_EDITOR"
    bl_region_type = "TOOLS"
    bl_category = "Track"

    

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.operator("clip.filter_tracks")
        layout.prop(scene, "track_threshold")





def register():

    bpy.utils.register_class(CLIP_OT_filter_tracks)
    bpy.utils.register_class(CLIP_PT_filter_tracks)
    bpy.types.Scene.track_threshold = bpy.props.FloatProperty \
      (
        name = "Track Threshold",
        description = "Filter Threshold",
        default = 5.0
      )


def unregister():
    bpy.utils.unregister_class(CLIP_OT_filter_tracks)
    bpy.utils.unregister_class(CLIP_PT_filter_tracks)


if __name__ == "__main__":
    register()
