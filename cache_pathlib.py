import os
import bpy
from bpy.types import Panel, Operator
from bpy.props import *
from pathlib import Path


def save_viewer_node_on_framechange(dummy):
    context = bpy.context
    scn = context.scene
    path = Path(scn.cache_settings.cache_directory)
    frame = bpy.context.scene.frame_current
    cache_name = "cache_" + str(frame).zfill(4)
    filepath = path / cache_name.with_suffix("jpg")
    print(filepath)
    bpy.data.images['Viewer Node'].save_render(filepath=filepath)


class CACHE_OT_toggle_output(Operator):
    bl_idname = "scene.cache_toggle_output"
    bl_label = "Show Cache"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return space.type == 'IMAGE_EDITOR'

    def execute(self, context):
        bpy.app.handlers.frame_change_pre.remove(save_viewer_node_on_framechange)
        scn = context.scene
        scn.use_nodes = False
        path = scn.cache_settings.cache_directory
        filepath = os.path.join(path, "cache_0001.jpg")
        img = bpy.data.images.load(filepath)
        img.source = 'SEQUENCE'
        space = context.space_data
        space.image = img
        space.image_user.use_auto_refresh = True
        space.image_user.frame_duration = scn.frame_end

        return {'FINISHED'}

class CACHE_OT_node_cache_viewer(Operator):
    bl_idname = "scene.node_cache_viewer"
    bl_label = "Enable Node Cache"
    
    def execute(self, context):
        scn = context.scene
        scn.use_nodes = True
        tree = scn.node_tree
        viewer = tree.nodes['Viewer']
        viewer.use_custom_color = True
        viewer.color = (0.0, 0.6, 0.0)
        append_function_unique(bpy.app.handlers.frame_change_pre, save_viewer_node_on_framechange)
        # bpy.app.handlers.frame_change_pre.append(save_viewer_node_on_framechange)
        return {'FINISHED'}


class CACHE_PT_node_cache_control(Panel):
    bl_idname = "scene.node_cache_control"
    bl_label = "Node Cache Control"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'

    def draw(self, context):
         layout = self.layout
         col = layout.column()
         col.prop(context.scene.cache_settings, "cache_directory")


class CACHE_settings(bpy.types.PropertyGroup):
    cache_directory = StringProperty(
        name="Cache Directory",
        description="Where to store the cache",
        default="/tmp/",
        subtype='DIR_PATH'
    )

classes = (
    CACHE_settings,
    CACHE_OT_toggle_output,
    CACHE_OT_node_cache_viewer,
    CACHE_PT_node_cache_control
)

# trying to avoid having mulitple handlers
def append_function_unique(fn_list, fn):
    """ Appending 'fn' to 'f_list',
        Remove any funtions form with a mathcin name & module.
    """
    fn_name = fn.__module__
    for i in range(len(fn_list) -1, -1, -1):
        if fn_list[i].__name__ == fn_name and fn_list[i].__module__ == fn_module:
            del fn_list[i]
    fn_list.append(fn)


def register():
    for c in classes:
        bpy.utils.register_class(c)

    bpy.types.Scene.cache_settings = PointerProperty(type=CACHE_settings)

def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)

if __name__ == "__main__":
    register()
