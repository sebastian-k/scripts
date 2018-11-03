import bpy


class UV_rotater(bpy.types.Operator):
    bl_idname = "mesh.uv_rotater"
    bl_label = "Rotate UVs 90"

    def execute(self, context):
        bpy.ops.uv.select_all(action='SELECT')
        bpy.ops.transform.rotate(value=1.5708, axis=(-0, -0, -1), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=0.00704012)
    
        return {'FINISHED'}


def register():
    bpy.utils.register_class(UV_rotater)

    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name='UV Editor', space_type='IMAGE_EDITOR')

    kmi = km.keymap_items.new('mesh.uv_rotater', 'U', 'PRESS')





def unregister():
    bpy.utils.unregister_class(UV_rotater)

if __name__ == "__main__":
    register()



