## Project: Search and Sample Return
### Writeup Template: You can use this file as a template for your writeup if you want to submit it as a markdown file, but feel free to use some other method and submit a pdf if you prefer.

---


**The goals / steps of this project are the following:**

**Training / Calibration**

* Download the simulator and take data in "Training Mode"
* Test out the functions in the Jupyter Notebook provided
* Add functions to detect obstacles and samples of interest (golden rocks)
* Fill in the `process_image()` function with the appropriate image processing steps (perspective transform, color threshold etc.) to get from raw images to a map.  The `output_image` you create in this step should demonstrate that your mapping pipeline works.
* Use `moviepy` to process the images in your saved dataset with the `process_image()` function.  Include the video you produce as part of your submission.

**Autonomous Navigation / Mapping**

* Fill in the `perception_step()` function within the `perception.py` script with the appropriate image processing functions to create a map and update `Rover()` data (similar to what you did with `process_image()` in the notebook).
* Fill in the `decision_step()` function within the `decision.py` script with conditional statements that take into consideration the outputs of the `perception_step()` in deciding how to issue throttle, brake and steering commands.
* Iterate on your perception and decision function until your rover does a reasonable (need to define metric) job of navigating and mapping.

[//]: # (Image References)

[image1]: ./output/example_images.png
[image2]: ./output/mydata_images.png
[image3]: ./output/example_warped.png
[image4]: ./output/mydata_warped.png
[image5]: ./output/example_color_thresh.png
[image6]: ./output/mydata_color_thresh.png
[image7]: ./output/example_hsv_thresh.png
[image8]: ./output/mydata_hsv_thresh.png

## [Rubric](https://review.udacity.com/#!/rubrics/916/view) Points
### Here I will consider the rubric points individually and describe how I addressed each point in my implementation.

---
### Writeup / README

#### 1. Provide a Writeup / README that includes all the rubric points and how you addressed each one.  You can submit your writeup as markdown or pdf.

You're reading it!

### Notebook Analysis
#### 1. Run the functions provided in the notebook on test images (first with the test data provided, next on data you have recorded). Add/modify functions to allow for color selection of obstacles and rock samples.

To run the perspective transformation on my dataset, I calibrate the transformation parameters using `../calibration_images/my_grid.jpg` taken in training mode with grid on. I need to do this because the camera perspective in my settings may be different to the one used in the example.

My Roversim settings:
- Screen resolution: 1680 x 1050
- Windowed: Yes
- Graphics quality: Fantastic

Example images:

![Example images][image1]

My data images:

![My data images][image2]

Warped images:

![Example warped image][image3]
![My data warped image][image4]

The `color_thresh()` function has been modified to accept both lower and upper thresholds. This is useful to detect obstacles as well as navigable terrain.

![Example color_thresh image][image5]
![My data color_thresh image][image6]

To detect golden rocks, HSV (hue, saturation, and value) color space is used. Color detection in this color space is robust to the lighting condition. See `hsv_thresh()` function.

![Example hsv_thresh image][image7]
![My data hsv_thresh image][image8]

#### 2. Populate the `process_image()` function with the appropriate analysis steps to map pixels identifying navigable terrain, obstacles and rock samples into a worldmap.  Run `process_image()` on your test data using the `moviepy` functions provided to create video output of your result.
And another!

After filling the steps in `process_image()` function with the implemented functions, the below video is produced from my dataset:

![My Video 1](./output/my_mapping1.mp4)

Another video from another dataset:

![My Video 2](./output/my_mapping2.mp4)

### Autonomous Navigation and Mapping

#### 1. Fill in the `perception_step()` (at the bottom of the `perception.py` script) and `decision_step()` (in `decision.py`) functions in the autonomous mapping scripts and an explanation is provided in the writeup of how and why these functions were modified as they were.

Changes in `perception_step()` function:
- Fill in the steps. All are straight-forward.
- Step 1: Define the source box according to the calibration image. The destination is similar to the one provided in the example.
- Step 2: Perform the perspective transformation.
- Step 3: Apply `color_thresh()` to detect obstacles and navigable terrain. Apply `hsv_thresh()` to detect golden rocks (collectible samples).
- Step 4: Update the vision image. Multiply the values by 255 to get the maximum values for each color channels.
- Step 5: Convert pixel coords to Rover-centric coords via `rover_coords()` function for each type of objects (obstacle, navigable, rock).
- Step 6: Convert rover-centric coords to world coords via `pix_to_world()` function for each type.
- Step 7: Update worldmap. To improve the mapping fidelity, only images where the Rover's pitch and roll are in range of `(-1 deg, 1 deg)` are considered.
- Step 8: Convert rover-centric pixel positions to polar coordinates preparing for decision making.

Changes in `decision_step()` function:
- Stop earlier before hitting the obstacles. If the max distance of open space is less than `40 units`, hit the brake.
- Rotate left/right randomly when looking for open space. Steer left half of the time, steer right another half.
- Add unstuck mode. Every `60 seconds`, check if the navigable worldmap has not been expanded since last check. Unstuck the Rover by rotate to a random yaw angle.
- Favor left side. When there is open space, the steering angle is the combination of the average angle and the left most angle with more weight on the average angle.

#### 2. Launching in autonomous mode your rover can navigate and map autonomously.  Explain your results and how you might improve them in your writeup.

**Note: running the simulator with different choices of resolution and graphics quality may produce different results, particularly on different machines!  Make a note of your simulator settings (resolution and graphics quality set on launch) and frames per second (FPS output to terminal by `drive_rover.py`) in your writeup when you submit the project so your reviewer can reproduce your results.**

- Screen resolution: 1680 x 1050
- Windowed: Yes
- Graphics quality: Fantastic
- FPS (average): 11

I did not use maps to plan navigation for the robot. This is where I would do if I were going to persue this further. Furthermore, the robot does not collect the samples for now.

Besides those, the results are quite good, they meet or exceed the requirements every run. I believe the two techniques contribute most to the result are the unstuck mode and the keep left strategy. The HSV color detection is also good at detecting the sample in this simulated environment. However, sometimes the samples are not registered. This could be because of the inaccuracy in coordinates when the robot car is moving.



