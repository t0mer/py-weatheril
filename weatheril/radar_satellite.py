from __future__ import annotations
import os
import glob
import uuid
import tempfile
import requests
from PIL import Image
from loguru import logger
from urllib.parse import urlparse
from dataclasses import dataclass, field


@dataclass
class RadarSatellite:
    imsradar_images: list
    radar_images: list
    middle_east_satellite_images: list
    europe_satellite_images: list

    def __init__(
        self,
        imsradar_images: list = [],
        radar_images: list = [],
        middle_east_satellite_images: list = [],
        europe_satellite_images: list = [],
    ):
        self.imsradar_images = imsradar_images
        self.radar_images = radar_images
        self.middle_east_satellite_images = middle_east_satellite_images
        self.europe_satellite_images = europe_satellite_images

    def generate_images(self, path: str = ""):
        self.create_animation("imsradar.gif", self.imsradar_images, path)
        self.create_animation("radar.gif", self.radar_images, path)
        self.create_animation(
            "middle_east.gif", self.middle_east_satellite_images, path
        )
        self.create_animation("europe.gif", self.europe_satellite_images, path)

    def create_animation(self, animated_file: str, images: list, path: str):
        """
        This method will download the images needed to create animated Radar / Satellite image
        parameters:
            >>> path: path to save the animated image. if path wil not be provided, the default path will be the current one.
            >>> animated_file: The name of the animated file
            >>> images: the list of images for creating the animation.
        """
        try:
            if os.path.exists(path):
                animated_image_path = path + "/" + animated_file
            else:
                animated_image_path = (
                    os.path.realpath(os.path.dirname(__file__)) + "/" + animated_file
                )
            logger.debug(
                "Creating " + animated_file + " animation at: " + animated_image_path
            )

            for idx, item in enumerate(images):
                file = requests.get(images[idx])
                open(
                    tempfile.gettempdir()
                    + "/"
                    + os.path.basename(urlparse(images[idx]).path),
                    "wb",
                ).write(file.content)
                images[idx] = (
                    tempfile.gettempdir()
                    + "/"
                    + os.path.basename(urlparse(images[idx]).path)
                )

            frames = [Image.open(image) for image in images]
            frame_one = frames[0]
            frame_one.save(
                animated_image_path,
                format="GIF",
                append_images=frames,
                save_all=True,
                duration=4,
                loop=0,
            )

            for image in images:
                os.remove(image)
            return animated_image_path
        except Exception as e:
            logger.error("Error creating " + animated_file + " animation. " + str(e))
            return None
