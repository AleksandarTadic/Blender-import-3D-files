bl_info = {
    "name": "Import xyz and ply",
    "blender": (3, 6, 0),
    "location": "FILE -> Import/Export",
    "category": "Import"
}

import bpy
import math
import random
import os
from mathutils import Vector
# ply import
from io_mesh_ply import import_ply

from bpy.props import (
    CollectionProperty,
    StringProperty,
    BoolProperty,
    FloatProperty,
)
from bpy_extras.io_utils import (
    ImportHelper,
    ExportHelper,
    axis_conversion,
    orientation_helper,
)

'''Access to imported files and the number of objects, based on randomly selected files.'''
bpy.types.Scene.imported_files = []
class MyProperties(bpy.types.PropertyGroup):
    my_number: bpy.props.IntProperty(name="Number:", default = 0, min=0)

'''File import via menu, creation of XYZ and PLY collections.'''
class ImportXYZandPLY(bpy.types.Operator, ImportHelper):
    bl_idname = 'import_mesh.xyz'
    bl_label = "Import XYZ and PLY"
    bl_options = {'UNDO'}
    
    bpy.types.Scene.imported_files: []
    files: CollectionProperty(
        name="File Path",
        description="File path used for importing the XYZ and PLY files",
        type=bpy.types.OperatorFileListElement,
    )
    hide_props_region: BoolProperty(
        name="Hide Operator Properties",
        description="Collapse the region displaying the operator settings",
        default=True,
    )
    directory: StringProperty()
    filter_glob: StringProperty(default="*.xyz;*.ply", options={'HIDDEN'})

    if "xyz" not in bpy.data.collections:
        xyz = bpy.data.collections.new("xyz")
        bpy.context.scene.collection.children.link(xyz)
    if "ply" not in bpy.data.collections:
        ply = bpy.data.collections.new("ply")
        bpy.context.scene.collection.children.link(ply)

    def execute(self, context):
        context.window.cursor_set('WAIT')
        
        paths = [
            os.path.join(self.directory, name.name)
            for name in self.files
        ]

        if not paths:
            paths.append(self.filepath)
            
        bpy.types.Scene.imported_files = paths

        context.window.cursor_set('DEFAULT')

        return {'FINISHED'}

'''Adjust panel allows choosing the number of objects, with an OK operator button to add them to the scene.'''
class PANEL_PT_Object_number(bpy.types.Panel):
    bl_idname = 'PANEL_PT_Object_number'
    bl_label = "Show panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Adjust'
    bl_label = 'Adjust'
    
    def draw(self, context):
        scene = context.scene
        mytool = scene.my_tool
        
        layout = self.layout
        row = layout.row()
        row.label(text = "Number of objects", icon="OPTIONS")
        row = layout.row()
        row.prop(mytool, 'my_number')
        row = layout.row()
        row.operator("createobjects.main")
  

