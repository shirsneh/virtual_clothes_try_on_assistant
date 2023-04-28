<img src="https://user-images.githubusercontent.com/84031027/235169420-40efb062-281d-47a5-b4c5-0e07b14aab5b.png" width="250" height="250">


## The Problem:

How many times did you buy a clothing item online, got really exited and then got super disapointed when it arrived and it didn't fit as well as you imagined?

Unfortunately - While buying clothes online, it is difficult for a customer to select a desirable outfit in the first attempt because they can’t try on clothes before they are delivered physically.

## The Solution:

E-commerce websites can be equipped with virtual dressing rooms that allow users to try on multiple clothes virtually and select the best looking outfit.

It's never been easier to look fabulous!!!

## The Approach:

I created a Virtual clothing assistant using Deep learning algorithms in order to help the consumers.

The user can select the cloth he/she wants to wear and then upload his/her image of any pose they want and the assistant will help to dress that human with his/her selected cloth.

*So how exactly does it work?*
1.  	We allow the user to upload his/her image and their clothing item’s image.
<img src="https://user-images.githubusercontent.com/84031027/235174964-bdeb18cb-8ff8-44e4-b172-d5b589110979.png" width="800" height="250">

2.  	We create a cloth mask with Mask R-CNN.
<p float="left">
  <img src="https://user-images.githubusercontent.com/84031027/235176316-3c09f007-a8eb-4efc-ae48-4b95bae0bd6f.jpg" width="200" height="200">
  <img src="https://user-images.githubusercontent.com/84031027/235176735-98fbd32d-b168-4065-ac88-749b56e20315.png" width="200" height="200">
</p>

3.  	We get a body position estimation and keypoints with open pose.
<p float="left">
  <img src="https://user-images.githubusercontent.com/84031027/235178057-99749252-8871-40ae-8b49-073425e24e97.png" width="200" height="300">
  <img src="https://user-images.githubusercontent.com/84031027/235177861-e20bec1d-42a0-41ba-b8d4-f7137970065c.png" width="200" height="300">
</p>

4.  	We segment the user body with U2Net.
<p float="left">
  <img src="https://user-images.githubusercontent.com/84031027/235178057-99749252-8871-40ae-8b49-073425e24e97.png" width="200" height="300">
  <img src="https://user-images.githubusercontent.com/84031027/235179179-cf1294e8-07db-47c0-af11-3c9f6ae8a0c6.png" width="200" height="300">
</p>

5.  	These are used to create a new image of the user wearing the requested cloth item. The image is created using ALIASGenerator.

