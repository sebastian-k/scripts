bl_info = {
"name": "Main Settings",
"author": "Sebastian Koenig",
"version": (1, 0),
"blender": (2, 7, 4),
"category": "Scene"}






import bpy



def border_camera(context):
    render = context.scene.render
    if render.use_border:
        render.use_border = False

    else:
        render.use_border = True
        render.border_min_x = 0
        render.border_min_y = 0
        render.border_max_x = 1
        render.border_max_y = 1

class Prop_OT_toggle_camborder(bpy.types.Operator):
    bl_idname = "scene.toggle_camborder"
    bl_label = "Toggle Camera Border"

    def execute(self, context):

        border_camera(context)

        return {'FINISHED'} 

class VIEW3D_PT_viewport_controls(bpy.types.Panel):
    bl_idname = "scene.viewport_controls"
    bl_label = "Viewport Controls"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):
        layout = self.layout

        scene = context.scene
        view = context.space_data

        ob = context.active_object
       
        row = layout.row()
        row.label(text="", icon='OBJECT_DATA')
        if ob:
            row.prop(ob, "name", text="")
            if ob.type == 'ARMATURE' and ob.mode in {'EDIT', 'POSE'}:
                bone = context.active_bone
                if bone:
                    row = layout.row()
                    row.label(text="", icon='BONE_DATA')
                    row.prop(bone, "name", text="")
               
        col = layout.column()
        col.prop(context.user_preferences.view, "use_rotate_around_active")
        col.prop(view, "show_only_render")

        row = layout.row(align=True)
        row.prop(view, "show_floor", text="Grid")
        row.prop(view, "show_relationship_lines")
        col.prop(view, "show_background_images", text="Background Images")
        row = layout.row(align=True)
        if view.viewport_shade not in {'BOUNDBOX', 'WIREFRAME'}:
            row.prop(view.fx_settings, "use_ssao", text="AO")
        if view.viewport_shade == 'SOLID':
            row.prop(view, "show_textured_solid", text="Texture")

        row = layout.row(align=True)
        row.operator("view3d.view_all")
        row.operator("view3d.view_selected")

        
        
      




class PROP_PT_main_settings(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "Main Settings"
    bl_idname = "RENDER_PT_main_settings"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"

    def draw(self, context):
        layout = self.layout

        scene = context.scene
        render = scene.render

        row = layout.row(align=True)
        if render.use_border:
            row.operator("scene.toggle_camborder", icon="RENDER_REGION")
        else:
            row.operator("scene.toggle_camborder", icon="RESTRICT_RENDER_OFF")

        # Create a simple row.
        layout.label(text="Basic Settings:")

        row = layout.row()
        row.prop(scene.cycles, "film_transparent")
        row.prop(render, "use_simplify")
        row = layout.row()
        row.prop(scene.cycles, "debug_use_spatial_splits")
        

        row = layout.row()
        row.prop(render, "resolution_percentage")



        sub = row.column(align=True)
        sub.prop(scene.cycles, "device", text="")
        sub.prop(render, "tile_x", text="X")
        sub.prop(render, "tile_y", text="Y")


        layout.label(text="VR Settings:")

        row = layout.row()
        row.prop(render, "use_multiview")
        row.prop(scene.cube_map, "use_cube_map")


        


def register():
    bpy.utils.register_class(PROP_PT_main_settings)
    bpy.utils.register_class(Prop_OT_toggle_camborder)
    bpy.utils.register_class(VIEW3D_PT_viewport_controls)


def unregister():
    bpy.utils.unregister_class(PROP_PT_main_settings)
    bpy.utils.unregister_class(Prop_OT_toggle_camborder)
    bpy.utils.unregister_class(VIEW3D_PT_viewport_controls)


if __name__ == "__main__":
    register()

