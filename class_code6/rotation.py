import numpy as np

def rotate_around_point(cx, cy, x, y, theta_degrees):
    # Convert degrees to radians
    theta = np.radians(theta_degrees)
    cos_t, sin_t = np.cos(theta), np.sin(theta)
    
    # 1. Translate to origin (subtract center)
    translation1 = np.array([
        [1, 0, -x],
        [0, 1, -y],
        [0, 0,  1]
    ])
    
    # 2. Rotate
    rotation = np.array([
        [cos_t, -sin_t, 0],
        [sin_t,  cos_t, 0],
        [0,      0,     1]
    ])
    
    # 3. Translate back (add center)
    translation2 = np.array([
        [1, 0, x],
        [0, 1, y],
        [0, 0, 1]
    ])
    
    # Combine transformations into a single matrix
    transformation_matrix = translation2 @ rotation @ translation1
    
    # Define the point vector in homogenous coordinates [cx, cy, 1]
    point = np.array([cx, cy, 1])
    
    # Apply transformation
    final_point = transformation_matrix @ point
    
    # Extract x and y
    return final_point[0], final_point[1]

x_final, y_final = rotate_around_point(10, 11, 3, 4, 60)
print(f"Rotated coordinates: ({x_final:.2f}, {y_final:.2f})")
