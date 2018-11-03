bl_info = {
"name": "Maskerade",
"author": "Sebastian Koenig",
"version": (1, 2),
"blender": (2, 7, 2),
"location": "Clip Editor > Maskerade",
"description": "Pie and Node Controls for Masking",
"warning": "",
"wiki_url": "",
"tracker_url": "",
"category": "Compositing"}



import bpy
from bpy.types import Menu
from mathutils import Vector

########## Setup Scene ##############

def CLIP_spaces_walk(context, all_screens, tarea, tspace, callback, *args):
    screens = bpy.data.screens if all_screens else [context.screen]

    for screen in screens:
        for area in screen.areas:
            if area.type == tarea:
                for space in area.spaces:
                    if space.type == tspace:
                        callback(space, *args)



class MASK_OT_setup_masking_scene(bpy.types.Operator):
    """docstring for MASK_OT_setup_masking_scene"""
    bl_label = "Setup Masking Scene"
    bl_idname = "mask.setup_masking_scene"


    @classmethod
    def poll(cls, context):
        sc = context.space_data

        if sc.type != 'CLIP_EDITOR':
            return False
        return sc.clip 

    @staticmethod
    def _findNode(tree, type):
        for node in tree.nodes:
            if node.type == type:
                return node
        return None

    @staticmethod
    def _findOrCreateNode(tree, type):
        node = MASK_OT_setup_masking_scene._findNode(tree, type)

        if not node:
            node = tree.nodes.new(type=type)
        return node
    

    @staticmethod
    def _needSetupNodes(context):
        scene = context.scene
        tree = scene.node_tree

        if not tree:
            # No compositor node tree found, time to create it!
            return True

        for node in tree.nodes:
            if node.type in {'MOVIECLIP'}:
                return False

        return True
   

    @staticmethod
    def _wipeDefaultNodes(tree):
        if len(tree.nodes) != 2:
            return False
        types = [node.type for node in tree.nodes]
        types.sort()

        if types[0] == 'COMPOSITE' and types[1] == 'R_LAYERS':
            while tree.nodes:
                tree.nodes.remove(tree.nodes[0])


    def _setupNodes(self, context):
        if not self._needSetupNodes(context):
            # compositor nodes were already setup or even changes already
            # do nothing to prevent nodes damage
            return

        # Enable backdrop for all compositor spaces
        def setup_space(space):
            space.show_backdrop = True

        CLIP_spaces_walk(context, True, 'NODE_EDITOR', 'NODE_EDITOR',
                         setup_space)

        sc = context.space_data
        scene = context.scene
        scene.use_nodes = True
        tree = scene.node_tree
        clip = sc.clip


        # Remove all the nodes if they came from default node setup.
        # This is simplest way to make it so final node setup is
        # is correct.
        self._wipeDefaultNodes(tree)

        # create nodes
        composite = self._findOrCreateNode(tree, 'CompositorNodeComposite')
        viewer = tree.nodes.new(type='CompositorNodeViewer')
        scale = tree.nodes.new(type='CompositorNodeScale')
        movieclip = tree.nodes.new(type='CompositorNodeMovieClip')

        tree.links.new(movieclip.outputs["Image"], scale.inputs["Image"])
        tree.links.new(scale.outputs[0], composite.inputs[0])
        tree.links.new(scale.outputs[0], viewer.inputs[0])

        movieclip.clip = clip
        scale.space = 'RENDER_SIZE'

        scale.location = movieclip.location
        scale.location += Vector((200, 0.0))

        composite.location = scale.location
        composite.location += Vector((800.0, 0.0))

        viewer.location = composite.location
        composite.location += Vector((0.0, 200.0))



    def execute(self, context):
        scene = context.scene
        current_active_layer = scene.active_layer

        self._setupNodes(context)

        return {'FINISHED'}


############### FUNCTIONS MASKERADE  ##########################

def select_mask():
    # Select the mask in the Image Editor and set Viewer Node

    active_node = bpy.context.scene.node_tree.nodes.active 

    # check whether the active node is a mask
    if active_node.type == 'MASK':
        the_mask = active_node.mask

        # set the correct mode in image and clip editor to the mask 
        set_mask_mode(the_mask)



def set_mask_mode(mask):
    # Set the Mask mode in image and clip editor

    context = bpy.context
    active_node = context.scene.node_tree.nodes.active 

    # find image or movie editor
    for area in context.screen.areas: 
        active_space = area.spaces.active

        # set mode to mask and select the mask    
        if area.type == 'IMAGE_EDITOR' or area.type == 'CLIP_EDITOR': 
            active_space.mode = 'MASK' 
            active_space.mask = mask

        # if it's the image editor, assign the viewer node if possible    
        elif area.type == 'IMAGE_EDITOR':
            if bpy.data.images["Viewer Node"]:
                active_space.image = bpy.data.images["Viewer Node"]

