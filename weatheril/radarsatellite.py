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


    def create_animation(self, images: list=[]):
        animated_image = str(uuid.uuid4()) + ".gif"
        extention = os.path.splitext(images[0])[1]

        if not os.path.exists("images"):
            os.makedirs("images")
        for image in images:
            file = requests.get(image)
            open("images/" + os.path.basename(urlparse(image).path), "wb").write(file.content)
        frames = [Image.open(image) for image in glob.glob("images/*" + extention)]
        frame_one = frames[0]
        frame_one.save(animated_image, format="GIF", append_images=frames,save_all=True, loop=0)

        for image in images:
            os.remove("images/" + os.path.basename(urlparse(image).path))
        return animated_image