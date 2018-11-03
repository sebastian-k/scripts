bl_info = {
"name": "Tracking Pies",
"author": "Sebastian Koenig, Keir Mierle, Andreas Schuster",
"version": (1, 2),
"blender": (2, 7, 3),
"location": "Clip Editor > Tracking Pies",
"description": "Pie Controls for Tracking",
"category": "Movie Tracking"}

'''
This script adds tracking pies to the clip editor.
Hotkeys:
Q:      Marker Setup
W:      Setup Clip and Display options
E:      Tracking commands
Shift+S: Solving
Shift+W: Scene Reconstruction
OSkey+A: Playback and frame jumping commands
'''


import bpy
from bpy.types import Menu
from bpy.props import FloatProperty
from mathutils import Vector


############ FUNCTIONS ##################

def get_marker_coordinates_in_pixels(context, clip, track, frame_number):
    width, height = clip.size
    marker = track.markers.find_frame(frame_number)
    return Vector((marker.co[0] * width, marker.co[1] * height))

def marker_velocity(context, clip, track, frame):
    marker_a = get_marker_coordinates_in_pixels(context, clip, track, frame)
    marker_b = get_marker_coordinates_in_pixels(context, clip, track, frame - 1)
    return marker_a - marker_b


def filter_values(context, threshold):
    scene = context.scene
    frame_start = scene.frame_start
    frame_end = scene.frame_end
    clip = context.space_data.clip
    length = clip.frame_duration

    bpy.ops.clip.clean_tracks(frames=10, action='DELETE_TRACK')

    tracks_to_clean = []

    for frame in range(frame_start, frame_end + 1):     

        # Find tracks with markers in both this frame and the previous one.
        relevant_tracks = [track for track in clip.tracking.tracks
                           if track.markers.find_frame(frame) and
                              track.markers.find_frame(frame - 1)]

        if not relevant_tracks:
            continue

        # Get average velocity and deselect track.
        average_velocity = Vector((0.0, 0.0))
        for track in relevant_tracks:
            track.select = False
            average_velocity += marker_velocity(context, clip, track, frame)
        if len(relevant_tracks) >= 1:
            average_velocity = average_velocity / len(relevant_tracks)

        # Then find all markers that behave differently than the average.
        for track in relevant_tracks:
            track_velocity = marker_velocity(context, clip, track, frame)
            distance = (average_velocity - track_velocity).magnitude

            if distance > threshold and not track in tracks_to_clean:
                tracks_to_clean.append(track)

    for track in tracks_to_clean:
        track.select = True
    return len(tracks_to_clean)


############# CLASSES #############

class CLIP_OT_track_settings_to_track(bpy.types.Operator):
    """Copy tracking settings from active track to selected tracks"""

    bl_label = "Copy Track Settings"
    bl_idname = "clip.track_settings_to_track"
    bl_options = {'UNDO', 'REGISTER'}

    _attrs_track = (
        "correlation_min",
        "frames_limit",
        "pattern_match",
        "margin",
        "motion_model",
        "use_brute",
        "use_normalization",
        "use_mask",
        "use_red_channel",
        "use_green_channel",
        "use_blue_channel",
        "weight"
        )

    _attrs_marker = (
        "pattern_corners",
        "search_min",
        "search_max",
        )

    @classmethod
    def poll(cls, context):
        space = context.space_data
        if space.type != 'CLIP_EDITOR':
            return False
        clip = space.clip
        return clip and clip.tracking.tracks.active


    def execute(self, context):
        space = context.space_data
        clip = space.clip
        track = clip.tracking.tracks.active

        framenr = context.scene.frame_current - clip.frame_start + 1

        for t in clip.tracking.tracks:
            if t.select:
                marker = track.markers.find_frame(framenr, False)
                marker_selected = t.markers.find_frame(framenr, False)
                for attr in self._attrs_track:
                    setattr(t, attr, getattr(track, attr))
                for attr in self._attrs_marker:
                    setattr(marker_selected, attr, getattr(marker, attr))

        return {'FINISHED'}



