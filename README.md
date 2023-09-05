<img src="https://user-images.githubusercontent.com/84031027/235169420-40efb062-281d-47a5-b4c5-0e07b14aab5b.png" width="250" height="250">


## The Problem:

How many times did you buy a clothing item online, got really excited and then got super disappointed when it arrived, and it didn't fit as well as you imagined?

Unfortunately - Online clothes shopping can be tricky because you can't try things on before they arrive, which can lead to disappointment if the fit or style isn't what you expected.


## The Solution:

E-commerce websites can be equipped with virtual dressing rooms that allow users to try on multiple clothes virtually and select the best-looking outfit.

It's never been easier to look fabulous!!!


## The Approach:

I created a Virtual clothing assistant using Deep learning algorithms in order to help the costumers.

The user can select the clothing item he/she wants to wear and then upload his/her image of any pose they want, and the assistant will help to dress that human with his/her selected clothing item.


*So how exactly does it work?*
1.  	Input - We allow the user to upload his/her image and their clothing item’s image. 

<img src="https://github.com/shirsneh/virtual_clothes_try_on_assistant/assets/84031027/b2e797ff-805d-4fd0-a433-b09d9a23c2ce" width="600" height="250">

2.  	Cloth mask - We create a cloth mask with U2Net. 

<img src="https://github.com/shirsneh/virtual_clothes_try_on_assistant/assets/84031027/03f5065a-f731-4261-a414-e54c8d3d22c8" width="400" height="200">

<img src="https://github.com/shirsneh/virtual_clothes_try_on_assistant/assets/84031027/6e2151c8-ebb2-4dac-8f96-0e069d7eb069" width="500" height="200">


3.  	Body position - We get a body position estimation and key points with Mediapipe.

<img src="https://github.com/shirsneh/virtual_clothes_try_on_assistant/assets/84031027/28049d38-3c88-44fc-974a-6183fecd3381" width="500" height="200">

<img src="https://github.com/shirsneh/virtual_clothes_try_on_assistant/assets/84031027/7ef1cfbd-31b3-4942-9c46-6b27d6f3102b" width="500" height="200">

</p>

4.  	Body parsing - We parse the user body with Self-Correction-Human-Parsing.

<img src="https://github.com/shirsneh/virtual_clothes_try_on_assistant/assets/84031027/12f0863e-1c97-4f15-b95e-7681b960a244" width="500" height="200">

<img src="https://github.com/shirsneh/virtual_clothes_try_on_assistant/assets/84031027/b8e9d64d-eea1-4f60-86aa-53ee4cf7b2d6" width="500" height="200">


5.    Body segmentation -
6.  	Generating the result - ALIASGenerator uses these to create the requested image.

<img src="https://user-images.githubusercontent.com/84031027/235325853-24748a7d-3db6-47f8-8aa0-7ed0ba804328.png" width="500" height="200">

6.    Output - a new image of the user wearing the requested item.

<img src="https://user-images.githubusercontent.com/84031027/235325952-43226aa0-21bf-4a6c-b73d-8d0d643e5bd2.png" width="150" height="150">

## Explanation about U2NET

A neural network architecture which is designed for image segmentation tasks. 

<img src="https://github.com/shirsneh/virtual_clothes_try_on_assistant/assets/84031027/f267e63b-0994-4031-b716-994e69bb8e8d" width="250" height="300">



A brief explanation of the code:

•	*REBNCONV class:* This is a basic building block of the network, consisting of a convolutional layer followed by batch normalization and ReLU activation.

•	*RSU (Recursive Supervision Unit) classes:* These classes define the network architecture, with each RSU containing multiple REBNCONV blocks. RSU7, RSU6, RSU5, RSU4, and RSU4F represent different levels of the network hierarchy, gradually reducing spatial dimensions while increasing feature channels.

•	*U2NET class:* This is the main U2Net architecture, composed of multiple RSU stages for feature extraction and a decoder section for feature expansion. It takes an input image and produces multiple side outputs at different scales, which are then concatenated and passed through a final convolutional layer to produce the segmentation mask.

•	*U2NETP class:* This is a smaller variant of U²-Net, designed for faster inference with lower computational resources. It follows a similar architecture but with fewer parameters and lower-resolution feature maps.

The code also includes operations for upsampling (_upsample_like) and side-output convolution layers (side1 through side6) to generate the final segmentation map.

