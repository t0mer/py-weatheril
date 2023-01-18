import os
import glob
import requests
import uuid
from PIL import Image
from urllib.parse import urlparse

class RadarSatellite:
    imsradar_images: list
    radar_images: list
    middle_east_satellite_images: list
    europe_satellite_images: list

    def __init__(self,imsradar_images: list=[], radar_images: list=[],middle_east_satellite_images: list=[],europe_satellite_images: list=[]):
        self.imsradar_images = imsradar_images
        self.radar_images = radar_images
        self.middle_east_satellite_images = middle_east_satellite_images
        self.europe_satellite_images = europe_satellite_images


    def create_animation(self,path: str = None, images: list=[]):
        if path is not None and os.path.exists(path):
            animated_image = path + "/" + str(uuid.uuid4()) + ".gif"
        else:
            animated_image = os.path.realpath(os.path.dirname(__file__)) + "/" + str(uuid.uuid4()) + ".gif"

                
        extention = os.path.splitext(images[0])[1]

        if not os.path.exists("images"):
            os.makedirs("images")

        for idx, item in enumerate(images):
            file = requests.get(images[idx])
            open("images/" + os.path.basename(urlparse(images[idx]).path), "wb").write(file.content)
            images[idx] = "images/" + os.path.basename(urlparse(images[idx]).path)
        
        frames = [Image.open(image) for image in images]
        frame_one = frames[0]
        frame_one.save(animated_image, format="GIF", append_images=frames,save_all=True, loop=0)

        for image in images:
            print(image)
            os.remove(image)
        return animated_image