def set_image_viewer():
    # make the viewer node active in editor

    context = bpy.context
    for area in context.screen.areas:
        active_space = area.spaces.active

        if area.type == 'IMAGE_EDITOR':
            if bpy.data.images['Viewer Node']:
                area.spaces.active.image = bpy.data.images['Viewer Node']


def add_mask_node(the_mask):
    # Add a mask node, connect it to active node 

    context = bpy.context
    scene = context.scene
    if scene.node_tree:
        tree = scene.node_tree
        links = tree.links
    
        # link the viewer to the active node 
        active_node = tree.nodes.active
        bpy.ops.node.link_viewer()
        tree.nodes.active = active_node # TODO: figure out why I did this...

        # create a new mask node and link mask to factor input (if that exists)
        my_mask = tree.nodes.new(type="CompositorNodeMask")
        my_mask.location = active_node.location[0]-200, active_node.location[1]+100
        if 'Fac' in active_node.inputs:
            links.new(my_mask.outputs[0], active_node.inputs['Fac'])
        my_mask.use_antialiasing = True
        
        # assing the mask from image editor 
        my_mask.mask = the_mask



def add_mask():
    # Add the mask in Clip or Image Editor, and set the Viewer Node if possible

    active_node = bpy.context.scene.node_tree.nodes.active

    # see if the active node has an input and output at all
    if 'Image' in active_node.inputs and 'Image' in active_node.outputs:

        #create a new mask 
        new_mask = bpy.data.masks.new()

        #call the function to set mask mode in image and clip editor
        set_mask_mode(new_mask)
              
        # finally create a new mask node with the current mask as input
        add_mask_node(new_mask)

   


################ CLASSES MASKERADE #################




class NODE_OT_select_mask(bpy.types.Operator):
    bl_idname = "node.select_mask"
    bl_label = "Select Mask"

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return space.type == 'NODE_EDITOR' and space.tree_type == 'CompositorNodeTree'

    def execute(self, context):
        select_mask()
        return {'FINISHED'}



class NODE_OT_add_mask(bpy.types.Operator):
    bl_idname = "node.add_mask"
    bl_label = "Add Mask"

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return space.type == 'NODE_EDITOR' and space.tree_type == 'CompositorNodeTree'

    def execute(self, context):
        add_mask()        
        return {'FINISHED'}




class IMAGE_OT_set_viewer_node(bpy.types.Operator):
    bl_idname = "scene.set_image_viewer"
    bl_label = "Set Viewer Node"

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return space.type == 'IMAGE_EDITOR'

    def execute(self, context):
        set_image_viewer()
        return {'FINISHED'}





############### FUNCTIONS PIES ##########################


class MASK_OT_new_masklayer(bpy.types.Operator):
    bl_idname = "mask.new_masklayer"
    bl_label = "New Masklayer"

    def execute(self, context):
        active_layer = context.space_data.mask.layers.active
        if active_layer:
            active_layer.hide_select=True
        bpy.ops.mask.layer_new()      
        return {'FINISHED'}
        

class MASK_OT_set_to_add(bpy.types.Operator):
    bl_idname = "mask.set_to_add"
    bl_label = "Set Add"

    def execute(self, context):

        sc = context.space_data
        mask = sc.mask
        active_layer = mask.layers.active
        active_layer.blend="MERGE_ADD"
        return {'FINISHED'}


class MASK_OT_lock_inactive_layers(bpy.types.Operator):
    bl_idname = "mask.lock_inactive_layers"
    bl_label = "Lock Inactive Layers"

    def execute(self, context):

        mask = context.space_data.mask
        active_layer = mask.layers.active
        for ml in mask.layers:
            ml.hide_select=True
        active_layer.hide_select=False
        return {'FINISHED'}


class MASK_OT_hide_inactive_layers(bpy.types.Operator):
    bl_idname = "mask.hide_inactive_layers"
    bl_label = "Hide Inactive Layers"

    def execute(self, context):

        mask = context.space_data.mask
        active_layer = mask.layers.active
        layers = []
        hidden = []
        # get all layers
        for ml in mask.layers:
            if ml != active_layer:
                layers.append(ml)
    
        for l in layers:
            if l:
                if l.hide:
                    hidden.append(l)
        if len(hidden) == len(layers):
            for l in hidden:
                l.hide = False
        else:
            for l in layers:
                l.hide = True
      
    
        return {'FINISHED'}


        
class MASK_OT_set_drawtype(bpy.types.Operator):
    bl_idname = "mask.set_drawtype"
    bl_label = "Draw Smooth"

    def execute(self, context):

        sc = context.space_data
        sc.show_mask_smooth = True
        sc.mask_draw_type = "WHITE"
        return {'FINISHED'}
        

