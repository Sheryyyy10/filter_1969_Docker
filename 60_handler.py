import os
import time
import random
import requests
import tempfile
import uuid
from PIL import Image
from deepface import DeepFace
import runpod

# Define media directory
MEDIA_DIR = "media"
os.makedirs(MEDIA_DIR, exist_ok=True)

# Face swap API details
API_URL = "https://faceswap.cognise.art/api/face_fusion_push/?adeel"
HEADERS = {"Authorization": "Token b0b35e6bc00d39023d7bb569d8c8e753f8374d31"}

# Hardcoded Image URL
# HARDCODED_IMAGE_URL = "https://storage.cognise.art/media/faceswap/outputs/3acdddc9-d1ba-42f1-8f4c-383d67595917.png"


def get_gender_race(image_path):
    """Analyzes gender and race of a given image."""
    objs = DeepFace.analyze(img_path=image_path, actions=["gender", "race"])
    result = objs[0]
    return result["dominant_gender"].lower(), result["dominant_race"].lower()


def handler(job):
    """Processes face swap jobs in a serverless function."""
    try:
        image_url = job.get("image_url")
        if not image_url:
            return {"error": "No image URL provided"}

        # Download Image
        response = requests.get(image_url)
        if response.status_code != 200:
            return {"error": "Failed to download image"}

        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
            temp_file.write(response.content)
            temp_image_path = temp_file.name

        # Identify Gender & Race
        gender, race = get_gender_race(temp_image_path)

        # Select Target Image
        race_mapping = {"middle eastern": "indian", "latino hispanic": "asian", "indian": "indian", "asian": "asian"}
        race_folder = race_mapping.get(race, race)
        gender_folder = "Man" if "man" in gender.lower() else "Woman"
        target_img_path = os.path.join("data", race_folder, gender_folder, f"{random.randint(1, 7)}.png")

        if not os.path.exists(target_img_path):
            return {"error": "Target image not found"}

        # Perform Face Swap
        with open(temp_image_path, "rb") as source_img, open(target_img_path, "rb") as target_img:
            files = {"source_path": source_img, "target_path": target_img}
            data = {
                "reference_face_position": "2",
                "face_analyzer_order": "left-right",
                "multiple_faces": "false",
                "api_key": "face_fusion-6cba92e9-4e3d-4340-a277-78b837e7f09d",
                "packagename": "com.testing",
                "time_zone": "Asia/Karachi"
            }
            swap_response = requests.post(API_URL, headers=HEADERS, files=files, data=data)

        os.remove(temp_image_path)

        if swap_response.status_code == 200:
            swap_data = swap_response.json()
            output_path = swap_data.get("output_path", "")

            if not output_path:
                return {"error": "Face swap response did not return an output path"}

            return {"status": "success", "output_path": output_path}
        else:
            return {"error": "Face swap failed", "response": swap_response.text}

    except Exception as e:
        return {"error": str(e)}

# RunPod Serverless Start
if __name__ == '__main__':
    runpod.serverless.start({"handler": handler})