class CLIP_OT_filter_tracks(bpy.types.Operator):
    bl_label="Filter Tracks"
    bl_idname="clip.filter_tracks"
    bl_options = {'UNDO', 'REGISTER'}

    track_threshold = FloatProperty(
            name="Track Threshold",
            description="Filter Threshold to select problematic track",
            default=5.0,
            )

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return (space.type == 'CLIP_EDITOR') and space.clip

    def execute(self, context):
        num_tracks = filter_values(context, self.track_threshold)
        self.report({'INFO'}, "Identified %d problematic tracks" % num_tracks)
        return {'FINISHED'}



class CLIP_OT_set_active_clip(bpy.types.Operator):
    bl_label = "Set Active Clip"
    bl_idname = "clip.set_active_clip"

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return space.type == 'CLIP_EDITOR'

    def execute(self, context):
        clip = context.space_data.clip
        scene = context.scene
        scene.active_clip = clip
        scene.render.resolution_x = clip.size[0]
        scene.render.resolution_y = clip.size[1]
        return {'FINISHED'}



class CLIP_PIE_refine_pie(Menu):
    # Refinement Options
    bl_label = "Refine Intrinsics"

    def draw(self, context):
        clip = context.space_data.clip
        settings = clip.tracking.settings

        layout = self.layout
        pie = layout.menu_pie()

        pie.prop(settings, "refine_intrinsics", expand=True)



class CLIP_PIE_geometry_reconstruction(Menu):
    # Geometry Reconstruction
    bl_label = "Reconstruction"

    def draw(self, context):
        space = context.space_data

        layout = self.layout
        pie = layout.menu_pie()

        pie.operator("clip.bundles_to_mesh", icon='MESH_DATA')
        pie.operator("clip.track_to_empty", icon='EMPTY_DATA')



class CLIP_PIE_proxy_pie(Menu):
    # Proxy Controls
    bl_label = "Proxy Size"

    def draw(self, context):
        space = context.space_data

        layout = self.layout
        pie = layout.menu_pie()

        pie.prop(
            space.clip,
            "use_brute",
            text="Use Proxy",
            icon=('CHECKBOX_HLT' if space.clip.use_proxy else 'CHECKBOX_DEHLT')
            )
        pie.prop(space.clip_user, "proxy_render_size", expand=True)      


class CLIP_PIE_display_pie(Menu):
    # Display Options
    bl_label = "Marker Display"

    def draw(self, context):
        space = context.space_data

        layout = self.layout
        pie = layout.menu_pie()

        pie.prop(space, "show_names", text="Show Track Info", icon='WORDWRAP_ON')
        pie.prop(space, "show_disabled", text="Show Disabled Tracks", icon='VISIBLE_IPO_ON')
        pie.prop(space, "show_marker_search", text="Display Search Area", icon='VIEWZOOM')
        pie.prop(space, "show_marker_pattern", text="Display Pattern Area", icon='BORDERMOVE')



class CLIP_PIE_marker_pie(Menu):
    # Settings for the individual markers
    bl_label = "Marker Settings"
    bl_idname = "clip.marker_pie"

    def draw(self, context):
        clip = context.space_data.clip
        settings = clip.tracking.settings
        track_active = clip.tracking.tracks.active

        layout = self.layout
        pie = layout.menu_pie()

        prop = pie.operator("wm.context_set_enum", text="Loc", icon='OUTLINER_DATA_EMPTY')
        prop.data_path="space_data.clip.tracking.tracks.active.motion_model"
        prop.value = "Loc"
        prop = pie.operator("wm.context_set_enum", text="Affine", icon='OUTLINER_DATA_LATTICE')
        prop.data_path="space_data.clip.tracking.tracks.active.motion_model"
        prop.value = "Affine"

        pie.operator("clip.track_settings_to_track", icon='COPYDOWN')
        pie.operator("clip.track_settings_as_default", icon='SETTINGS')

        if track_active:
            pie.prop(
                track_active,
                "use_normalization",
                text="Normalization",
                icon=('CHECKBOX_HLT' if track_active.use_normalization else 'CHECKBOX_DEHLT')
                )
            pie.prop(
                track_active,
                "use_brute",
                text="Use Brute Force",
                icon=('CHECKBOX_HLT' if track_active.use_brute else 'CHECKBOX_DEHLT')
                )
            pie.prop(
                track_active,
                "use_blue_channel",
                text="Blue Channel",
                icon=('CHECKBOX_HLT' if track_active.use_blue_channel else 'CHECKBOX_DEHLT')
                )

            if track_active.pattern_match == "PREV_FRAME":
                prop = pie.operator("wm.context_set_enum", text="Match Previous", icon='KEYINGSET')
                prop.data_path = "space_data.clip.tracking.tracks.active.pattern_match"
                prop.value = 'KEYFRAME'
            else:
                prop = pie.operator("wm.context_set_enum", text="Match Keyframe", icon='KEY_HLT')
                prop.data_pat = "space_data.clip.tracking.tracks.active.pattern_match"
                prop.value = 'PREV_FRAME'


