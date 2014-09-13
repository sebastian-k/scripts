bl_info = {
    "name": "Snapping Pies",
    "author": "Sebastian Koenig",
    "version": (0, 1),
    "blender": (2, 71, 6),
    "description": "Custom Pie Menus",
    "category": "3D View",}




import bpy
from bpy.types import Menu



###### FUNTIONS ##########

def origin_to_selection(context):
    context = bpy.context

    if context.object.mode == "EDIT":
        bpy.ops.view3d.snap_cursor_to_selected()
        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')


########### CUSTOM OPERATORS ###############

#Menu Snap Target
class VIEW3D_OT_SnapTargetMenu(Menu):
    bl_idname = "snap.targetmenu"
    bl_label = "Snap Target Menu"

    def draw(self, context):
        layout = self.layout       
        
         
        layout.operator("object.snaptargetvariable", text="Active").variable='ACTIVE'
        layout.operator("object.snaptargetvariable", text="Median").variable='MEDIAN'
        layout.operator("object.snaptargetvariable", text="Center").variable='CENTER' 
        layout.operator("object.snaptargetvariable", text="Closest").variable='CLOSEST'



class VIEW3D_OT_origin_to_selected(bpy.types.Operator):
    bl_idname="object.origin_to_selected"
    bl_label="Origin to Selection"

    @classmethod
    def poll(cls, context):
        sc = context.space_data
        return (sc.type == 'VIEW_3D')

    def execute(self, context):
        origin_to_selection(context)
        return {'FINISHED'}



class VIEW3D_OT_lock_Z(bpy.types.Operator):
    bl_idname="object.origin_to_selected"
    bl_label="Origin to Selection"

    @classmethod
    def poll(cls, context):
        sc = context.space_data
        return (sc.type == 'VIEW_3D')

    def execute(self, context):
        origin_to_selection(context)
        return {'FINISHED'}

class VIEW3D_OT_origin_to_selected(bpy.types.Operator):
    bl_idname="object.origin_to_selected"
    bl_label="Origin to Selection"

    @classmethod
    def poll(cls, context):
        sc = context.space_data
        return (sc.type == 'VIEW_3D')

    def execute(self, context):
        origin_to_selection(context)
        return {'FINISHED'}

class VIEW3D_OT_origin_to_selected(bpy.types.Operator):
    bl_idname="object.origin_to_selected"
    bl_label="Origin to Selection"

    @classmethod
    def poll(cls, context):
        sc = context.space_data
        return (sc.type == 'VIEW_3D')

    def execute(self, context):
        origin_to_selection(context)
        return {'FINISHED'}


class VIEW3D_OT_SnapTargetVariable(bpy.types.Operator):
    bl_idname = "object.snaptargetvariable"
    bl_label = "Snap Target Variable"
    variable = bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        bpy.context.scene.tool_settings.snap_target=self.variable
        return {'FINISHED'} 



################### PIES #####################

class VIEW3D_PIE_origin(Menu):
    # label is displayed at the center of the pie menu.
    bl_label = "Origin"
    bl_idname = "object.snapping_pie"

    def draw(self, context):
        context = bpy.context
        layout = self.layout


        pie = layout.menu_pie()
        
        pie.operator("view3d.snap_selected_to_cursor", icon="CURSOR")
        pie.operator("view3d.snap_cursor_to_selected", icon="CLIPUV_HLT")

        if context.object.mode == "EDIT":
            pie.operator("object.origin_to_selected")
        else:
            pie.operator("object.origin_set",icon="EMPTY_DATA", text="Origin to Cursor").type="ORIGIN_CURSOR"


        op = pie.operator("wm.context_set_enum", text="Edge Snapping", icon="SNAP_EDGE")
        op.data_path="tool_settings.snap_element"
        op.value="EDGE"
        
        op = pie.operator("wm.context_set_enum", text="Vertex Snapping", icon="SNAP_VERTEX")
        op.data_path="tool_settings.snap_element"
        op.value="VERTEX"
        

        op = pie.operator("wm.context_set_enum", text="Face Snapping", icon="SNAP_FACE")
        op.data_path="tool_settings.snap_element"
        op.value="FACE"


        if context.scene.tool_settings.use_snap:
            pie.prop(context.scene.tool_settings, "use_snap", text="Use Snap(ON)")
        else:
            pie.prop(context.scene.tool_settings, "use_snap", text="Use Snap(OFF)")

        pie.menu("snap.targetmenu", text="Snap Target", icon='SNAP_SURFACE')
     

      


########## REGISTER ############

def register():
    bpy.utils.register_class(VIEW3D_PIE_origin)
    bpy.utils.register_class(VIEW3D_OT_origin_to_selected)
    bpy.utils.register_class(VIEW3D_OT_SnapTargetMenu)
    bpy.utils.register_class(VIEW3D_OT_SnapTargetVariable)
    

    wm = bpy.context.window_manager
    
    km = wm.keyconfigs.addon.keymaps.new(name='3D View', space_type="VIEW_3D")
    kmi = km.keymap_items.new('wm.call_menu_pie', 'C', 'PRESS').properties.name = "object.snapping_pie"





def unregister():
   
    bpy.utils.unregister_class(VIEW3D_PIE_origin)
    bpy.utils.unregister_class(VIEW3D_OT_origin_to_selected)
    bpy.utils.unregister_class(VIEW3D_OT_SnapTargetMenu)
    bpy.utils.unregister_class(VIEW3D_OT_SnapTargetVariable)


if __name__ == "__main__":
    register()
    #bpy.ops.wm.call_menu_pie(name="mesh.mesh_operators")
