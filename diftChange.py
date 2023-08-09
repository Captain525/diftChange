
from loadChange import *
from diftCalc import callDift
from imageDisplay import displayImages, convertPIL
from dataTransfer import saveImages
def diftChange(oscar):
    """
    Pipeline steps: 
    1. load annotated frames + their category and some way of naming them. 
    2. generate random points for each initial state. 
    3. run dift algorithm. 

    dift project has images in 270 x 480 but ocnverts them to 768 x 768. DOes this in the diffusion call. Need to generate points in the final size. 
    """
    numPoints = 10 
    #x,y
    desiredSize = (480, 270)
    finalSize = (768, 768)
    path =   "/mnt/c/Users/dheff/CodingProjects/PythonProjects/PALM Research/data/ChangeIt/"
    if oscar:
        path = "/users/dheffren/data/dheffren/ChangeIt/"
    categoryFrames = loadCategoryAnnotated("apple", path, desiredSize)
    numVideos = categoryFrames.shape[0]
    print("number of videos to process: ", numVideos)
    #still need to save these points because can't display in oscar.

    points = generateRandomPoints(numVideos, numPoints, finalSize)
    resultPoints = callDift(categoryFrames, points)
    for i in range(numVideos):

        beginningImage = convertPIL(categoryFrames[0, 0], finalSize[0])
        endImage = convertPIL(categoryFrames[0, 2], finalSize[0])
        saveImages(str(i), beginningImage, endImage, True)

    displayImages(beginningImage, endImage, points[0], resultPoints[0])
def diftChangeOneVideo(oscar):
    numPoints = 10
    #x,y
    desiredSize = (480, 270)
    category = "apple"
    path =   "/mnt/c/Users/dheff/CodingProjects/PythonProjects/PALM Research/data/ChangeIt/"
    if oscar:
       path = "/users/dheffren/data/dheffren/ChangeIt/"
    preset = "https://www.youtube.com/watch?v="
    videoChoice = "8AK0JQkaQpE.fps1.csv"
    link = path + "annotations/" + category
    print("video: ", videoChoice)
    indices, valid = loadAndProcessAnnotations(link+ "/" + videoChoice)
    if valid: 
        videoLink = preset + videoChoice[0:-9]
        frames = processVideoSimple(videoLink, indices)
    else:
        raise Exception("invalid choice")
    points = generateRandomPoints(1, numPoints, desiredSize)



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
    
diftChange(True)