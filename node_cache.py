import bpy

# mark node --> add file output and image sequence node
# check folder, if image exists, mute file output node

scene =  bpy.context.scene

def my_handler(scene):
    print("Frame Change", scene.frame_current)

bpy.app.handlers.frame_change_pre.append(my_handler)

def add_nodes(my_node, context, state, path):

    tree = context.scene.node_tree
    links = tree.links

    if state == 1:

        cache_in = tree.nodes.new(type="CompositorNodeOutputFile")
        cache_in.location = my_node.location[0] + 100, my_node.location[1] + 100
        cache_in.base_path = path

        cache_out = tree.nodes.new(type="CompositorNodeImage")
        cache_out.location = my_node.location[0]-100, my_node.location[1] - 150

        switch = tree.nodes.new(type="CompositorNodeSwitch")
        switch.location=my_node.location[0]+300, my_node.location[1]+50  

        links.new(my_node.outputs[0], switch.inputs[0])
        links.new(cache_out.outputs[0], switch.inputs[1])
        links.new(my_node.outputs[0], cache_in.inputs[0])





class NODE_cacher(bpy.types.Operator):
    bl_idname = "node.cacher"
    bl_label = "Cacher" 


    @classmethod
    def poll(cls, context):
        space = context.space_data
        return space.type == 'NODE_EDITOR' and space.tree_type == 'CompositorNodeTree'


    def execute(self, context):
        my_node = bpy.context.scene.node_tree.nodes.active
        path = "/tmp/test/test"
        add_nodes(my_node, context, 1)        
        return {'FINISHED'}


########## REGISTER ############

def register():
    bpy.utils.register_class(NODE_cacher)



def unregister():

    bpy.utils.unregister_class(NODE_cacher)

if __name__ == "__main__":
    register()