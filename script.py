import os
import open3d as o3d
import numpy as np

def script(path_to_folder):
    if os.path.isdir(path_to_folder):
        if not os.path.exists(path_to_folder + "/export"):
            os.makedirs(path_to_folder + "/export")
        file_list = os.listdir(path_to_folder)
        xyz_list = []
        for file in file_list:
            if file.endswith(".xyz"):
                file_name = file.split(".")[0]
                xyz = o3d.io.read_point_cloud(path_to_folder + "/" + file)
                xyz.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamKNN())
                cl, ind = xyz.remove_statistical_outlier(nb_neighbors = 10, std_ratio = .001)
                try:
                    export_file_xyz = ""
                    points = np.asarray(cl.points)
                    normals = np.asarray(cl.normals)
                    for i in range(len(points)):
                        temp = ""
                        if len(normals) > 0:
                            temp += f"{round(float(points[i][0]), 6)} {round(float(points[i][1]), 6)} {round(float(points[i][2]), 6)} {round(float(normals[i][0]), 6)} {round(float(normals[i][1]), 6)} {round(float(normals[i][2]), 6)} \n"
                        else:
                            temp += f"{round(float(points[i][0]), 6)} {round(float(points[i][1]), 6)} {round(float(points[i][2]), 6)} \n"
                        export_file_xyz += temp
                    with open(f"{path_to_folder}/export/{file_name}.xyz", "w", encoding="utf-8") as f:
                        f.write(export_file_xyz)
                    o3d.io.write_point_cloud(f"{path_to_folder}/export/{file_name}.ply", cl)
                except Exception as e:
                    print(e)
        print("All files are located in the export folder.")
    else:
        print("Invalid input, a folder path is required.")

script("D:/blender/export") # example