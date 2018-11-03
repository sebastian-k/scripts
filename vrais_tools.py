
import bpy
import os
import codecs
import datetime
from math import *
from bpy.props import *
import http.client

context = bpy.context
scene = context.scene

def initSceneProperties(scene):
    # Define own Properties
    bpy.types.Scene.description_string = StringProperty(
        name = "Scene Description")
    scene['description_string'] = "Test Description"
    
    bpy.types.Scene.output_folder = StringProperty(
        name = "Output Folder",
        subtype = "DIR_PATH")
    scene['output_folder'] = "//../../../"

    bpy.types.Scene.own_file_name = StringProperty(
        name = "File Name",)
    scene['own_file_name'] = ""

    bpy.types.Scene.overwrite_name = BoolProperty(
        name = "Name Boolean")
    scene['overwrite_name'] = False

    bpy.types.Scene.is_cubemap = BoolProperty(
        name = "IsCubemap Boolean")
    scene['is_cubemap'] = True

    return


#### configure parameters ###############################
initSceneProperties(bpy.context.scene)
###########################################################

def token_checker():
    # check if token exists and is (probably) valid
    if not bpy.context.scene.get("vrais_token"):
        print("nah")
        return "nah"
    else:
        vrais_token = bpy.context.scene.get('vrais_token')
        if len(str(vrais_token))<2:
            print("no valid token configured ")
        else:
            return vrais_token


def generate_filename():
    current_filename = bpy.path.basename(bpy.context.blend_data.filepath)
    blendname = os.path.splitext(current_filename)[0]
    now = datetime.datetime.now()
    date = now.strftime("%Y_%m%d_%H-%M")
    imagename = blendname + "_" + date
    return imagename


def prepare_vr(context):
    # ensure correct aspect ratio
    scene = context.scene
    render = scene.render
    cam = scene.camera.data

    if render.resolution_x != render.resolution_y*2:
        render.resolution_x = 2048
        render.resolution_y = 1024
    render.use_multiview = True
    render.use_file_extension = True
    render.image_settings.file_format = "JPEG"
    render.image_settings.views_format = 'STEREO_3D'
    render.image_settings.stereo_3d_format.display_mode = "TOPBOTTOM"
    cam.type = 'PANO'
    cam.cycles.panorama_type = 'EQUIRECTANGULAR'
    cam.stereo.convergence_mode = 'OFFAXIS'
    cam.stereo.pivot = 'CENTER'




def configure_outputpath(filename):
    outputpath = bpy.context.scene.output_folder + filename
    return outputpath
    

def vr_uploader_test():
    print("filename: ", filename)
    print("token: ", token)
    print("description :",  description)


def vr_uploader():
    filepath = os.path.dirname(bpy.context.blend_data.filepath) + configure_outputpath(filename) + ".jpg"
    f = open(filepath, "rb")
    chunk = f.read()
    f.close()

    headers = {
        "Content-type": "multipart/form-data",
        "Accept": "text/plain",
        "Title": filename,
        "Description": description,
        "Token": token,
        "Convergence": convergence,
        "IsCubemap": isCubemap
    }

    conn = http.client.HTTPConnection("vrais.io")
    conn.request("POST", "/api.php?cmd=uploadItem", chunk, headers)

    response = conn.getresponse()
    remote_file = response.read()
    conn.close()
    print (remote_file)
   

def render_handler(scene):
    vr_uploader()



######### CLASSES ##########


class OT_RenderVR(bpy.types.Operator):
    bl_idname = "scene.render_vr"
    bl_label = "Render and Upload VR"

    def execute(self, context):
        global description
        global filename
        global token
        global convergence

        scene = context.scene
        convergence = str(scene.camera.data.stereo.convergence_distance)[:4]
        token = token_checker()

        # configure filename and description based on user input or auto
        if scene.overwrite_name == True:
            filename = scene.own_file_name
        else:
            filename = generate_filename()

        if len(scene.description_string)==0:
            description = "Test"
        else:
            description = bpy.context.scene.description_string

        # make sure the scene is configured for VR
        prepare_vr(context)

        #set output path and render
        bpy.context.scene.render.filepath = configure_outputpath(filename)
        bpy.ops.render.render('INVOKE_DEFAULT', write_still = True)

        return{'FINISHED'}



############## UI ###########

class PROP_PT_vr_controls(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "VR Render & Upload"
    bl_idname = "RENDER_PT_vr_controls"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        render = scene.render

        col = layout.column()
        col.prop(scene, "is_cubemap", text="Is a Cubemap")
        col.prop(scene, "overwrite_name", text="Use own filename")
        if scene.overwrite_name == True:
            col.prop(scene, "own_file_name", text="Filename")
        col.prop(scene, 'output_folder')
        col.prop(scene, 'description_string')
        col.operator("scene.render_vr", icon="RENDER_STILL")




########## REGISTER ############

def register():
    bpy.app.handlers.render_complete.append(render_handler)
    
    bpy.utils.register_class(OT_RenderVR)
    bpy.utils.register_class(PROP_PT_vr_controls)

def unregister():
    if render_handler in bpy.app.handlers.render_complete:
        bpy.app.handlers.render_complete.remove(render_handler)
    
    bpy.utils.register_class(OT_RenderVR)
    bpy.utils.register_class(PROP_PT_vr_controls)

if __name__ == "__main__":
     register()

