import bpy

# material switching from cycles to blender


mat_list=[]

def switch_materials(current_material, target_material, context):
    current_mat_list=[]
    target_mat_list=[]
    missing_mat_list=[]
    for mat in bpy.data.materials:
        if current_material in mat.name:
            current_mat_list.append(mat.name)
        elif target_material in mat.name:
            target_mat_list.append(mat.name)

    for ob in bpy.data.objects:
        if ob.type =="MESH":
            for slot in ob.material_slots:
                mat = slot.material
                if mat.name in current_mat_list:
                    new_mat = mat.name.replace(current_material, target_material)
                    if new_mat in target_mat_list:
                        slot.material = bpy.data.materials[new_mat]
                    else:
                        missing_mat_list.append(mat.name)
    print("missing materials:", missing_mat_list)
    return missing_mat_list

            
            
class VIEW3D_OT_material_switcher(bpy.types.Operator):
    bl_idname="object.material_switcher"
    bl_label="Material Switcher"

    def execute(self, context):
        scene = bpy.context.scene
        missing=switch_materials(scene.current_material, scene.target_material, context)
        self.report({"INFO"}, "There are %d materials missing, look in console for more" % len(missing))
        return {'FINISHED'}


class VIEW3D_PT_material_switcher(bpy.types.Panel):
    bl_idname = "object.material_switcher_panel"
    bl_label = "Material Switcher"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.operator("object.material_switcher")
        layout.prop(scene, "current_material")
        layout.prop(scene, "target_material")



def register():
    bpy.utils.register_class(VIEW3D_OT_material_switcher)
    bpy.utils.register_class(VIEW3D_PT_material_switcher)
    bpy.types.Scene.current_material = bpy.props.StringProperty \
    (
        name = "Current Material",
        description = "Which material to replace",
    )
    bpy.types.Scene.target_material = bpy.props.StringProperty \
    (
        name = "Target Material",
        description = "Material to be replaced",
    )



def unregister():
    bpy.utils.unregister_class(VIEW3D_OT_material_switcher)
    bpy.utils.unregister_class(VIEW3D_PT_material_switcher)


if __name__ == "__main__":
    register()