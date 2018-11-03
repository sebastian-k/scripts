import bpy

context = bpy.context



# for ob in context.selected_objects:
    # if ob.type == 'EMPTY' and ob.dupli_group:
        # print(ob.name, " = Empty")
        # # what kind of type are the objects in the instanced group?
        # for ob in ob.dupli_group.objects:
            # if ob.type == 'EMPTY' and ob.dupli_group:
                # for ob in ob.dupli_group.objects:
                    # if ob.type == 'MESH':
                        # print('MESH!!')
                    # elif ob.type == 'EMPTY':
                        # print("EMPTY")
            # elif ob.type == 'MESH':
                # print("MESH")

for ob in context.selected_objects:
    object = False
    while object:
        if ob.type == 'MESH':
            object = True
        else:
            if ob.type == 'EMPTY' and ob.dupli_group:
                object = False
    print("hello")


