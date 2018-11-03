import bpy

def set_active_clip(context):

    clip = context.space_data.clip
    scene = context.scene

    scene.active_clip = clip
    scene.render.resolution_x = clip.size[0]
    scene.render.resolution_y = clip.size[1]



class CLIP_set_active_clip(bpy.types.Operator):
    bl_idname = "clip.set_active_clip"
    bl_label = "Set Active Clip"

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return space.type == 'CLIP_EDITOR'

    def execute(self, context):
        set_active_clip(context)
        return {'FINISHED'}


########## REGISTER ############

def register():
    bpy.utils.register_class(CLIP_set_active_clip)



def unregister():

    bpy.utils.unregister_class(CLIP_set_active_clip)

if __name__ == "__main__":
    register()