class CLIP_PIE_tracking_pie(Menu):
    # Tracking Operators
    bl_label = "Tracking"
    bl_idname = "clip.tracking_pie"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        prop = pie.operator("clip.track_markers", icon='PLAY_REVERSE')
        prop.backwards = True
        prop.sequence = True
        prop = pie.operator("clip.track_markers", icon='PLAY')
        prop.backwards = False
        prop.sequence = True

        pie.operator("clip.disable_markers", icon='RESTRICT_VIEW_ON')
        pie.operator("clip.detect_features", icon='ZOOM_SELECTED')

        pie.operator("clip.clear_track_path", icon='BACK').action = 'UPTO'
        pie.operator("clip.clear_track_path", icon='FORWARD').action = 'REMAINED'

        pie.operator("clip.refine_markers", icon='LOOP_BACK').backwards = True
        pie.operator("clip.refine_markers", icon='LOOP_FORWARDS').backwards = False



class CLIP_PIE_clipsetup_pie(Menu):
    # Setup the clip display options
    bl_label = "Clip and Display Setup"
    bl_idname = "clip.clipsetup_pie"

    def draw(self, context):
        space = context.space_data
        clip = context.space_data.clip

        layout = self.layout
        pie = layout.menu_pie()

        pie.operator("clip.reload", text="Reload Footage", icon='FILE_REFRESH')
        pie.operator("clip.prefetch", text="Prefetch Footage", icon='LOOP_FORWARDS')

        pie.prop(space, "use_mute_footage", text="Mute Footage", icon='MUTE_IPO_ON')
        pie.prop(
            space.clip_user,
            "use_render_undistorted",
            text="Render Undistorted",
            icon=('CHECKBOX_HLT' if space.clip_user.use_render_undistorted else 'CHECKBOX_DEHLT')
            )
        pie.operator("clip.set_scene_frames", text="Set Scene Frames", icon='SCENE_DATA')
        pie.operator("wm.call_menu_pie", text="Marker Display", icon='PLUS').name = "CLIP_PIE_display_pie"
        pie.operator("clip.set_active_clip", icon='CLIP')
        pie.operator("wm.call_menu_pie", text="Proxy", icon='PLUS').name = "CLIP_PIE_proxy_pie"



class CLIP_PIE_solver_pie(Menu):
    # Operators to solve the scene
    bl_label = "Solving"
    bl_idname = "clip.solver_pie"

    def draw(self, context):
        space = context.space_data
        clip = context.space_data.clip
        settings = clip.tracking.settings

        layout = self.layout
        pie = layout.menu_pie()

        pie.operator("clip.create_plane_track", icon='MESH_PLANE')
        pie.operator("clip.solve_camera", text="Solve Camera", icon='OUTLINER_OB_CAMERA')

        pie.operator("wm.call_menu_pie", text="Refinement", icon='CAMERA_DATA').name = "CLIP_PIE_refine_pie"
        pie.prop(
            settings,
            "use_tripod_solver",
            text="Tripod Solver",
            icon=('RESTRICT_RENDER_OFF' if settings.use_tripod_solver else 'RESTRICT_RENDER_ON')
            )

        pie.operator("clip.set_solver_keyframe", text="Set Keyframe A", icon='KEY_HLT').keyframe = 'KEYFRAME_A'
        pie.operator("clip.set_solver_keyframe", text="Set Keyframe B", icon='KEY_HLT').keyframe = 'KEYFRAME_B'

        prop = pie.operator("clip.clean_tracks", icon='STICKY_UVS_DISABLE')
        pie.operator("clip.filter_tracks", icon='FILTER')
        prop.frames = 15
        prop.error = 2


