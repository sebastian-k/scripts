import bpy
from bpy.props import (BoolProperty, EnumProperty,
                       FloatProperty, FloatVectorProperty,
                       IntProperty, StringProperty)

def init_properties():
    scene = bpy.types.Scene

    scene.rc_final_resolution = IntProperty(
        default=100,
        name="Final Resolution")

    scene.rc_fps = IntProperty(
        default=25,
        name="Frames per second")

    scene.rc_simplify = BoolProperty(
        default=0,
        name="Use Simplification")

def clear_properties():
    props = (
        "rc_final_resolution",
        "rc_simplify"
    )
    
    wm = bpy.context.window_manager
    for p in props:
        if p in wm:
            del wm[p] 




class OP_save_renderconfig(bpy.types.Operator):
    bl_idname = "scene.save_renderconfig"
    bl_label = "Save Render Config"

    def execute(self, context):
        scene = context.scene
        render = scene.render

        scene.rc_final_resolution = render.resolution_percentage

        
        return {'FINISHED'}




class OP_load_renderconfig(bpy.types.Operator):
    bl_idname = "scene.load_renderconfig"
    bl_label = "load Render Config"

    def execute(self, context):

        print(renderconfig)
        '''
        render = context.scene.render

        render.resolution_x = renderconfig["dim_x"]
        render.resolution_y = renderconfig["dim_y"]
        render.resolution_percentage = renderconfig["dim_res"]
        '''
        return {'FINISHED'}




class PROP_renderconfig(bpy.types.Panel):
    bl_idname = "scene.renderconfig"
    bl_label = "Render Config"  
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"

    def draw(self, context):
        layout = self.layout

        scene = context.scene
        render = scene.render

        row=layout.row()
        row.operator("scene.save_renderconfig")
        row.operator("scene.load_renderconfig")
        row = layout.row()
        row.label(text="Settings:")
        col = layout.column()
        col.prop(render, "resolution_percentage", text="")
        col.prop(render, "use_border")
        col.prop(render, "use_simplify")
        col.prop(scene.cycles, "film_transparent")

########## REGISTER ############

def register():
    init_properties()

    bpy.utils.register_class(PROP_renderconfig)
    bpy.utils.register_class(OP_save_renderconfig)
    bpy.utils.register_class(OP_load_renderconfig)



def unregister():
    clear_properties()

    bpy.utils.unregister_class(PROP_renderconfig)
    bpy.utils.unregister_class(OP_save_renderconfig)
    bpy.utils.unregister_class(OP_load_renderconfig)

if __name__ == "__main__":
    register()