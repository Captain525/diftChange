import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from PIL import Image
def displayImageList(beginningImage, imageList, initPoints, resultsArray):
     """
     Display images method for thing with multiple result frames. 
     beginning image - one PIL image of first thing. 

     See TODO in loadAndDisplay - could make them all one loop for ease of use. 
     """
     numImages = len(imageList)
     fig_size = 3
     scatter_size = 70
     fig, axes = plt.subplots(1, numImages+1, figsize = ((numImages+1)*fig_size, fig_size))
     plt.tight_layout()
     #want numPoints
     print(resultsArray.shape)
     colors = cm.rainbow(np.linspace(0, 1,resultsArray.shape[1]))
     axes[0].clear()
     axes[0].imshow(beginningImage)
     axes[0].scatter(initPoints[:, 0], initPoints[:, 1], c=colors, s=scatter_size)
     axes[0].set_title('source image')
     for i in range(numImages):
          results = resultsArray[i]
          axes[i+1].clear()
          axes[i+1].imshow(imageList[i])
          axes[i+1].scatter(results[:,0], results[:, 1], c=colors, s=scatter_size)
          axes[i+1].set_title("result image number: {}".format(i+1))
     plt.show()
def displayImages(beginningImage, endImage, initPoints, endPoints):
    """
    Old image display method for when we just cared about beginning and end image. 
    """
    fig_size = 3
    scatter_size = 70
    fig, axes = plt.subplots(1, 2, figsize=(2*fig_size, fig_size))
    plt.tight_layout()
    images = [beginningImage, endImage]
    print(endPoints.shape)
    colors = cm.rainbow(np.linspace(0, 1,endPoints.shape[0]))
    """
    #I think this section was useless, haven't tested it yet because switched to a different method. 
    for i in range(2):
            axes[i].imshow(images[i])
            axes[i].axis('off')
            if i == 0:
                axes[i].set_title('source image')
            else:
                axes[i].set_title('target image')
    """
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
    axes[1].set_title('target image')
    plt.show()
def convertPIL(imageArray, img_size):
    #open cv uses BGR, image uses RGB
    image = Image.fromarray(np.uint8(imageArray), "RGB")
    image = image.resize((img_size, img_size))
    return image
def displayFrames(frames):
    """
    Displays the n extracted frames from all the frames. 
    Basically same as displayIMages but without the points. 
    """
    numFrames = frames.shape[0]
    fig_size = 3
    scatter_size = 70
    fig, axes = plt.subplots(1, numFrames, figsize=(numFrames*fig_size, fig_size))

    plt.tight_layout()
    for i in range(numFrames):
            axes[i].imshow(convertPIL(frames[i], 768))
            axes[i].axis('off')
            if i == 0:
                axes[i].set_title('init image')
            else:
                axes[i].set_title('target image')
    plt.show()
