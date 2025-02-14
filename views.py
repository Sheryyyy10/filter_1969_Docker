import os
import time
import random
import requests
import cv2
from deepface import DeepFace
from django.http import JsonResponse
from rest_framework.views import APIView
from io import BytesIO
from PIL import Image
from Api.storage import *
import uuid
import time


# Define media directory
MEDIA_DIR = "media"
os.makedirs(MEDIA_DIR, exist_ok=True)

api_url = "https://faceswap.cognise.art/api/face_fusion_push/?adeel"
headers = {"Authorization": "Token b0b35e6bc00d39023d7bb569d8c8e753f8374d31"}
# Server details (replace with actual value

def get_gender_race(image_path):
    objs = DeepFace.analyze(img_path=image_path, actions=["gender", "race"])
    result = objs[0]
    print(result)
    return result["dominant_gender"].lower(), result["dominant_race"].lower()



class FaceSwapAPI(APIView):
    def post(self, request, *args, **kwargs):
        try:
            image_url = request.data.get("image_url")
            if not image_url:
                return JsonResponse({"status": "error", "message": "No image URL provided"}, status=400)

            im = time.time()
            response = requests.get(image_url)
            if response.status_code != 200:
                return JsonResponse({"status": "error", "message": "Failed to download image"}, status=400)




            temp_image_path = os.path.join(MEDIA_DIR, f"temp_image_{uuid.uuid4()}.jpg")
            with open(temp_image_path, "wb") as f:
                f.write(response.content)

            im_e = time.time()


            gender_time = time.time()

            gender, race = get_gender_race(temp_image_path)

            gender_end = time.time()
            race_mapping = {"middle eastern": "indian", "latino hispanic": "asian", "indian": "indian", "asian": "asian"}
            race_folder = race_mapping.get(race, race)
            gender_folder = "Man" if "man" in gender.lower() else "Woman"
            target_img = os.path.join("data", race_folder, gender_folder, f"{random.randint(1, 7)}.png")

            if not os.path.exists(target_img):
                return JsonResponse({"status": "error", "message": "Target image not found"}, status=400)

            swap_start = time.time()
            files = {
                "source_path": open(temp_image_path, "rb"),
                "target_path": open(target_img, "rb")
            }
            data = {
                "reference_face_position": "2",
                "face_analyzer_order": "left-right",
                "multiple_faces": "false",
                "api_key": "face_fusion-6cba92e9-4e3d-4340-a277-78b837e7f09d",
                "packagename": "com.testing",
                "time_zone": "Asia/Karachi"
            }

            swap_response = requests.post(api_url, headers=headers, files=files, data=data)
            os.remove(temp_image_path)
            end_swap = time.time()

            if swap_response.status_code == 200:
                swap_data = swap_response.json()
                output_path = swap_data.get("output_path", "")

                if not output_path:
                    return JsonResponse({"status": "error", "message": "Face swap response did not return an output path"}, status=500)

                # # Construct full image URL
                # base_url = swap_data.get("base_url", "").rstrip("/")
                # full_image_url = f"{base_url}{output_path}"
                #
                # # Download the swapped image
                # swapped_image_response = requests.get(full_image_url)
                # if swapped_image_response.status_code != 200:
                #     return JsonResponse({"status": "error", "message": "Failed to download swapped image"}, status=500)
                #
                # # Save the swapped image temporarily
                # swapped_image_path = os.path.join(MEDIA_DIR, "swapped_image.jpg")
                # with open(swapped_image_path, "wb") as f:
                #     f.write(swapped_image_response.content)
                #
                # # Upload to storage
                # with open(swapped_image_path, "rb") as img_file:
                #     uploaded_image_path = postUserImages(img_file, "faceswap", "face_swap_result", ".jpg")

                # os.remove(output_path)  # Cleanup
                print("im download: ", im_e-im)
                print("gender time: ", gender_end - gender_time)
                print("face swap time: ", end_swap - swap_start)
                return JsonResponse({
                    "status": "success",
                    "output_path": output_path,
                 })

            else:
                return JsonResponse({"status": "error", "message": "Face swap failed", "response": swap_response.text}, status=500)

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
