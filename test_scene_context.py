import bpy


def testcreator():
    hashes = [hash(scene) for scene in bpy.data.scenes]
    old = bpy.context.scene.name
    bpy.ops.scene.new(type='NEW')
    scene = [scene for scene in bpy.data.scenes if hash(scene) not in hashes][0]
    new = scene.name
    print("old:", old)
    print("new:", new)


class VIEW3D_OT_scenetester(bpy.types.Operator):
    bl_idname = "scene.scenetester"
    bl_label = "Test scene"

    def execute(self, context):
        testcreator()
        return{'FINISHED'}



class VIEW3D_PT_scenetester(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "Test scene"
    bl_idname = "SCENE_PT_senetester"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # Create a simple row.
        col = layout.column()
        col.operator("scene.scenetester")

def register():
    bpy.utils.register_class(VIEW3D_OT_scenetester)
    bpy.utils.register_class(VIEW3D_PT_scenetester)



def unregister():
    bpy.utils.unregister_class(VIEW3D_OT_scenetester)
    bpy.utils.unregister_class(VIEW3D_PT_scenetester)



if __name__ == "__main__":
    register()