'''Random files, creation of XYZ and PLY objects in the scene.'''
class CREATEOBJECTS_OT_main(bpy.types.Operator):
    bl_idname = "createobjects.main"
    bl_label = "OK"

    def execute(self, context):
        scene = context.scene
        mytool = scene.my_tool
        
        files = bpy.types.Scene.imported_files
        
        xyz_files = []
        ply_files = []
        
        random_files = []
        if len(files) > 0:
            for i in range(mytool.my_number):
                random_files.append(random.choice(files))
        random_files = list(tuple(random_files))
        
        for file in random_files:
            ext = os.path.splitext(file)[-1].lower()
            if ext == ".xyz":
                xyz_files.append(file)
            elif ext == ".ply":
                ply_files.append(file)
        
        
        self.xyz_draw(xyz_files)

        self.ply_draw(ply_files)
        
        
        return {'FINISHED'}

    def xyz_draw(self, xyz_files):
        if "xyz" not in bpy.data.collections:
            xyz = bpy.data.collections.new("xyz")
            bpy.context.scene.collection.children.link(xyz)
        
        for file in xyz_files:
            if bpy.data.collections["xyz"].children.get(os.path.basename(file)) is None:
                if bpy.data.collections["xyz"].objects.get(os.path.basename(file)) is None:
                    try:
                        obj_collection = bpy.data.collections.new(os.path.basename(file))
                        bpy.data.collections["xyz"].children.link(obj_collection)
                        bpy.context.view_layer.active_layer_collection = \
                        bpy.context.view_layer.layer_collection.children["xyz"].children.get(obj_collection.name)

                        with open(file, "r") as f:
                            temp_file = f.readlines()
                            chosen_lines = temp_file[::100]
                            for line in chosen_lines:
                                bpy.ops.object.select_all(action = 'DESELECT')
                                cordinates = line.replace("\n", "").split(" ")
                                
                                nrml = Vector((1.0, 1.0, 1.0))
                                vector_normal = Vector((float(0), float(0), float(0)))
                                if len(cordinates) > 3:
                                    vector_normal = Vector((float(cordinates[3]), float(cordinates[4]), float(cordinates[5])))
                                rot = vector_normal.rotation_difference(nrml).to_euler()
                                
                                cube = bpy.ops.mesh.primitive_cube_add(location = (float(cordinates[0]), float(cordinates[1]), float(cordinates[2])), rotation=rot)
                                                 
                    except Exception as e:
                        print(e)

        bpy.ops.object.select_all(action='DESELECT')
        for coll in bpy.data.collections["xyz"].children.items():
            bpy.context.view_layer.layer_collection.children["xyz"].children.get(coll[0])
            current_coll = coll[1].objects.values()
            for obj in current_coll:
                if obj.type == 'MESH':
                    obj.select_set(True)
                    bpy.context.view_layer.objects.active = obj
                else:
                    obj.select_set(False)
            bpy.ops.object.join()
#            coll[0].split(".")[0]
            obj.name = coll[0]
            obj.data.name = coll[0]
            coll[1].objects.unlink(obj)
            bpy.data.collections["xyz"].objects.link(obj)
            bpy.ops.object.select_all(action='DESELECT')
            bpy.data.collections.remove(coll[1])
        
    def ply_draw(self, ply_files):
        if "ply" not in bpy.data.collections:
            ply = bpy.data.collections.new("ply")
            bpy.context.scene.collection.children.link(ply)
        if bpy.data.collections["ply"].children.get("CH") is None:
            obj_collection = bpy.data.collections.new("CH")
            bpy.data.collections["ply"].children.link(obj_collection)
        
        bpy.context.view_layer.active_layer_collection = \
        bpy.context.view_layer.layer_collection.children.get("ply")
        
        for file in ply_files:
            if bpy.data.collections["ply"].objects.get(os.path.basename(file).split(".")[0]) is None:
                import_ply.load_ply(file)
        
        
        bpy.ops.object.select_all(action='DESELECT')
        for obj in bpy.data.collections["ply"].objects.items():
            if bpy.data.collections["ply"].children.get("CH").objects.get(obj[0]+".ply") is None:
                obj = obj[1]
                copy = obj.copy()
                mesh_copy = obj.data.copy()
                copy.data = mesh_copy
                bpy.data.collections["ply"].children.get("CH").objects.link(copy)
                bpy.context.view_layer.objects.active = copy
                copy.select_set(True)
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.convex_hull()
                bpy.ops.object.mode_set(mode='OBJECT')
                copy.name = obj.name + ".ply"
                copy.data.name = obj.name + ".ply"
                bpy.ops.object.select_all(action='DESELECT')
                

blender_classes = [  
    MyProperties,  
    ImportXYZandPLY,
    PANEL_PT_Object_number,
    CREATEOBJECTS_OT_main
]

def menu_func_import(self, context):
    self.layout.operator(ImportXYZandPLY.bl_idname, text="Import xyz and/or ply (.xyz/.ply)")
    
def register():
    for blender_class in blender_classes:
        bpy.utils.register_class(blender_class)
        
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.types.Scene.my_tool = bpy.props.PointerProperty(type=MyProperties)
    
def unregister():
    for blender_class in blender_classes:
        bpy.utils.unregister_class(blender_class)
    
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
        
if __name__ == "__main__":
    register()