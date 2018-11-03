import bpy
import platform
data = bpy.data
context = bpy.context

def fix_path(i, testphrase):
    # cut off pseudo relative path that includes absolute path
    if testphrase in i.filepath:
        fixed_path = i.filepath.partition(testphrase)[1:]
        fixed_path = "".join(fixed_path)
        i.filepath = fixed_path

def fix_os(i):
    # change main absolute directories
    lin_shared = "/media/shared/"
    win_shared = "S:/"
    lin_render = "/media/render/"
    win_render = "R:/"
    if platform.system() == "Windows":
        i.filepath = i.filepath.replace(lin_shared, win_shared)
        i.filepath = i.filepath.replace(lin_render, win_render)
        fix_path(i, win_shared)
        fix_path(i, win_render)
        print(i.filepath)
    else:
        i.filepath = i.filepath.replace(win_shared, lin_shared)
        i.filepath = i.filepath.replace(win_render, lin_render)
        fix_path(i, lin_shared)
        fix_path(i, lin_render)
        print(i.filepath)

for i in data.images:
    if not i.packed_file is not None:
        fix_os(i)

for m in data.movieclips:
    fix_os(m)

fix_os(context.scene.render)
