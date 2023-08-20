
import numpy as np
from loadChange import loadFramesPreDownloaded
from diftCalc import callDift
from dataTransfer import loadListDownloaded

def diftChange(oscar):
    """
    Pipeline steps: 
    1. load annotated frames + their category and some way of naming them. 
    2. generate random points for each initial state. 
    3. run dift algorithm. 

    dift project has images in 270 x 480 but ocnverts them to 768 x 768. DOes this in the diffusion call. Need to generate points in the final size.

    THis is the main method, does everything once the videos are downloaded. Call this with a gpu. 
    """
    numPoints = 100
    desiredSize = (480, 270)
    finalSize = (768, 768)
    #load the list of downloaded files names and the list of links to those files on youtube. 
    listDownloaded, listLinks = loadListDownloaded(oscar)
    #load the frames from the predownloaded videos. 
    frames = loadFramesPreDownloaded(listDownloaded, listLinks,desiredSize, oscar)
    #numVideos x 4 x 270 x 480 x 3
    print("category frames shape: ", frames.shape)
    numVideos = frames.shape[0]
    print("number of videos to process: ", numVideos)
    #still need to save these points because can't display in oscar.
    points = generateRandomPoints(numVideos, numPoints, finalSize)
    #gets results and saves them. 
    resultPoints = callDift(frames, points, listDownloaded, oscar)
    print("results shape: ", resultPoints.shape)
    
def generateRandomPoints(numVideos, numPoints, desiredSize):
    """
    Videos shape: numVideos x 3 x desiredSize[0] x desiredSize[1] x 3
    Should I move this method somewhere else? 
    """

    #uniform points but no repeats. generate random in each direction but need a way to check and regenerate. 
    listPoints = []
    for i in range(numVideos):
        pointCount = 0
        uniqueArr = np.zeros(shape = (1,))
        while pointCount< numPoints+1:
            randomValues = np.random.randint(0, desiredSize[0]*desiredSize[1], size = numPoints)
            arr = np.concatenate([uniqueArr, randomValues], axis=0)
            uniqueRandom = np.unique(arr)
            uniqueArr = uniqueRandom
            pointCount = uniqueRandom.shape[0]
        #convert to 2d
        # look at which coord which. 
        randPoints = uniqueArr[1:numPoints+1]
        #not sure if x and y coords are right. 
        #.astype should round down if working as intended for first one. 
        #print("divided: ", randPoints/desiredSize[0])
        #correct here. 
        xCoord = (randPoints/desiredSize[0]).astype(int)
        #print("x coord: ", xCoord)
        #.astype shouldnt' round at all here. 
        #correct here. 
        yCoord = (randPoints%desiredSize[1]).astype(int)
        coords = np.stack([xCoord,yCoord]).T
        #print("coords shape: ", coords.shape)
        assert(coords.shape == (numPoints, 2))
        listPoints.append(coords)
    return np.stack(listPoints, dtype = int)

diftChange(True)
#loadAndDisplay()