class MASK_OT_set_marker_drawtype(bpy.types.Operator):
    bl_idname = "mask.set_marker_drawtype"
    bl_label = "Set Marker Drawtype"

    def execute(self, context):

        sc = context.space_data
        sc.show_marker_pattern = False
        sc.show_marker_search= False
        sc.show_track_path = False
        return {'FINISHED'}
        

class MASK_OT_switch_editor(bpy.types.Operator):
    bl_idname = "mask.switch_editor"
    bl_label = "Switch Editor"

    def execute(self, context):
        for area in context.screen.areas: 
            active_space = area.spaces.active
            if area.type == "CLIP_EDITOR":
                if context.scene.node_tree and context.scene.node_tree.nodes.get('Viewer'):
                    mask = active_space.mask
                    area.type = "IMAGE_EDITOR"
                    active_area = area.spaces.active
                    # this only works if a Viewer Node existsa
                    if bpy.data.images["Viewer Node"]:
                        active_area.image = bpy.data.images["Viewer Node"]
                    active_area.mode = "MASK"
                    active_area.mask = mask
                else:
                    self.report({"INFO"}, "You need a Viewer Node for this to work")

            elif area.type == "IMAGE_EDITOR":
                mask = active_space.mask
                area.type = "CLIP_EDITOR"
                active_area = area.spaces.active
                active_area.mode = "MASK"
                active_area.mask = mask

        return {'FINISHED'}
  

    
class MASK_OT_set_to_subtract(bpy.types.Operator):
    bl_idname = "mask.set_to_subtract"
    bl_label = "Set Subtract"

    def execute(self, context):

        sc = context.space_data
        mask = sc.mask
        active_layer = mask.layers.active
        active_layer.blend="MERGE_SUBTRACT"
        return {'FINISHED'}
        


class MASK_OT_clear_keyframes(bpy.types.Operator):
    bl_idname = "mask.clear_keyframes"
    bl_label = "Clear keyframes"

    def execute(self, context):
        scene = context.scene
        current_frame = scene.frame_current
        bpy.ops.mask.shape_key_insert()
        for f in range(current_frame+1, scene.frame_end+1):
            scene.frame_set(f)
            bpy.ops.mask.shape_key_clear()
        for f in range(scene.frame_start, current_frame-1):
            scene.frame_set(f)
            bpy.ops.mask.shape_key_clear()
        scene.frame_current = current_frame
        #bpy.ops.mask.shape_key_clear()
        return {'FINISHED'}
        






########### PIES ##################

class MASK_PIE_clear_animations(Menu):
    bl_label = "Clear Animations"

    def draw(self, context):
        layout = self.layout

        pie = layout.menu_pie()
        pie.operator("mask.clear_keyframes", icon='X')
        pie.operator("mask.shape_key_feather_reset", icon='ANIM')
        pie.operator("mask.feather_weight_clear", icon='X')


class MASK_PIE_handletype(Menu):
    bl_label = "Handle Type"

    def draw(self, context):
        layout = self.layout

        pie = layout.menu_pie()
        pie.operator_enum("MASK_OT_handle_type_set", "type")
       

class MASK_PIE_masklayers(Menu):
    bl_label = "Masking Pie"
    bl_idname = "clip.masklayer_pie"


    def draw(self, context):
        layout = self.layout
        tool_settings = bpy.context.scene.tool_settings

        pie = layout.menu_pie()
        pie.operator("mask.hide_inactive_layers", icon='RESTRICT_VIEW_OFF')
        pie.operator("mask.lock_inactive_layers", icon='LOCKED')
        
        pie.operator("mask.set_drawtype", icon='IPO_LINEAR') 
        pie.prop(context.space_data, "show_mask_overlay", text="Show Mask Overlay", icon ="IMAGE_ZDEPTH")
        
        pie.operator("mask.switch_editor", icon='CONSTRAINT')
        pie.operator("wm.call_menu_pie", text="Clear Animations", icon='PLUS').name = "MASK_PIE_clear_animations"
        
        if tool_settings.use_keyframe_insert_auto:
            pie.prop(bpy.context.scene.tool_settings, "use_keyframe_insert_auto",text="Disable Autokey (ON)")
        else:
            pie.prop(bpy.context.scene.tool_settings, "use_keyframe_insert_auto", icon="PROP_OFF", text="Enable Autokey (OFF)")
            


