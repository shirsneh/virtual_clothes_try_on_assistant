from PIL import Image
import os


# running the preprocessing

def resize_img(path):
    im = Image.open(path)
    im = im.resize((768, 1024))
    im.save(path)


for path in os.listdir('/content/inputs/test/clothing_item/'):
    resize_img(f'/content/inputs/test/clothing_item/{path}')

os.chdir('/content/virtual_clothes_try_on_assistant')
os.system("rm -rf /content/inputs/test/clothing_item/.ipynb_checkpoints")
os.system("python utils/cloth_mask.py")
print("after cloth_mask")
os.chdir('/content')
os.system("python /content/virtual_clothes_try_on_assistant/utils/remove_bg.py")
print("after remove_bg")
os.system("python3 /content/Self-Correction-Human-Parsing/simple_extractor.py --dataset 'lip' --model-restore '/content/Self-Correction-Human-Parsing/checkpoints/final.pth' --input-dir '/content/inputs/test/image' --output-dir '/content/inputs/test/image-parse'")
os.chdir('/content')
os.system("cd openpose && ./build/examples/openpose/openpose.bin --image_dir /content/inputs/test/image/ --write_json /content/inputs/test/openpose-json/ --display 0 --render_pose 0 --hand")
os.system("cd openpose && ./build/examples/openpose/openpose.bin --image_dir /content/inputs/test/image/ --display 0 --write_images /content/inputs/test/openpose-image/ --hand --render_pose 1 --disable_blending true")

model_image = os.listdir('/content/inputs/test/image')
print("model_image")
clothing_item_image = os.listdir('/content/inputs/test/clothing_item')
print("clothing_item_image")
pairs = zip(model_image, clothing_item_image)

with open('/content/inputs/test_pairs.txt', 'w') as file:
    for model, clothing_item in pairs:
        file.write(f"{model} {clothing_item}")

# making predictions
os.system("python /content/virtual_clothes_try_on_assistant/test.py --name output --dataset_dir /content/inputs --checkpoint_dir /content/virtual_clothes_try_on_assistant/checkpoints --save_dir /content/")
# os.system("rm -rf /content/inputs")
# os.system("rm -rf /content/output/.ipynb_checkpoints")