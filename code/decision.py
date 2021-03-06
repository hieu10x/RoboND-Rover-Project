import numpy as np
import time
import random


def from_polar_coords(d, a):
    return int(d * np.cos(a)), int(d * np.sin(a))

# This is where you can build a decision tree for determining throttle, brake and steer
# commands based on the output of the perception_step() function
def decision_step(Rover):

    # Implement conditionals to decide what to do given perception data
    # Here you're all set up with some basic functionality but you'll need to
    # improve on this decision tree to do a good job of navigating autonomously!
    # Check if we have vision data to make decisions with
    if Rover.nav_angles is not None:
        t = time.time()
        # every 60 seconds, check if stuck
        if t - Rover.last_map_check > 60:
            Rover.last_map_check = t
            mapped_area = np.sum(Rover.worldmap[:, :, 2] > 0)
            if Rover.mapped_area >= mapped_area:
                Rover.mode = 'unstuck'
            Rover.mapped_area = mapped_area
        # Check for Rover.mode status
        if Rover.mode == 'forward':
            # Check the extent of navigable terrain
            # If there's a lack of navigable terrain pixels then go to 'stop' mode
            if len(Rover.nav_angles) < Rover.stop_forward or np.max(Rover.nav_dists) < 40:
                    # Set mode to "stop" and hit the brakes!
                    Rover.throttle = 0
                    # Set brake to stored brake value
                    Rover.brake = Rover.brake_set
                    Rover.steer = 0
                    Rover.mode = 'stop'
                    print("MODE STOP")
            else:
                # If mode is forward, navigable terrain looks good
                # and velocity is below max, then throttle
                if Rover.vel < Rover.max_vel:
                    # Set throttle value to throttle setting
                    Rover.throttle = Rover.throttle_set
                else: # Else coast
                    Rover.throttle = 0
                Rover.brake = 0
                # Set steering to average angle clipped to the range +/- 15
                # Average
                if (np.sum(Rover.nav_dists > 10) > 0):
                    max_angle = np.max(Rover.nav_angles[Rover.nav_dists > 10])
                    Rover.steer = np.clip((np.mean(Rover.nav_angles) * 8 + max_angle) / 9 * 180/np.pi, -15, 15)
                else:
                    Rover.steer = np.clip(np.mean(Rover.nav_angles) * 180 / np.pi, -15, 15)

        # If we're already in "stop" mode then make different decisions
        elif Rover.mode == 'stop':
            # If we're in stop mode but still moving keep braking
            if Rover.vel > 0.2:
                Rover.throttle = 0
                Rover.brake = Rover.brake_set
                Rover.steer = 0
            # If we're not moving (vel < 0.2) then do something else
            elif Rover.vel <= 0.2:
                # Now we're stopped and we have vision data to see if there's a path forward
                if len(Rover.nav_angles) < Rover.go_forward:
                    Rover.throttle = 0
                    # Release the brake to allow turning
                    Rover.brake = 0
                    # Turn range is +/- 15 degrees, when stopped the next line will induce 4-wheel turning
                    # obstacle on the left, turn right
                    if (int(time.time()) / 60) % 2 == 0:
                        Rover.steer = -15
                    else:
                        Rover.steer = 15
                # If we're stopped but see sufficient navigable terrain in front then go!
                if len(Rover.nav_angles) >= Rover.go_forward and np.max(Rover.nav_dists) > 40:
                    # Set throttle back to stored value
                    Rover.throttle = Rover.throttle_set
                    # Release the brake
                    Rover.brake = 0
                    # Set steer to mean angle
                    Rover.steer = np.clip(np.mean(Rover.nav_angles) * 180 / np.pi, -15, 15)
                    Rover.mode = 'forward'
        elif Rover.mode == 'unstuck':
            print("MODE UNSTUCK", Rover.random_angle)
            if Rover.vel > 0.2:
                Rover.throttle = 0
                Rover.brake = Rover.brake_set
                Rover.steer = 0
                Rover.random_angle = random.random() * 360
            # If we're not moving (vel < 0.2) then do something else
            elif Rover.vel <= 0.2:
                # Now we're stopped and we have vision data to see if there's a path forward
                if np.absolute(Rover.yaw - Rover.random_angle) < 10:
                    Rover.mode = 'forward'
                else:
                    Rover.throttle = 0
                    Rover.brake = 0
                    if (int(time.time()) / 60) % 2 == 0:
                        Rover.steer = -15
                    else:
                        Rover.steer = 15

    # Just to make the rover do something
    # even if no modifications have been made to the code
    else:
        Rover.throttle = Rover.throttle_set
        Rover.steer = 0
        Rover.brake = 0

    return Rover

