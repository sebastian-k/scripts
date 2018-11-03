#mouse mover
import bpy

class NODE_OT_move_da_mouse(bpy.types.Operator):
    bl_idname="node.move_da_mouse"
    bl_label="Move da Mouse"

    x = bpy.props.IntProperty()
    y = bpy.props.IntProperty()

    @classmethod
    def poll(cls, context):
        sc = context.space_data
        return (sc.type == 'NODE_EDITOR')

    

    def invoke(self, context, event):
        tree = bpy.context.scene.node_tree
        nodes = tree.nodes

        self.x = event.mouse_region_x
        self.y = event.mouse_region_y

        origin = context.region.view2d.view_to_region(0,0, clip=True)
        print("origin= ", origin)

        rel_mouse_x = self.x - origin[0]
        print("mouse", rel_mouse_x)
        abs_mouse_x = context.region.view2d.region_to_view(self.x, 0)[0]
        print(abs_mouse_x)

        for n in nodes:
            nodex=int(n.location[0])
            if nodex > abs_mouse_x:
                print("node ", n, " : " , nodex, "rel_mouse_x", rel_mouse_x)        

                n.location[0] += 200

        return self.execute(context)

    def execute(self, context):
        return {'FINISHED'}

class NODE_OT_collapsatron2000(bpy.types.Operator):
    bl_idname="node.move_da_mouse_back"
    bl_label="Move da Mouse back"

    x = bpy.props.IntProperty()
    y = bpy.props.IntProperty()
    direction = bpy.props.IntProperty()

    @classmethod
    def poll(cls, context):
        sc = context.space_data
        return (sc.type == 'NODE_EDITOR'and sc.tree_type == 'ShaderNodeTree')

    

    def invoke(self, context, event):
        tree = bpy.context.scene.node_tree
        nodes = tree.nodes

        self.x = event.mouse_region_x
        self.y = event.mouse_region_y

        origin = context.region.view2d.view_to_region(0,0, clip=True)
        print("origin= ", origin)

        rel_mouse_x = self.x - origin[0]
        print("mouse", rel_mouse_x)
        abs_mouse_x = context.region.view2d.region_to_view(self.x, 0)[0]
        print(abs_mouse_x)

        for n in nodes:
            nodex=int(n.location[0])
            if nodex > abs_mouse_x:
                print("node ", n, " : " , nodex, "rel_mouse_x", rel_mouse_x)        

                n.location[0] -= 200

        return self.execute(context)

    def execute(self, context):
        return {'FINISHED'}


def collapsatron2000(operator, self, context, event, direction, tree):

    self.x = event.mouse_region_x
    self.y = event.mouse_region_y
    direction = operator.direction

    origin = context.region.view2d.view_to_region(0,0, clip=True)

    rel_mouse_x = self.x - origin[0]
    abs_mouse_x = context.region.view2d.region_to_view(self.x, 0)[0]

    for n in nodes:
        nodex=int(n.location[0])
        if nodex > abs_mouse_x:
            print("node ", n, " : " , nodex, "rel_mouse_x", rel_mouse_x)        
            n.location[0] += 200*(direction)

    return self.execute(context)



def register():
    bpy.utils.register_class(NODE_OT_move_da_mouse)
    bpy.utils.register_class(NODE_OT_collapsatron2000)

    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name='Node Editor', space_type='NODE_EDITOR')
    
    kmi = km.keymap_items.new('node.move_da_mouse', 'E', 'PRESS')
    kmi.properties.direction = 1
    
    kmi = km.keymap_items.new('node.move_da_mouse_back', 'Q', 'PRESS')
    kmi.properties.direction = -1

def unregister():
    bpy.utils.register_class(NODE_OT_move_da_mouse)
    bpy.utils.register_class(NODE_OT_collapsatron2000)


if __name__ == "__main__":
    register()
