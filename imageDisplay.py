import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from PIL import Image
def displayImages(beginningImage, endImage, initPoints, endPoints):
    fig_size = 3
    scatter_size = 70
    fig, axes = plt.subplots(1, 2, figsize=(2*fig_size, fig_size))
    plt.tight_layout()
    images = [beginningImage, endImage]
    print(endPoints.shape)
    colors = cm.rainbow(np.linspace(0, 1,endPoints.shape[0]))
    for i in range(2):
            axes[i].imshow(images[i])
            axes[i].axis('off')
            if i == 0:
                axes[i].set_title('source image')
            else:
                axes[i].set_title('target image')
    #stuff from later
    axes[0].clear()
    axes[0].imshow(images[0])
    axes[0].axis('off')
    #x values
    axes[0].scatter(initPoints[:, 0], initPoints[:, 1], c=colors, s=scatter_size)
    axes[0].set_title('source image')

    axes[1].clear()
    axes[1].imshow(images[1])
    axes[1].scatter(endPoints[:, 0], endPoints[:,1], c=colors, s=scatter_size)
    axes[i].set_title('target image')
    plt.show()
def convertPIL(imageArray, img_size):
    #open cv uses BGR, image uses RGB
    image = Image.fromarray(np.uint8(imageArray), "RGB")
    image = image.resize((img_size, img_size))
    return image
def displayFrames(frames):
    """
    Displays the three extracted frames from all the frames. 

    """
    fig_size = 3
    scatter_size = 70
    fig, axes = plt.subplots(1, 3, figsize=(3*fig_size, fig_size))

    plt.tight_layout()
    for i in range(3):
            axes[i].imshow(convertPIL(frames[i], 768))
            axes[i].axis('off')
            if i == 0:
                axes[i].set_title('init image')
            elif i==1:
                 axes[i].set_title('action image')
            else:
                axes[i].set_title('target image')
    plt.show()
def makeIntoImageAndDisplay(frame):
     Image.show(frame)
