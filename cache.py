import os
import bpy
from bpy.types import Panel, Operator, Menu
from bpy.props import *
from pathlib import Path


def save_viewer_node_on_framechange(dummy):
    context = bpy.context
    scn = context.scene
    frame = scn.frame_current
    path = Path(scn.cache_settings.cache_directory)
    cache_name = get_cache_name() + str(frame).zfill(4)
    filepath = (path / cache_name).with_suffix(".jpg")
    bpy.data.images['Viewer Node'].save_render(filepath=str(filepath))

def get_cache_name():
    blend_path = Path(bpy.context.blend_data.filepath)
    cache_name = blend_path.stem + "_cache"
    return cache_name

def has_viewer(context):
    viewer_node = False
    space = context.space_data
    if space.type  == 'NODE_EDITOR' and space.tree_type == 'CompositorNodeTree':
        if context.scene.use_nodes:
            try:
                viewer_node = space.node_tree.nodes.get('Viewer') is not None
            except:
                pass
    return viewer_node


class CACHE_OT_cache_show_cache(Operator):
    bl_idname = "scene.cache_show_cache"
    bl_label = "Show Cache"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return space.type == 'IMAGE_EDITOR'

    def execute(self, context):
        scn = context.scene
        space = context.space_data
        # make sure the handler is not running
        try:
            bpy.app.handlers.frame_change_pre.remove(save_viewer_node_on_framechange)
        except:
            self.report({'WARNING'}, "Viewer Node has not been recording")
        # set recording status to false if needed
        if scn.cache_settings.is_recording:
            scn.cache_settings.is_recording = False
            scn.node_tree.nodes.get('Viewer').use_custom_color = False
        # try to load the cache
        scn.use_nodes = False
        path = Path(scn.cache_settings.cache_directory)
        cache_name = get_cache_name()
        filepath = path / (cache_name + "0001.jpg")
        cache_img = bpy.data.images.get(cache_name)
        width = scn.render.resolution_x
        height = scn.render.resolution_y
        if not cache_img:
            cache_img = bpy.data.images.new(name=cache_name, width=width, height=height)
            cache_img.source = 'SEQUENCE'
            try:
                cache_img.filepath = str(filepath)
            except:
                print("cache could not be loaded", filepath)
        space.image = cache_img
        space.image_user.use_auto_refresh = True
        space.image_user.frame_offset = 0
        space.image_user.frame_start = scn.frame_start
        space.image_user.frame_duration = scn.frame_current

        return {'FINISHED'}


class CACHE_OT_use_compositor(Operator):
    bl_idname = "scene.cache_use_compositor"
    bl_label = "Use Compositor"

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return space.type == 'IMAGE_EDITOR'

    def execute(self, context):
        space = context.space_data
        space.image = bpy.data.images.get('Viewer Node')
        context.scene.use_nodes = True
        return {'FINISHED'}

class CACHE_OT_record_viewer(Operator):
    bl_idname = "scene.cache_record_viewer"
    bl_label = "Enable Node Cache"
    
    @classmethod
    def poll(cls, context):
        return has_viewer(context)

    def execute(self, context):
        scn = context.scene
        if not scn.cache_settings.is_recording:
            scn.use_nodes = True
            tree = scn.node_tree
            viewer = tree.nodes['Viewer']
            viewer.use_custom_color = True
            viewer.color = (0.0, 0.6, 0.0)
            append_function_unique(bpy.app.handlers.frame_change_pre, save_viewer_node_on_framechange)
            scn.cache_settings.is_recording = True
        else:
            self.report({'INFO'}, "Viewer Node is alreay recording")
        return {'FINISHED'}


class CACHE_PT_node_cache_control(Panel):
    bl_idname = "scene.cache_node_cache_control"
    bl_label = "Node Cache Control"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'

    def draw(self, context):
         layout = self.layout
         col = layout.column()
         col.prop(context.scene.cache_settings, "cache_directory")
         col.operator("scene.cache_record_viewer")


class CACHE_PIE_cache_controls(Menu):
    bl_label = "Cache Control"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        pie.operator("scene.cache_use_compositor")
        pie.operator("scene.cache_show_cache")


class CACHE_settings(bpy.types.PropertyGroup):
    cache_directory = StringProperty(
        name="Cache Directory",
        description="Where to store the cache",
        default="/tmp/",
        subtype='DIR_PATH'
    )
    is_recording = BoolProperty(
        name="Viewer Recording",
        description="Store whether the viewer node is being recorded",
        default=False
    )

classes = (
    CACHE_settings,
    CACHE_OT_cache_show_cache,
    CACHE_OT_record_viewer,
    CACHE_OT_use_compositor,
    CACHE_PIE_cache_controls,
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

addon_keymaps = []

def register():
    addon_keymaps.clear()
    for c in classes:
        bpy.utils.register_class(c)

    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name="Image", space_type='IMAGE_EDITOR')

    kmi = km.keymap_items.new('wm.call_menu_pie', 'C', 'PRESS')
    kmi.properties.name = "CACHE_PIE_cache_controls"
    addon_keymaps.append((km, kmi))


    bpy.types.Scene.cache_settings = PointerProperty(type=CACHE_settings)

def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.adodn
    if kc:
        for km, kmi in addon_keymaps:
            km.keymap_items.remove(kmi)
    addon_keymaps.clear()

if __name__ == "__main__":
    register()
