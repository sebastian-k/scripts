bl_info = {
    "name": "Plane Track Comp Setup",
    "author": "Sebastian Koenig",
    "version": (1, 0),
    "blender": (3, 3, 0),
    "location": "Clip Editor",
    "description": "Setup Node Setup for Plane Track Image",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Clip Editor"
}

import bpy
from mathutils import Vector


def CLIP_spaces_walk(context, all_screens, tarea, tspace, callback, *args):
    screens = bpy.data.screens if all_screens else [context.screen]

    for screen in screens:
        for area in screen.areas:
            if area.type == tarea:
                for space in area.spaces:
                    if space.type == tspace:
                        callback(space, *args)


class CLIP_OT_PlaneTrackSetup(bpy.types.Operator):
    """Create a Plane Track Setup in the Compositor"""
    bl_idname = "clip.plane_track_setup"
    bl_label = "Plane Track Setup"

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return space.type == 'CLIP_EDITOR'

    @staticmethod
    def _findNode(tree, type):
        for node in tree.nodes:
            if node.type == type:
                return node
        return None

    @staticmethod
    def _findOrCreateNode(tree, type):
        node = CLIP_OT_PlaneTrackSetup._findNode(tree, type)

        if not node:
            node = tree.nodes.new(type=type)
        return node

    def _setup_plane_track_nodes(self, tree, clip):

        #create image and planetrack node
        planetrack = tree.nodes.new(type='CompositorNodePlaneTrackDeform')
        image = tree.nodes.new(type='CompositorNodeImage')

        # set their properties
        planetrack.clip = clip
        planetrack.tracking_object = clip.tracking.objects.active.name
        planetrack.plane_track_name = clip.tracking.plane_tracks.active.name
        image.image = clip.tracking.plane_tracks.active.image

        # setup links
        tree.links.new(image.outputs[0], planetrack.inputs[0])

        # arrange nodes
        image.location = planetrack.location
        image.location += Vector((-400, 0.0))

        # return image and planetrack so we can use them in _setupNodes
        return (image, planetrack)

    def _setupNodes(self, context, clip):
        scene = context.scene
        scene.use_nodes = True
        tree = scene.node_tree

        # Enable backdrop for all compositor spaces
        def setup_space(space):
            space.show_backdrop = True

        CLIP_spaces_walk(context, True, 'NODE_EDITOR', 'NODE_EDITOR', setup_space)

        # create nodes
        composite = self._findOrCreateNode(tree, 'CompositorNodeComposite')
        viewer = tree.nodes.new(type='CompositorNodeViewer')
        # scale = tree.nodes.new(type='CompositorNodeScale')
        movieclip = tree.nodes.new(type='CompositorNodeMovieClip')
        alphaover = tree.nodes.new(type='CompositorNodeAlphaOver')

        # create planetrack nodes
        planetracknodes = self._setup_plane_track_nodes(tree, clip)
        image = planetracknodes[0]
        planetrack = planetracknodes[1]

        tree.links.new(movieclip.outputs["Image"], alphaover.inputs[1])
        tree.links.new(planetrack.outputs[0], alphaover.inputs[2])
        tree.links.new(alphaover.outputs[0], composite.inputs[0])
        tree.links.new(alphaover.outputs[0], viewer.inputs[0])

        movieclip.clip = clip

        alphaover.location = movieclip.location
        alphaover.location += Vector((300.0, 0.0))

        planetrack.location = movieclip.location
        planetrack.location += Vector((0.0, -400.0))

        composite.location = alphaover.location
        composite.location += Vector((800.0, 0.0))

        viewer.location = composite.location
        composite.location += Vector((0.0, 200.0))

    def execute(self, context):
        sc = context.space_data
        clip = sc.clip
        scene = context.scene
        tree = scene.node_tree

        if not tree or len(tree.nodes) == 0:
            # No compositor node tree found, time to create it!
            print(len(tree.nodes))
            self._setupNodes(context, clip)
        else:
            # see if there already is a planetrack setup
            planetracks = 0
            for node in tree.nodes:
                if node.type in {'PLANETRACKDEFORM'}:
                    planetracks += 1

            # no planetrack found, create image and planetrack
            if not planetracks:
                self._setup_plane_track_nodes(tree, clip)

        return {'FINISHED'}


########## REGISTER ############


def register():
    bpy.utils.register_class(CLIP_OT_PlaneTrackSetup)

    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name='Clip', space_type='CLIP_EDITOR')
    kmi = km.keymap_items.new('clip.plane_track_setup', 'J', 'PRESS')


def unregister():

    bpy.utils.unregister_class(CLIP_OT_PlaneTrackSetup)


if __name__ == "__main__":
    register()