class CLIP_PIE_reconstruction_pie(Menu):
    # Scene Reconstruction
    bl_label = "Reconstruction"
    bl_idname = "clip.reconstruction_pie"

    def draw(self, context):
        clip = context.space_data.clip
        settings = clip.tracking.settings

        layout = self.layout
        pie = layout.menu_pie()

        pie.operator("clip.set_viewport_background", text="Set Viewport Background", icon='SCENE_DATA')
        pie.operator("clip.setup_tracking_scene", text="Setup Tracking Scene", icon='SCENE_DATA')

        pie.operator("clip.set_plane", text="Setup Floor", icon='MESH_PLANE')
        pie.operator("clip.set_origin", text="Set Origin", icon='MANIPUL')

        pie.operator("clip.set_axis", text="Set X Axis", icon='AXIS_FRONT').axis = "X"
        pie.operator("clip.set_axis", text="Set Y Axis", icon='AXIS_SIDE').axis = "Y"

        pie.operator("clip.set_scale", text="Set Scale", icon='ARROW_LEFTRIGHT')
        pie.operator("wm.call_menu_pie", text="Reconstruction", icon='MESH_DATA').name = "CLIP_PIE_geometry_reconstruction"


class CLIP_PIE_timecontrol_pie(Menu):
    # Time Controls
    bl_label = "Time Control"
    bl_idname = "clip.timecontrol_pie"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        pie.operator("screen.frame_jump", text="Jump to Startframe", icon='TRIA_LEFT').end = False
        pie.operator("screen.frame_jump", text="Jump to Endframe", icon='TRIA_RIGHT').end = True

        pie.operator("clip.frame_jump", text="Start of Track", icon='REW').position = "PATHSTART"
        pie.operator("clip.frame_jump", text="End of Track", icon='FF').position = "PATHEND"

        pie.operator("screen.animation_play", text="Playback Backwards", icon='PLAY_REVERSE').reverse = True
        pie.operator("screen.animation_play", text="Playback Forwards", icon='PLAY').reverse = False

        pie.operator("screen.frame_offset", text="Previous Frame", icon='TRIA_LEFT').delta =- 1
        pie.operator("screen.frame_offset", text="Next Frame", icon='TRIA_RIGHT').delta = 1





########## register ############

classes = (
    CLIP_OT_set_active_clip,
    CLIP_OT_filter_tracks,
    CLIP_OT_track_settings_to_track,
    CLIP_PIE_geometry_reconstruction,
    CLIP_PIE_tracking_pie,
    CLIP_PIE_display_pie,
    CLIP_PIE_proxy_pie,
    CLIP_PIE_marker_pie,
    CLIP_PIE_solver_pie,
    CLIP_PIE_refine_pie,
    CLIP_PIE_reconstruction_pie,
    CLIP_PIE_clipsetup_pie,
    CLIP_PIE_timecontrol_pie,
    )
    


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name='Clip', space_type='CLIP_EDITOR')
    kmi = km.keymap_items.new('wm.call_menu_pie', 'Q', 'PRESS').properties.name = "clip.marker_pie"
    kmi = km.keymap_items.new('wm.call_menu_pie', 'W', 'PRESS').properties.name = "clip.clipsetup_pie"
    kmi = km.keymap_items.new('wm.call_menu_pie', 'E', 'PRESS').properties.name = "clip.tracking_pie"
    kmi = km.keymap_items.new('wm.call_menu_pie', 'S', 'PRESS', shift=True).properties.name = "clip.solver_pie"
    kmi = km.keymap_items.new('wm.call_menu_pie', 'W', 'PRESS', shift=True).properties.name = "clip.reconstruction_pie"

    km = wm.keyconfigs.addon.keymaps.new(name='Frames')
    kmi = km.keymap_items.new('wm.call_menu_pie', 'A', 'PRESS', oskey=True).properties.name = "clip.timecontrol_pie"


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
