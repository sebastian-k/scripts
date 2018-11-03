import bpy
import bmesh
from math import floor
from mathutils import Vector
from bpy.types import Operator, Panel

def create_projector_camera(context, clip):
    cam_data = bpy.data.cameras.new(name="projector")
    camera = bpy.data.objects.new(name="projector", object_data=cam_data)
    cam_data.type = 'ORTHO'
    cam_data.ortho_scale = 1.0
    context.scene.objects.link(camera)
    context.scene.camera = camera
    camera.location = [0,0,1]
    return camera

def get_track_coordinates(frame, plane_track):
    coordinates = []
    for co in plane_track.markers[frame].corners:
        co_0 = co[0]
        co_1 = co[1]
        co_2 = 0.0
        point = Vector((co_0, co_1, co_2))
        coordinates.append(point)
    return coordinates




def prepare_baking_scene(context, clip, track):
    scn = context.scene
    # get the coordinates of plane track
    frame = scn.frame_current
    coordinates = get_track_coordinates(frame, track)
    print(coordinates)
        # coordinates.append((co0, co1))
    # create a new scene
    hashes = [hash(s) for s in bpy.data.scenes]
    bpy.ops.scene.new(type='NEW')
    new_scn = [s for s in bpy.data.scenes if hash(s) not in hashes][0]
    new_scn.frame_current = scn.frame_current
    context.screen.scene = new_scn
    camera = create_projector_camera(context, clip)
    # add new objects
    bpy.ops.mesh.primitive_plane_add(radius=0.5, calc_uvs=True, enter_editmode=False)
    ob = new_scn.objects.active
    aspect = clip.size[0] / clip.size[1]
    ob.location[0] = -0.5
    ob.location[1] = -((1/aspect)/2)
    # create the mesh
    me = ob.data
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bm.verts.ensure_lookup_table()
    for v in bm.verts:
        bm.verts.remove(v)
    for co in coordinates:
        bm.verts.new(co)
    verts = bm.verts
    bm.faces.new((verts))
    bm.to_mesh(ob.data)
    # scale the object to the movie clip dimensions
    ob.dimensions[1] = 1/aspect
    uv_layer = me.uv_layers[-1].data
    default_coords = ((0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0))
    i=0
    for co in default_coords:
        uv_layer[i].uv = co
        i+=1
    uv_tex = me.uv_textures.new(name="project") 


    sub = ob.modifiers.new(name="Subsurf", type='SUBSURF')
    sub.subdivision_type = 'SIMPLE'
    sub.levels = 5
    sub.render_levels = 5
    bpy.ops.object.modifier_apply(modifier="Subsurf")

    uvp = ob.modifiers.new(name="UVProject", type='UV_PROJECT')
    uvp.uv_layer = "project"
    uvp.aspect_x = aspect
    uvp.projectors[0].object = camera


    # prepare for baking
    new_scn.render.engine = 'CYCLES'
    new_scn.cycles.bake_type = 'EMIT'
    new_scn.cycles.max_bounces = 0
    new_scn.cycles.samples = 2
    proj_mat = bpy.data.materials.new(name="Projection")
    ob.data.materials.append(proj_mat)
    proj_mat.use_nodes = True
    nodes = proj_mat.node_tree.nodes
    links = proj_mat.node_tree.links
    for n in nodes:
        nodes.remove(n)
    emit = nodes.new(type='ShaderNodeEmission')
    output = nodes.new(type='ShaderNodeOutputMaterial')
    input = nodes.new(type='ShaderNodeTexImage')
    bake = nodes.new(type='ShaderNodeTexImage')
    uv = nodes.new(type='ShaderNodeUVMap')
    # load and setup the input image
    if not bpy.data.images.get(clip.name):
        img_input = bpy.data.images.load(clip.filepath)
    else:
        img_input = bpy.data.images.get(clip.name)
    input.image_user.frame_duration = new_scn.frame_end
    input.image_user.use_auto_refresh = True
    input.image = img_input
    # setup the baking image
    bake_input = bpy.data.images.new("Projection", 1024, 1024)
    uv.uv_map = "project"
    links.new(uv.outputs[0], input.inputs[0])
    links.new(input.outputs[0], emit.inputs[0])
    links.new(emit.outputs[0], output.inputs[0])
    bake.image = bake_input
    nodes.active  = bake
    bpy.ops.object.bake(type='EMIT')
    # bpy.data.scenes.remove(bpy.data.scenes[new_scn.name], do_unlink=True)

    # assign image to the plane track
    track.image = bake_input


class CLIP_OT_extract_plane_texture(Operator):
    bl_idname = "clip.extract_plane_texture"
    bl_label = "Extract Texture"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return space.type == 'CLIP_EDITOR' and space.clip.tracking.plane_tracks.active

    def execute(self, context):
        space = context.space_data
        clip = space.clip
        tracking = clip.tracking
        plane_track = tracking.plane_tracks.active
        prepare_baking_scene(context, clip, plane_track)
        return {'FINISHED'}



class CLIP_OT_setup_plane_track_composite(Operator):
    bl_idname = "scene.setup_plane_tack_composite"
    bl_label = "Setup Plane Composite"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return space.type == 'CLIP_EDITOR'

    def execute(self, context):
        scn = context.scene
        clip = context.space_data.clip

        if not scn.use_nodes:
            scn.use_nodes = True
        tree = scn.node_tree
        nodes = tree.nodes
        links = tree.links

        plane = nodes.new(type='CompositorNodePlaneTrackDeform')
        plane.clip = clip
        object = clip.tracking.objects.active.name
        track = clip.tracking.plane_tracks.active
        plane.tracking_object = object
        plane.plane_track_name = track.name
        plane.use_motion_blur = True
        plane.motion_blur_samples = 4

        plane_input = nodes.new(type='CompositorNodeImage')
        plane_input.image = track.image
        plane_input.location = plane.location
        plane_input.location[0] = plane.location[0] - 250


        links.new(plane_input.outputs[0], plane.inputs[0])



        return {'FINISHED'}

def register():
    bpy.utils.register_class(CLIP_OT_extract_plane_texture)
    bpy.utils.register_class(CLIP_OT_setup_plane_track_composite)

def unregister():
    bpy.utils.unregister_class(CLIP_OT_extract_plane_texture)
    bpy.utils.unregister_class(CLIP_OT_setup_plane_track_composite)

if __name__ == "__main__":
    register()