Overall, U2Net and U2NetP are deep neural networks for semantic segmentation tasks, with U2Net being more complex and suitable for higher accuracy at the cost of increased computational requirements, while U2NetP is a smaller and faster variant designed for real-time or resource-constrained applications.

*Results:*

<img src="https://github.com/shirsneh/virtual_clothes_try_on_assistant/assets/84031027/880e43fc-3892-43d1-95eb-9e4538b77727" width="500" height="200">

<img src="https://github.com/shirsneh/virtual_clothes_try_on_assistant/assets/84031027/3b9b54eb-9807-4ea3-9620-19cfe4196f82" width="500" height="200">

<img src="https://github.com/shirsneh/virtual_clothes_try_on_assistant/assets/84031027/b3fbd464-db8c-4879-bfe1-83543b673fa3" width="500" height="200">

<img src="https://github.com/shirsneh/virtual_clothes_try_on_assistant/assets/84031027/de3d21bd-7984-4c9e-82d0-d42633a48907" width="500" height="200">


#### Based on a paper titled "U2-Net: Going Deeper with Nested U-Structure for Salient Object Detection" by Qin et al. in 2020. 
Link to the paper:  https://www.sciencedirect.com/science/article/abs/pii/S0031320320302077

#### Was trained with VITON-HD dataset
Link to the dataset: https://github.com/shadow2496/VITON-HD/tree/main

## Explanation about Mediapipe

Mediapipe is a versatile framework developed by Google that provides tools for building various computer vision and machine learning applications, including pose estimation. My code uses the Mediapipe library to perform pose estimation on the model image, saves the detected pose landmarks, and creates an annotated image for visualization.

Link for Mediapipe: https://developers.google.com/mediapipe/solutions

*Results:*

<img src="https://github.com/shirsneh/virtual_clothes_try_on_assistant/assets/84031027/92860997-fc6c-4c78-9e04-27283f863563" width="500" height="200">

<img src="https://github.com/shirsneh/virtual_clothes_try_on_assistant/assets/84031027/7ff160f2-e84d-4bb9-8e79-7510acc06c3f" width="500" height="200">

<img src="https://github.com/shirsneh/virtual_clothes_try_on_assistant/assets/84031027/222aa9f4-f378-4251-aad8-d799da41818c" width="500" height="200">

<img src="https://github.com/shirsneh/virtual_clothes_try_on_assistant/assets/84031027/f8213e12-f08f-48a3-9dd2-31533f40ac56" width="500" height="200">


## Explanation about Self-Correction-Human-Parsing

semantic segmentation of human body parts or clothing in images using a deep neural network. It provides flexibility in choosing the dataset, specifying input and output directories, and optionally saving logits for further analysis. 

Link for Self-Correction-Human-Parsing: https://github.com/GoGoDuck912/Self-Correction-Human-Parsing

*Results:*

<img src="https://github.com/shirsneh/virtual_clothes_try_on_assistant/assets/84031027/0899809b-621c-4561-bf40-5cd6051ec9dd" width="500" height="200">

<img src="https://github.com/shirsneh/virtual_clothes_try_on_assistant/assets/84031027/b98cfcc2-5e9d-41e9-88ad-84ea08a2403b" width="500" height="200">

<img src="https://github.com/shirsneh/virtual_clothes_try_on_assistant/assets/84031027/f19c2cd3-f504-4e62-8d0f-dac3214e2eba" width="500" height="200">

<img src="https://github.com/shirsneh/virtual_clothes_try_on_assistant/assets/84031027/4e461912-fea4-4bfd-9ae4-698d3400b18b" width="500" height="200">


## Project presentation

[project presentation.pptx](https://github.com/shirsneh/virtual_clothes_try_on_assistant/files/11360128/project.presentation.pptx)


## Resources

VITON-HD Dataset - https://paperswithcode.com/dataset/viton-hd

U2Net - "U2-Net: Going Deeper with Nested U-Structure for Salient Object Detection" by Qin et al. in 2020.  
https://www.sciencedirect.com/science/article/abs/pii/S0031320320302077

Mediapipe - https://developers.google.com/mediapipe/solutions

Self-Correction-Human-Parsing - https://github.com/GoGoDuck912/Self-Correction-Human-Parsing

