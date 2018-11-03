import bpy


def set_switch(context, bypass_node, start_node):
    print(bypass_node)
    print(start_node)

    tree = context.scene.node_tree
    links = tree.links

    # create the switch node
    switch = tree.nodes.new(type="CompositorNodeSwitch")
    switch.location=bypass_node.location[0]+300, bypass_node.location[1]+50  
    switch.label="Switch " +  bypass_node.name

    # find the target node
    if bypass_node.outputs[0].links:
        target = bypass_node.outputs[0].links[0].to_node
    else:
        target = None
    if bypass_node.inputs[0].links[0].from_node:
        source = bypass_node.inputs[0].links[0].from_node

    # create links
    if not start_node ==None:
        links.new(start_node.outputs[0], switch.inputs[0])
        links.new(bypass_node.outputs[0], switch.inputs[1])
    else: 
        links.new(source.outputs[0], switch.inputs[0])
        links.new(bypass_node.outputs[0], switch.inputs[1])
    if not target == None:
        links.new(switch.outputs[0], target.inputs[0])

    # only select the switch node
    for n in tree.nodes:
        n.select = False
    switch.select=True
    tree.nodes.active = switch


def node_switcher(context):
    tree = context.scene.node_tree

    # get the selected nodes
    nodes = []
    for n in tree.nodes:
        if n.select:
            nodes.append(n)

    # check if there is an active node and assign variable
    if tree.nodes.active:
        active = tree.nodes.active
    else:
        a = None

    # check how many nodes are selected. if more than 2 the script doesn't work
    if len(nodes)==2:
        for n in nodes:
            # assign a variable to the selected but not active node
            if not n==active:
                bypass_node = n
        start_node = active

        set_switch(context, bypass_node, start_node)
        
    # if there is only 1 node selected, bypass that one
    elif len(nodes)==1:
        for n in nodes:
            bypass_node = n
            start_node = None


        set_switch(context, bypass_node, start_node)
        

    else:
        print("wrong selection")

            

class NODE_node_switcher(bpy.types.Operator):
    bl_idname = "node.node_switcher"
    bl_label = "Switchy"

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return space.type == 'NODE_EDITOR' and space.tree_type == 'CompositorNodeTree'

    def execute(self, context):
        node_switcher(context)        
        return {'FINISHED'}



########## register ############



def register():
    bpy.utils.register_class(NODE_node_switcher)

    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name='Node Editor', space_type='NODE_EDITOR')

    kmi = km.keymap_items.new('node.node_switcher', 'S', 'PRESS', alt=True )



def unregister():
    bpy.utils.unregister_class(NODE_node_switcher)


if __name__ == "__main__":
    register()

