import bpy

'''
add the texture coordinates and mapping nodes to any texture input in cycles shading nodes.
'''


def texture_coordinator:
    node_x = active_node.location_x
    node_y = active_node.location_y

    node.create.new(texture coordinates)
    node.location_x = node_x - 200
    node.location_y = node_y

    node.create.new(mapping)
    node.location_x = node_x -100
    node.location_y = node_y

class NODES_coordinator(bpy.types.Operator):
    bl_idname = "nodes.tex_coordinator"
    bl_label = "Texture Coordinator"

    def execute:
