
import numpy as np
from PIL import Image
import os
def savePoints(points, name, oscar=False):
    link = "/mnt/c/Users/dheff/CodingProjects/PythonProjects/PALM Research/GlobusData/"
    if oscar:
        link = "/users/dheffren/data/dheffren/"
    np.save(link + "diftChange/Points/" + name, points)
def loadPoints(name, oscar=False):
    link = "/mnt/c/Users/dheff/CodingProjects/PythonProjects/PALM Research/GlobusData/"  
    if oscar:
       link = "/users/dheffren/data/dheffren/" 
    clicksArray = np.load(link + "diftChange/Points/" + name + ".npy")
    return clicksArray
def saveResults(results, name, oscar=True):
    link = "/mnt/c/Users/dheff/CodingProjects/PythonProjects/PALM Research/GlobusData/"
    if oscar:
        link = "/users/dheffren/scratch/"
    np.save(link + "diftChange/Results/" + name, results)
def loadResults(name, oscar=False):
    link = "/mnt/c/Users/dheff/CodingProjects/PythonProjects/PALM Research/GlobusData/"
    if oscar:
        link = "/users/dheffren/scratch/"
    clicksArray = np.load( link + "diftChange/Results/"+ name + ".npy")
    return clicksArray
def saveImages(name, beginImage, endImage, oscar=False):
    link = "/mnt/c/Users/dheff/CodingProjects/PythonProjects/PALM Research/GlobusData/"
    if oscar:
        link = "/users/dheffren/data/dheffren/"
    beginImage.save(link + "/diftChange/Images/" + "begin" + name + ".jpg")
    endImage.save(link + "/diftChange/Images/"+ "end" + name + ".jpg")  
def loadImages(name, oscar=False):
    link = "/mnt/c/Users/dheff/CodingProjects/PythonProjects/PALM Research/GlobusData/"
    if oscar:
        link = "/users/dheffren/data/dheffren/" 
    beginImage = Image.open(link + "/diftChange/Images/" + "begin" + name + ".jpg")
    endImage = Image.open(link + "/diftChange/Images/"+ "end" + name + ".jpg")
    return beginImage, endImage
def getPathChange(oscar=True):
    path = "/mnt/c/Users/dheff/CodingProjects/PythonProjects/PALM Research/data/ChangeIt/"
    if oscar:
        path = "/users/dheffren/data/dheffren/ChangeIt/"
    return path
def videoPath(name, oscar=True):
    path = getPathChange(oscar)
    downloadPath = path + "annotatedVideos/" + name + ".mp4"
    return downloadPath
def video(path, name):
    return path + "annotatedVideos/" + name+ ".mp4"
def getAnnotationPath(link, category, oscar):
    path = getPathChange(oscar)
    return path + "annotations/" + category + "/" + link + ".fps1.csv"
def saveListDownloaded(listNames,listLinks, oscar):
    path = getPathChange(oscar)
    fileName = "listDownloaded"
    with open(path + fileName,"w") as f:
        for i in range(len(listNames)):
            f.write("{},{}\n".format(listNames[i], listLinks[i]))
def loadListDownloaded(oscar):
    path = getPathChange(oscar)
    fileName = "listDownloaded"
    with open(path + fileName, "r") as f:
        nameLinks = [(video.replace("\n","").split(",")[0], video.replace("\n","").split(",")[1])for video in f.readlines()]
    names, links = zip(*nameLinks)
    nameList = list(names)
    linkList = list(links)
    print(nameLinks)
    print(names)
    print(links)
    return nameList, linkList
