# Blender-import-3D-files

**Python and Blender scripts for processing and visualizing 3D point clouds and meshes.**

This repository contains two main components:

1. **Python script** – processes `.xyz` point cloud files, performs rotations, estimates normals, removes outliers, and saves outputs as `.xyz` and `.ply`.  
2. **Blender add-on/script** – imports `.xyz` and `.ply` files into **Blender 3.6.0**, visualizes point clouds as cubes, applies Convex Hulls to meshes, and organizes objects into collections.

---

## 1️⃣ Python Processing Script

The Python script performs the following:

- Takes a **folder path** containing `.xyz` files as input.  
- Estimates **normals** for each point cloud.  
- Performs **statistical outlier removal** to clean noisy points.  
- Applies **rotations** to the point clouds.  
- Saves **rotated outputs** in both `.xyz` and `.ply` formats.
