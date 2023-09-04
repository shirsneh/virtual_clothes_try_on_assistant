import json
import cv2
import numpy as np
from PIL import Image
import mediapipe as mp
import os


# running the preprocessing

def resize_img(path):
    im = Image.open(path)
    im = im.resize((768, 1024))
    im.save(path)


for path in os.listdir('/content/inputs/test/cloth/'):
    resize_img(f'/content/inputs/test/cloth/{path}')

os.chdir('/content/virtual_clothes_try_on_assistant')
os.system("rm -rf /content/inputs/test/cloth/.ipynb_checkpoints")
os.system("python cloth-mask.py")
os.chdir('/content')
os.system("python /content/virtual_clothes_try_on_assistant/remove_bg.py")
print("after remove_bg")
os.system(
    "python3 /content/Self-Correction-Human-Parsing/simple_extractor.py --dataset 'lip' --model-restore "
    "'/content/Self-Correction-Human-Parsing/checkpoints/final.pth' --input-dir '/content/inputs/test/image' "
    "--output-dir '/content/inputs/test/image-parse'")
os.chdir('/content')

mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=True, min_detection_confidence=0.5)
input_image_dir = '/content/inputs/test/image/'
mediapipe_json_dir = '/content/inputs/test/mediapipe_json/'
mediapipe_img_dir = '/content/inputs/test/mediapipe_img/'
openpose_json_dir = '/content/inputs/test/openpose_json/'
os.makedirs(openpose_json_dir, exist_ok=True)
for image_path in os.listdir(input_image_dir):
    image = cv2.imread(os.path.join(input_image_dir, image_path))
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = pose.process(image_rgb)
    keypoints = results.pose_landmarks
    openpose_data = {
        "version": 1.0,
        "people": []
    }
    if keypoints:
        person_data = {
            "person_id": 1,
            "pose_keypoints_2d": []
        }
        for landmark in keypoints.landmark:
            x = landmark.x
            y = landmark.y
            confidence = landmark.z  # Use the z-coordinate as confidence
            person_data["pose_keypoints_2d"].extend([x, y, confidence])
        openpose_data["people"].append(person_data)
        json_filename = image_path.replace('.jpg', '.json')
        json_path = os.path.join(openpose_json_dir, json_filename)
        with open(json_path, 'w') as json_file:
            json.dump(openpose_data, json_file)
    annotated_image = image.copy()
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing.draw_landmarks(annotated_image, keypoints, mp_pose.POSE_CONNECTIONS)
    img_path = os.path.join(mediapipe_img_dir, image_path.replace('.jpg', '_pose.jpg'))
    cv2.imwrite(img_path, annotated_image)
pose.close()

for image_path in os.listdir(input_image_dir):
    image = cv2.imread(os.path.join(input_image_dir, image_path))
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image_21_channels = np.zeros((image_rgb.shape[0], image_rgb.shape[1], 21))
    image_21_channels[:, :, :3] = image_rgb

# os.system(
#     "cd openpose && ./build/examples/openpose/openpose.bin --image_dir /content/inputs/test/image/ --display 0 --render_pose 0 --hand --write_json '/content/inputs/test/openpose-json/'")
# os.system(
#     "cd openpose && ./build/examples/openpose/openpose.bin --image_dir /content/inputs/test/image/ --display 0 --hand --render_pose 1 --disable_blending true --write_images '/content/inputs/test/openpose-img/'")

model_image = os.listdir('/content/inputs/test/image')
cloth_image = os.listdir('/content/inputs/test/cloth')
pairs = zip(model_image, cloth_image)

with open('/content/inputs/test_pairs.txt', 'w') as file:
    for model, cloth in pairs:
        file.write(f"{model} {cloth}")

# making predictions
os.system(
    "python /content/virtual_clothes_try_on_assistant/test.py --name output --dataset_dir /content/inputs --checkpoint_dir /content/virtual_clothes_try_on_assistant/checkpoints --save_dir /content/")
# os.system("rm -rf /content/inputs")
os.system("rm -rf /content/output/.ipynb_checkpoints")