import bpy

def mask_list(self, context):
    return [(m.name) for m in bpy.data.masks]

class NODE_OT_MaskList(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "nodes.list_masks"
    bl_label = "Mask Master"
    bl_options = {'REGISTER', 'UNDO'}

    mask = bpy.props.EnumProperty(items=mask_list)

    

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.prop(self, "mask", expand=True)

    def execute(self, context):
        self.report({'INFO'}, self.mask)
        return {'FINISHED'}


def register():
    bpy.utils.register_class(NODE_OT_MaskList)


def unregister():
    bpy.utils.unregister_class(NODE_OT_MaskList)


if __name__ == "__main__":
    register()