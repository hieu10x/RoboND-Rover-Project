import numpy as np
import cv2

# Identify pixels above the threshold
def color_thresh(img, low_rgb_thresh=(0, 0, 0), up_rgb_thresh=(255, 255, 255)):
    # Create an array of zeros same xy size as img, but single channel
    color_select = np.zeros_like(img[:,:,0])
    # Require that each pixel be above all three threshold values in RGB
    # above_thresh will now contain a boolean array with "True"
    # where threshold was met
    take_thresh = True
    for i in range(3):
        take_thresh &= img[:,:,i] >= low_rgb_thresh[i]
        take_thresh &= img[:,:,i] <= up_rgb_thresh[i]
    # Index the array of zeros with the boolean array and set to 1
    color_select[take_thresh] = 1
    # Return the binary image
    return color_select

def hsv_thresh(img, low_hsv_thresh=(0, 0, 0), up_hsv_thresh=(255, 255, 255)):
    color_select = np.zeros_like(img[:,:,0])
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    print(img.shape, hsv.shape)
    take_thresh = True
    for i in range(3):
        take_thresh &= hsv[:,:,i] >= low_hsv_thresh[2-i]
        take_thresh &= hsv[:,:,i] <= up_hsv_thresh[2-i]
    color_select[take_thresh] = 1
    return color_select

# Define a function to convert to rover-centric coordinates
def rover_coords(binary_img):
    # Identify nonzero pixels
    ypos, xpos = binary_img.nonzero()
    # Calculate pixel positions with reference to the rover position being at the
    # center bottom of the image.
    x_pixel = np.absolute(ypos - binary_img.shape[0]).astype(np.float)
    y_pixel = -(xpos - binary_img.shape[0]).astype(np.float)
    return x_pixel, y_pixel


# Define a function to convert to radial coords in rover space
def to_polar_coords(x_pixel, y_pixel):
    # Convert (x_pixel, y_pixel) to (distance, angle)
    # in polar coordinates in rover space
    # Calculate distance to each pixel
    dist = np.sqrt(x_pixel**2 + y_pixel**2)
    # Calculate angle away from vertical for each pixel
    angles = np.arctan2(y_pixel, x_pixel)
    return dist, angles

# Define a function to apply a rotation to pixel positions
def rotate_pix(xpix, ypix, yaw):
    # Convert yaw to radians
    yaw_rad = yaw * np.pi / 180
    # Apply a rotation
    xpix_rotated = xpix * np.cos(yaw_rad) - ypix * np.sin(yaw_rad)
    ypix_rotated = xpix * np.sin(yaw_rad) + ypix * np.cos(yaw_rad)
    # Return the result
    return xpix_rotated, ypix_rotated

# Define a function to perform a translation
def translate_pix(xpix_rot, ypix_rot, xpos, ypos, scale):
    # Apply a scaling and a translation
    xpix_translated = (xpix_rot / scale) + xpos
    ypix_translated = (ypix_rot / scale) + ypos
    # Return the result
    return xpix_translated, ypix_translated

# Define a function to apply rotation and translation (and clipping)
# Once you define the two functions above this function should work
def pix_to_world(xpix, ypix, xpos, ypos, yaw, world_size, scale):
    # Apply rotation
    xpix_rot, ypix_rot = rotate_pix(xpix, ypix, yaw)
    # Apply translation
    xpix_tran, ypix_tran = translate_pix(xpix_rot, ypix_rot, xpos, ypos, scale)
    # Perform rotation, translation and clipping all at once
    x_pix_world = np.clip(np.int_(xpix_tran), 0, world_size - 1)
    y_pix_world = np.clip(np.int_(ypix_tran), 0, world_size - 1)
    # Return the result
    return x_pix_world, y_pix_world

# Define a function to perform a perspective transform
def perspect_transform(img, src, dst):

    M = cv2.getPerspectiveTransform(src, dst)
    warped = cv2.warpPerspective(img, M, (img.shape[1], img.shape[0]))# keep same size as input image

    return warped


# Apply the above functions in succession and update the Rover state accordingly
def perception_step(Rover):
    # Perform perception steps to update Rover()
    # NOTE: camera image is coming to you in Rover.img
    # 1) Define source and destination points for perspective transform
    dst_size = 5
    bottom_offset = 6
    # source = np.float32([[14, 140], [301 ,140],[200, 96], [118, 96]])
    source = np.float32([[7,143], [311,143], [202,97], [117,97]])  # my settings
    destination = np.float32([[Rover.img.shape[1]/2 - dst_size, Rover.img.shape[0] - bottom_offset],
                      [Rover.img.shape[1]/2 + dst_size, Rover.img.shape[0] - bottom_offset],
                      [Rover.img.shape[1]/2 + dst_size, Rover.img.shape[0] - 2*dst_size - bottom_offset],
                      [Rover.img.shape[1]/2 - dst_size, Rover.img.shape[0] - 2*dst_size - bottom_offset],
                      ])

    # 2) Apply perspective transform
    warped = perspect_transform(Rover.img, source, destination)
    # 3) Apply color threshold to identify navigable terrain/obstacles/rock samples
    nav = color_thresh(warped, low_rgb_thresh=(161,161,161))
    obstacle = color_thresh(warped, low_rgb_thresh=(2,2,2), up_rgb_thresh=(160,160,160))
    rock = hsv_thresh(warped, (130, 170, 0), (220, 255, 155))
    # 4) Update Rover.vision_image (this will be displayed on left side of screen)
    Rover.vision_image[:,:,0] = obstacle * 255
    Rover.vision_image[:,:,1] = rock * 255
    Rover.vision_image[:,:,2] = nav * 255
    # 5) Convert map image pixel values to rover-centric coords
    nav_x_rover, nav_y_rover = rover_coords(nav)
    obstacle_x_rover, obstacle_y_rover = rover_coords(obstacle)
    rock_x_rover, rock_y_rover = rover_coords(rock)
    # 6) Convert rover-centric pixel values to world coordinates
    scale = 10
    # Get navigable pixel positions in world coords
    nav_x_world, nav_y_world = pix_to_world(nav_x_rover, nav_y_rover,
                                            Rover.pos[0], Rover.pos[1], Rover.yaw,
                                            Rover.worldmap.shape[0], scale)
    obstacle_x_world, obstacle_y_world = pix_to_world(obstacle_x_rover, obstacle_y_rover,
                                            Rover.pos[0], Rover.pos[1], Rover.yaw,
                                            Rover.worldmap.shape[0], scale)
    rock_x_world, rock_y_world = pix_to_world(rock_x_rover, rock_y_rover,
                                            Rover.pos[0], Rover.pos[1], Rover.yaw,
                                            Rover.worldmap.shape[0], scale)
    # 7) Update Rover worldmap (to be displayed on right side of screen)
    Rover.worldmap[rock_y_world, rock_x_world, 1] += 1
    eps = 1
    if (0 <= Rover.pitch <= eps or 360 - eps <= Rover.pitch <= 360) and (0 <= Rover.roll <= eps or 360 - eps <= Rover.roll <= 360):
        Rover.worldmap[obstacle_y_world, obstacle_x_world, 0] += 1
        Rover.worldmap[nav_y_world, nav_x_world, 2] += 1

    # 8) Convert rover-centric pixel positions to polar coordinates
    # Update Rover pixel distances and angles
    rover_centric_pixel_distances, rover_centric_angles = to_polar_coords(nav_x_rover, nav_y_rover)
    Rover.nav_dists = rover_centric_pixel_distances
    Rover.nav_angles = rover_centric_angles




    return Rover