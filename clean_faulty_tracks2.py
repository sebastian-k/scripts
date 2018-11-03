bl_info = {
"name": "Spike Eraser",
"author": "Sebastian Koenig, Andreas Schuster",
"version": (1, 0),
"blender": (2, 7, 2),
"location": "Clip Editor > Spike Eraser",
"description": "Filter out spikes in tracker curves",
"warning": "",
"wiki_url": "",
"tracker_url": "",
"category": "Tracking"}



import bpy

from bpy.props import *

from mathutils import Vector

def denormalized_vector(context, t, i):

    sc = context.space_data
    clip = sc.clip
    width=clip.size[0]
    height=clip.size[1]


    marker = t.markers
    marker_x = marker.find_frame(i).co[0]*width
    marker_y = marker.find_frame(i).co[1]*height
    real_vector = Vector((marker_x, marker_y))
    return real_vector


def filter_values(threshold, context):

    scene = bpy.context.scene
    frameStart = scene.frame_start
    frameEnd = scene.frame_end
    sc = context.space_data
    clip = sc.clip
    length =clip.frame_duration
    width=clip.size[0]
    height=clip.size[1]
    size_vector = Vector((width, height))
    print(size_vector)

    
    print( frameStart, "to", frameEnd )
    print(length)

    
    
    bpy.ops.clip.clean_tracks(frames=10, action='DELETE_TRACK')
    

    clean_up_list=[]
    for i in range(frameStart,frameEnd):
        
        print("Frame: ", i)
        
        # get clean track list of valid tracks
        trackList = list(filter( lambda x: (x.markers.find_frame(i) and x.markers.find_frame(i-1)), clip.tracking.tracks))
                  
        # get average velocity and deselect track
        #averageVelocityVector = Vector()
        averageVelocity = Vector().to_2d()
        for t in trackList:
            t.select = False
            m_a = denormalized_vector(context, t,i)   
            m_b = denormalized_vector(context, t,i-1)  
            averageVelocity += m_a - m_b
        tracklist_length = float(len(trackList))
        if tracklist_length != 0.0: 
            averageVelocity = averageVelocity / tracklist_length
        
        print(averageVelocity.magnitude)
        # now compare all markers with average value and store in clean_up_list
        for t in trackList:            
            marker = t.markers
            # get velocity from current track 
            m_a = denormalized_vector(context, t,i)   
            m_b = denormalized_vector(context, t,i-1)
            tVelocity = m_a - m_b
            # create vector between current velocity and average and calc length
            #print("MarkerSpeed:", tVelocity.magnitude, "AverageSpeed:", averageVelocity.magnitude)
            distance = (averageVelocity-tVelocity).magnitude
            #print(tracklist_length, averageVelocity.magnitude, tVelocity.magnitude, distance)
            
            # if length greater than threshold add to list
            if distance > threshold and not t in clean_up_list:
                print( "Add Track:" , t.name, "Average Velocity:", averageVelocity.magnitude, "Distance:", distance )
                clean_up_list.append(t)


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
