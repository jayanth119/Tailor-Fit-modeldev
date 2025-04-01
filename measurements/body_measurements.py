"""Main file for body measurements"""
import trimesh
import open3d as o3d
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import ConvexHull
import math

'''Loading the 3D model'''
# Load the 3D human body model (.obj file)
mesh = trimesh.load_mesh(r"C:\Users\Sai\Desktop\My\dream\projects\Tailor-Fit-modeldev\outputs\result_poojitha_1_256.obj")

# Convert trimesh to Open3D format for further processing
o3d_mesh = o3d.geometry.TriangleMesh()
o3d_mesh.vertices = o3d.utility.Vector3dVector(mesh.vertices)
o3d_mesh.triangles = o3d.utility.Vector3iVector(mesh.faces)


def visualize_with_points(o3d_mesh, points_list, labels=None):
    """
    Visualize mesh with highlighted measurement points
    """
    mesh_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(size=0.1)
    geometries = [o3d_mesh, mesh_frame]
    
    # Create colored spheres for key points
    colors = [[1, 0, 0], [0, 1, 0], [0, 0, 1], [1, 1, 0], [1, 0, 1], [0, 1, 1]]
    
    for i, point in enumerate(points_list):
        sphere = o3d.geometry.TriangleMesh.create_sphere(radius=0.01)
        sphere.translate(point)
        sphere.paint_uniform_color(colors[i % len(colors)])
        geometries.append(sphere)
    
    o3d.visualization.draw_geometries(geometries)

'''Extract measurements based on cross-sections'''
def get_cross_section(mesh, height, axis=1):
    """
    Get a cross-section of the mesh at the specified height along the given axis
    Returns the 2D points of the cross-section
    """
    # Create a plane at the specified height
    plane_origin = [0, height, 0] if axis == 1 else ([0, 0, height] if axis == 2 else [height, 0, 0])
    plane_normal = [0, 1, 0] if axis == 1 else ([0, 0, 1] if axis == 2 else [1, 0, 0])
    
    # Get the cross-section
    slice_3d = mesh.section(plane_origin=plane_origin, plane_normal=plane_normal)
    
    if slice_3d is None or slice_3d.vertices.size == 0:
        return None
    
    # Convert to 2D points (ignoring the axis dimension)
    if axis == 1:  # Y-axis
        points_2d = slice_3d.vertices[:, [0, 2]]
    elif axis == 2:  # Z-axis
        points_2d = slice_3d.vertices[:, [0, 1]]
    else:  # X-axis
        points_2d = slice_3d.vertices[:, [1, 2]]
    
    return points_2d

def calculate_circumference(points_2d):
    """
    Calculate the circumference of a cross-section from 2D points
    """
    if points_2d is None or len(points_2d) < 3:
        return 0
    
    # Use convex hull to get the perimeter
    hull = ConvexHull(points_2d)
    
    # Calculate perimeter
    perimeter = 0
    for simplex in hull.simplices:
        p1 = points_2d[simplex[0]]
        p2 = points_2d[simplex[1]]
        perimeter += np.linalg.norm(p2 - p1)
    
    return perimeter

def get_height_measurement(vertices):
    """
    Calculate height of the model
    """
    return np.max(vertices[:, 1]) - np.min(vertices[:, 1])

def get_width_at_height(points_2d):
    """
    Calculate width of cross-section
    """
    if points_2d is None or len(points_2d) < 2:
        return 0
    
    min_x = np.min(points_2d[:, 0])
    max_x = np.max(points_2d[:, 0])
    return max_x - min_x

def get_depth_at_height(points_2d):
    """
    Calculate depth of cross-section
    """
    if points_2d is None or len(points_2d) < 2:
        return 0
    
    min_z = np.min(points_2d[:, 1])
    max_z = np.max(points_2d[:, 1])
    return max_z - min_z

# Convert vertices to NumPy array
vertices = np.asarray(mesh.vertices)

# Extract key heights
max_height = np.max(vertices[:, 1])
min_height = np.min(vertices[:, 1])
total_height = max_height - min_height

# Define key measurement heights (relative to the model's height)
key_heights = {
    'neck': 0.85,
    'shoulder': 0.80,
    'chest': 0.70,
    'waist': 0.50,
    'hip': 0.40,
    'thigh': 0.30,
    'knee': 0.20,
    'ankle': 0.05
}

# Calculate actual heights and store measurement points
measurement_points = {}
measurements = {}
heights = {}

for key, relative_height in key_heights.items():
    height = min_height + total_height * relative_height
    heights[key] = height
    
    # Get cross-section at this height
    points_2d = get_cross_section(mesh, height)
    
    if points_2d is not None and len(points_2d) >= 3:
        # Find centroid of the cross-section
        centroid = np.mean(points_2d, axis=0)
        # Convert back to 3D coordinates
        measurement_points[key] = np.array([centroid[0], height, centroid[1]])
        
        # Calculate measurements
        circumference = calculate_circumference(points_2d)
        width = get_width_at_height(points_2d)
        depth = get_depth_at_height(points_2d)
        
        measurements[key] = {
            'circumference': circumference,
            'width': width,
            'depth': depth
        }

# Calculate additional body measurements
measurements['height'] = total_height
measurements['shoulder_width'] = measurements.get('shoulder', {}).get('width', 0)
measurements['arm_length'] = total_height * 0.35  # Approximate

# Print all measurements in centimeters (assuming model is in meters)
print("\n===== BODY MEASUREMENTS =====")
print(f"Height: {measurements['height']*100:.1f} cm")

for key in key_heights.keys():
    if key in measurements:
        print(f"\n{key.capitalize()}:")
        print(f"  - Circumference: {measurements[key]['circumference']*100:.1f} cm")
        print(f"  - Width: {measurements[key]['width']*100:.1f} cm")
        print(f"  - Depth: {measurements[key]['depth']*100:.1f} cm")

# Visualize the mesh with measurement points
measurement_points_list = list(measurement_points.values())
measurement_labels = list(measurement_points.keys())

# Plot measurement cross-sections
fig, axes = plt.subplots(2, 4, figsize=(20, 10))
axes = axes.flatten()

for i, (key, height) in enumerate(list(heights.items())[:8]):
    points_2d = get_cross_section(mesh, height)
    if points_2d is not None and len(points_2d) >= 3:
        axes[i].scatter(points_2d[:, 0], points_2d[:, 1], s=1)
        axes[i].set_title(f"{key.capitalize()} (h={height:.2f})")
        axes[i].set_aspect('equal')
        
        # Plot convex hull
        hull = ConvexHull(points_2d)
        for simplex in hull.simplices:
            axes[i].plot(points_2d[simplex, 0], points_2d[simplex, 1], 'r-')

# plt.tight_layout()
# plt.savefig("body_measurements.png")
# plt.show()

# Visualize the 3D model with measurement points
visualize_with_points(o3d_mesh, measurement_points_list, measurement_labels)