
from loadChange import *
from diftCalc import callDift
from imageDisplay import displayImages, convertPIL
from dataTransfer import *
def diftChange(oscar):
    """
    Pipeline steps: 
    1. load annotated frames + their category and some way of naming them. 
    2. generate random points for each initial state. 
    3. run dift algorithm. 

    dift project has images in 270 x 480 but ocnverts them to 768 x 768. DOes this in the diffusion call. Need to generate points in the final size. 
    """
    numPoints = 100
    desiredSize = (480, 270)
    finalSize = (768, 768)
    path = getPathChange(oscar)
    #this method screws up the colors of the image.
    params, catList = loadCenteringParams(path)
    listCatFrames = []
    for cat in catList:
        frame = loadFramesPreDownloaded(cat, path, desiredSize)
        listCatFrames.append(frame)
    frames = np.vstack(listCatFrames)
    print("category frames shape: ", frames.shape)
    numVideos = frames.shape[0]
    print("number of videos to process: ", numVideos)
    #still need to save these points because can't display in oscar.
   
    points = generateRandomPoints(numVideos, numPoints, finalSize)
    #gets results and saves them. 
    resultPoints = callDift(frames, points)
def generateRandomPoints(numVideos, numPoints, desiredSize):
    """
    Videos shape: numVideos x 3 x desiredSize[0] x desiredSize[1] x 3
    HOWEVER: Need to generate random points in the range of the final image size. 
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
        print("divided: ", randPoints/desiredSize[0])
        #correct here. 
        xCoord = (randPoints/desiredSize[0]).astype(int)
        print("x coord: ", xCoord)
        #.astype shouldnt' round at all here. 
        #correct here. 
        yCoord = (randPoints%desiredSize[1]).astype(int)
        coords = np.stack([xCoord,yCoord]).T
        print("coords shape: ", coords.shape)
        assert(coords.shape == (numPoints, 2))
        listPoints.append(coords)
    return np.stack(listPoints, dtype = int)
def loadAndDisplay():
    num_images = 5
    for i in range(num_images):
        points = loadPoints(str(i), False)
        beginningImage, endImage = loadImages(str(i), False)
        results = loadResults(str(i), False)
        displayImages(beginningImage, endImage, points, results)
diftChange(False)
#loadAndDisplay()
