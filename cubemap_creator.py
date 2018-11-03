bl_info = {
    "name": "Cubemap Creator",
    "author": "Sebastian Koenig",
    "version": (0, 1),
    "blender": (2, 77, 0),
    "location": "Render -> Settings",
    "description": "Create cubemap stripes and upload to VRAIS",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Render"}


import bpy
import os
import http.client
from bpy.props import *
from bpy.types import Operator, AddonPreferences


class CubemapCreator(bpy.types.AddonPreferences):
    bl_idname = __name__

    vrais_token = StringProperty(name="VRAIS TOKEN")

    def draw(self, context):
        layout = self.layout
        layout.label(text="Configure your VRAIS Token")
        layout.prop(self, "vrais_token")


###########################################################


def create_cubemap_path(scene):
    renderpath = scene.render.filepath
    suffix = ".jpg"
    cubemap_path = os.path.join(renderpath, "../", scene.cubemap_settings.filename + suffix)
    return cubemap_path


def create_new_scene(new_scene, dimensions, resolution):
    scene = bpy.context.scene
    tree = new_scene.node_tree
    new_scene.view_settings.view_transform = scene.view_settings.view_transform
    new_scene.view_settings.look = scene.view_settings.look
    cam_data = scene.camera.data
    cam = bpy.data.objects.new("tmp_cam", cam_data)
    new_scene.objects.link(cam)
    render = new_scene.render
    render.resolution_x = dimensions*12
    render.resolution_y = dimensions
    render.resolution_percentage = resolution
    render.image_settings.file_format = "JPEG"
    render.filepath = create_cubemap_path(scene)
    new_scene.use_nodes = True
    for n in new_scene.node_tree.nodes:
        new_scene.node_tree.nodes.remove(n)


def create_img_path(source_scene, img):
    file_format = source_scene.render.image_settings.file_format.lower()
    if file_format == "jpeg":
        file_format = "jpg"
    path = os.path.join(source_scene.render.filepath, img + "." + file_format)
    return path


def nodes(new_scene, img, index):
    tree = new_scene.node_tree
    img_node = tree.nodes.new(type="CompositorNodeImage")
    img_node.location = img_node.location[0], img_node.location[1] -  index*300
    img_new = bpy.data.images.load(filepath=img)
    img_node.image = img_new
    img_node.name = str(index)


def connector(new_scene, offset):
    tree = new_scene.node_tree
    nodes = tree.nodes
    links = tree.links
    resolution = new_scene.render.resolution_percentage
    offset = offset/100*resolution
    center = -(offset*5)-(offset/2)

    for i in range(1,12):
        img_1 = nodes[str(i)]
        img_2 = nodes[str(i+1)]
        mix = nodes.new(type="CompositorNodeAlphaOver")
        if i == 1:
            tl_1 = nodes.new(type="CompositorNodeTransform")
            tl_1.location = img_1.location[0] + 100, img_1.location[1]
            tl_1.inputs['X'].default_value = center
            links.new(img_1.outputs[0], tl_1.inputs[0])
            links.new(tl_1.outputs[0], mix.inputs[1])

        tl = tree.nodes.new(type="CompositorNodeTransform")
        tl.inputs['X'].default_value = center + offset * i 
        tl.location = img_1.location[0] + 100, img_2.location[1]
        mix.location = tl.location[0] + 200, img_2.location[1] + 100
        links.new(img_2.outputs[0], tl.inputs[0])
        if not i ==1:
            links.new(img_1.outputs[0], mix.inputs[1])
        links.new(tl.outputs[0], mix.inputs[2])
        img_2.name = "old"
        mix.name = str(i+1)

    last_node = nodes['12']
    output = nodes.new(type="CompositorNodeComposite")
    output.location = last_node.location[0] + 200, last_node.location[1]
    links.new(last_node.outputs[0], output.inputs[0])


def img_node_creator(new_scene, source_scene):
    frame = str(source_scene.frame_current).zfill(4)

    img_dict = {
        "EAST_%s_R" % (frame):1,     
        "WEST_%s_R" % (frame):2,     
        "ZENITH_%s_R" % (frame):3,     
        "NADIR_%s_R" % (frame):4,     
        "NORTH_%s_R" % (frame):5,     
        "SOUTH_%s_R" % (frame):6,
        "EAST_%s_L" % (frame):7,     
        "WEST_%s_L" % (frame):8,     
        "ZENITH_%s_L" % (frame):9,     
        "NADIR_%s_L" % (frame):10,     
        "NORTH_%s_L" % (frame):11,     
        "SOUTH_%s_L" % (frame):12      
    }
    for img in img_dict:
        i = create_img_path(source_scene, img)
        index = img_dict[img]
        nodes(new_scene, i, index)


def vr_uploader(scene):
    filepath = bpy.path.abspath(create_cubemap_path(scene))
    f = open(filepath, "rb")
    chunk = f.read()
    f.close()
    if scene.vrais_enum == "VRAIS_Cubemap":
        is_cubemap = "1"
    else:
        is_cubemap = "0"

    headers = {
        "Content-type": "multipart/form-data",
        "Accept": "text/plain",
        "Title": scene.cubemap_settings.vrais_name,
        "Description": scene.cubemap_settings.description_string,
        "Token": bpy.context.user_preferences.addons[__name__].preferences.vrais_token,
        "Convergence": str(scene.camera.data.stereo.convergence_distance),
        "IsCubemap": is_cubemap
    }

    conn = http.client.HTTPConnection("vrais.io")
    conn.request("POST", "/api.php?cmd=uploadItem", chunk, headers)
    response = conn.getresponse()
    remote_file = response.read()
    conn.close()
    print ("uploaded ", remote_file)



class VIEW3D_OT_create_cubemap(bpy.types.Operator):
    """Create and upload Cubemap Stripe"""
    bl_idname = "scene.create_cubemap_stripe"
    bl_label = "Create & Upload Cubemap Stripe"


    def execute(self, context):
        # check for token
        # config variables
        source_scene = context.scene
        path = source_scene.render.filepath
        dimensions = source_scene.render.resolution_y
        convergence = str(source_scene.camera.data.stereo.convergence_distance)[:4]
        resolution = source_scene.render.resolution_percentage
        temp_scene = "tmp_"

        if len(source_scene.cubemap_settings.description_string)==0:
            description = "Test"
        else:
            description = bpy.context.scene.cubemap_settings.description_string

        # create hashes for the all existing scenes, in order to filter out the new now later
        hashes = [hash(scene) for scene in bpy.data.scenes]
        bpy.ops.scene.new(type='NEW')
        # get the new scene by comparing it to hashes
        new_scene = [scene for scene in bpy.data.scenes if hash(scene) not in hashes][0]
        new_scene.name = temp_scene
        # create the new tmp scene in order to stich the cubemap
        create_new_scene(new_scene, dimensions, resolution)
        # create the image nodes with the 12 cubemap images
        img_node_creator(new_scene, source_scene)
        # connect the image nodes to the transform nodes and mix them together
        connector(new_scene, dimensions)
        # render and save the composite
        bpy.ops.render.render(write_still=True, scene = temp_scene)
        # get rid of the tmp scene
        bpy.data.scenes.remove(bpy.data.scenes[temp_scene], do_unlink=True)
        # upload to VRAIS
        if len(context.user_preferences.addons[__name__].preferences.vrais_token)<2:
            self.report({'ERROR'}, "No VRAIS token configured in Addon Preferences!")
            return {'CANCELLED'}
        else:
            vr_uploader(source_scene)

        return {'FINISHED'}
 


########### UI ##################

class SCENE_PT_create_cubemap_stripe(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "Cubemap Stripe Creator"
    bl_idname = "SCENE_PT_create_cubemap_stripe"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        col = layout.column()
        cubemap = scene.vrais_enum == "VRAIS_Cubemap"
        col.prop(scene.cubemap_settings, 'filename')
        col.prop(scene.cubemap_settings, 'vrais_name')
        col.prop(scene.cubemap_settings, 'description_string')
        col = layout.column(align=True)
        col.operator("scene.create_cubemap_stripe")


####### PROPERTIES ############

class CubemapCreatorProperties(bpy.types.PropertyGroup):
    filename = StringProperty(name="Filename", default="cubemap")
    vrais_name = StringProperty(name="VRais Name", default="Blender VR Rendering")
    description_string = StringProperty(name="Scene Description", default="Render Test")


def register():
    bpy.utils.register_class(VIEW3D_OT_create_cubemap)
    bpy.utils.register_class(SCENE_PT_create_cubemap_stripe)
    bpy.utils.register_class(CubemapCreator)
    bpy.utils.register_class(CubemapCreatorProperties)

    bpy.types.Scene.cubemap_settings = PointerProperty(type=CubemapCreatorProperties)
    bpy.types.Scene.vrais_enum = bpy.props.EnumProperty(
        items=(
        ('VRAIS_Equi','Equirectangular','Equirectangular Rendering', 1),
        ('VRAIS_Cubemap','Cubemap','Cubemap Stripe', 2),
        )
    )




def unregister():
    bpy.utils.unregister_class(VIEW3D_OT_create_cubemap)
    bpy.utils.unregister_class(SCENE_PT_create_cubemap_stripe)
    bpy.utils.unregister_class(CubemapCreator)
    bpy.utils.unregister_class(CubemapCreatorProperties)
    del bpy.types.Scene.cubemap_settings


if __name__ == "__main__":
    register()