class MASK_PIE_mask_editing(Menu):
    bl_label = "Masking Pie"
    bl_idname = "clip.mask_editing_pie"

    def draw(self, context):
        layout = self.layout

        active_layer = context.space_data.mask.layers.active
        pie = layout.menu_pie()
        pie.operator("mask.set_to_add", icon='ZOOMIN')
        pie.operator("mask.set_to_subtract", icon='ZOOMOUT')
        pie.operator("mask.select_linked", icon="LINKED")
        pie.operator("mask.new_masklayer", icon='MESH_PLANE') 
        pie.operator("mask.cyclic_toggle", icon="CURVE_BEZCIRCLE")
        pie.operator("wm.call_menu_pie", text="Handle Type", icon='PLUS').name = "MASK_PIE_handletype"
        pie.operator("mask.switch_direction", icon="ARROW_LEFTRIGHT")

        pie.prop(active_layer, "invert", text="Invert Layer", icon='IMAGE_ALPHA')




class MASK_PIE_mask_access(Menu):
    bl_label = "Mask Access Pie"
    bl_idname = "clip.mask_access"

    def draw(self, context):
        layout = self.layout

        pie = layout.menu_pie()
        pie.operator("mask.switch_editor", icon='CONSTRAINT') 



      
      



########## register ############



def register():
    bpy.utils.register_class(MASK_OT_setup_masking_scene)
    bpy.utils.register_class(MASK_PIE_mask_editing)
    bpy.utils.register_class(MASK_PIE_masklayers)
    bpy.utils.register_class(MASK_PIE_mask_access)
    bpy.utils.register_class(MASK_PIE_clear_animations)
    bpy.utils.register_class(MASK_PIE_handletype)
    bpy.utils.register_class(MASK_OT_lock_inactive_layers)
    bpy.utils.register_class(MASK_OT_hide_inactive_layers)
    bpy.utils.register_class(MASK_OT_new_masklayer)
    bpy.utils.register_class(MASK_OT_set_to_subtract)
    bpy.utils.register_class(MASK_OT_set_to_add)
    bpy.utils.register_class(MASK_OT_set_drawtype)
    bpy.utils.register_class(MASK_OT_set_marker_drawtype)
    bpy.utils.register_class(MASK_OT_clear_keyframes)
    bpy.utils.register_class(MASK_OT_switch_editor)
    bpy.utils.register_class(NODE_OT_select_mask)
    bpy.utils.register_class(NODE_OT_add_mask)
    bpy.utils.register_class(IMAGE_OT_set_viewer_node)

    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name='Node Editor', space_type='NODE_EDITOR')
    kmi = km.keymap_items.new('node.select_mask', 'RIGHTMOUSE', 'DOUBLE_CLICK')
    kmi = km.keymap_items.new('node.add_mask', 'M', 'PRESS', ctrl=True )

    km = wm.keyconfigs.addon.keymaps.new(name='Mask Editing')
    kmi = km.keymap_items.new('wm.call_menu_pie', 'E', 'PRESS').properties.name = "clip.mask_editing_pie"
    kmi = km.keymap_items.new('wm.call_menu_pie', 'Q', 'PRESS').properties.name = "clip.masklayer_pie"

    km = wm.keyconfigs.addon.keymaps.new(name='Clip Editor')
    kmi = km.keymap_items.new('wm.call_menu_pie', 'W', 'PRESS').properties.name = "clip.mask_access"

    km = wm.keyconfigs.addon.keymaps.new(name='Image', space_type='IMAGE_EDITOR')
    kmi = km.keymap_items.new('scene.set_image_viewer', 'V', 'PRESS')





def unregister():
   
   
    bpy.utils.unregister_class(MASK_OT_setup_masking_scene)
    bpy.utils.unregister_class(MASK_PIE_masklayers)
    bpy.utils.unregister_class(MASK_PIE_mask_editing)
    bpy.utils.unregister_class(MASK_PIE_mask_access)
    bpy.utils.unregister_class(MASK_PIE_clear_animations)
    bpy.utils.unregister_class(MASK_PIE_handletype)
    bpy.utils.unregister_class(MASK_OT_lock_inactive_layers)
    bpy.utils.unregister_class(MASK_OT_hide_inactive_layers)
    bpy.utils.unregister_class(MASK_OT_new_masklayer)
    bpy.utils.unregister_class(MASK_OT_set_to_subtract)
    bpy.utils.unregister_class(MASK_OT_set_to_add)
    bpy.utils.unregister_class(MASK_OT_set_drawtype)
    bpy.utils.unregister_class(MASK_OT_set_marker_drawtype)
    bpy.utils.unregister_class(MASK_OT_clear_keyframes)
    bpy.utils.unregister_class(MASK_OT_switch_editor)
    bpy.utils.unregister_class(NODE_OT_select_mask)
    bpy.utils.unregister_class(NODE_OT_add_mask)
    bpy.utils.unregister_class(IMAGE_OT_set_viewer_node)


if __name__ == "__main__":
    register()


