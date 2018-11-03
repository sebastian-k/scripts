import bpy

# def update():
# 	groups = []
# 	for index, group in enumerate(bpy.data.groups):
# 		groups.append((str(index), group.name, str(index)))
# 	bpy.types.Scene.EnumProperty(attr="grp_list", name="Groups", description="Choose a Group", items=groups, default='0')


def update():

    objects = [] #list containing tuples of each object
    for index, object in enumerate(bpy.context.scene.objects): #iterate over all objects
        objects.append((str(index), object.name, str(index))) #put each object in a tuple and add this to the objects list
 
    bpy.types.Scene.EnumProperty( attr="obj_list", name="Objects", description="Choose an object", items=objects, default='0')

class OBJECT_PT_SelectObjects(bpy.types.Panel):
    '''
    Class to represent a panel that allows you to browse and select objects.
    '''
    bl_space_type = "PROPERTIES" #window type where the panel will be displayed
    bl_region_type = "WINDOW"
    bl_context = "object" #where to show panel in space_type
    bl_label = "Select Object" #panel name displayed in header
 
    def draw(self, context):
        '''
        Function used by blender to draw the panel.
        '''
        update() #update obj_list
        scene = context.scene
        layout = self.layout
        layout.prop(scene, "obj_list", text="Objects") #draw dropdown box on panel
        layout.separator()
        row = layout.row()
        row.operator("selectObject_button") #draw select button on panel
        row = layout.row()
        row.label(text="Active object is: " + bpy.context.active_object.name) #display the name of the active object


class VIEW3D_group_menu(bpy.types.Menu):
	bl_label = "Group Menu"
	bl_idname = "OBJECT_MT_group_menu"

	def draw(self, context):
		layout = self.layout
		layout.operator("object.group_link")

class VIEW3D_group_master(bpy.types.Operator):
    bl_name = "object.group_master"
    bl_label = "Group Master"

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return (space.type == 'VIEW3D')

    def execute():
        print("hello")
        return {'FINISHED'}


def register():
	bpy.utils.register_class(VIEW3D_group_menu)
	bpy.utils.register_class(OBJECT_PT_SelectObjects)

def unregister():
	bpy.utils.unregister_class(VIEW3D_group_menu)
	bpy.utils.unregister_class(OBJECT_PT_SelectObjects)

if __name__ == "__main__":
	register()


