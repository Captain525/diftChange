from dataTransfer import loadPoints, loadFrames, loadResults, loadListDownloaded
from imageDisplay import convertPIL, displayImages, displayImageList
def loadAndDisplay(oscar=False):
    """
    Displays the results obtained and trasmitted to the right place. Make sure finalSize matches with diftChange final size. 
    
    BUG: Not all loaded names will be valid points to load, since some of them are skipped. How to fix this? 
    """
    #how many videos to load. 
    num_images = 3

    #PROBLEM - NOT ALL VIDEOS WITH NAMES WORK. 
    #names of the vidoes, needed for loading. 
    names, links = loadListDownloaded(oscar)
    finalSize = 768
    for i in range(num_images):
        name = names[i]
        try:
            points = loadPoints(name, oscar)
            frames = loadFrames(name, oscar)
            imageList = []
            #TODO: could make it so that beginning image is in the list, but would have to combine points and results. For now, keep as is. \
            #Would have to change this method and the saving points methods and the displayImageList Method. 
            beginningImage = convertPIL(frames[0], finalSize)
            for j in range(1, frames.shape[0]):
                image = convertPIL(frames[j], finalSize)
                imageList.append(image)
            results = loadResults(name, oscar)
            displayImageList(beginningImage, imageList, points, results)
        except OSError:
            print("Couldn't find the file, ie it doesn't exist. ")
       
        
loadAndDisplay(False)