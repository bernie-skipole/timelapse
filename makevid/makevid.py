
"""
Create the video, code derived from

https://www.geeksforgeeks.org/python/python-create-video-using-multiple-images-using-opencv/

Gets images from /home/bernard/git/timelapse/images2
and creates movie file movie.avi

Requires environment with opencv-python

"""

import os
import cv2


def generate_video(path):

    images = [img for img in os.listdir(path) if img.endswith(".jpeg")] 
    images.sort()

    # Set frame from the first image
    frame = cv2.imread(os.path.join(path, images[0]))
    height, width, layers = frame.shape

    # Video writer to create .avi file
    video = cv2.VideoWriter("movie.avi", cv2.VideoWriter_fourcc(*'DIVX'), 10, (width, height))

    # Appending images to video
    for image in images:
        video.write(cv2.imread(os.path.join(path, image)))
        print(image)

    # Release the video file
    video.release()
    cv2.destroyAllWindows()
    print("Video generated successfully!")


if __name__ == "__main__":

    path = "/home/bernard/git/timelapse/images2"

    # Calling the function to generate the video
    generate_video(path)
