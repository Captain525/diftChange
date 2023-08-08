
import numpy as np
from PIL import Image
import os
def savePoints(points, name, oscar=False):
    link = "/mnt/c/Users/dheff/CodingProjects/PythonProjects/PALM Research/GlobusToOscar/"
    if oscar:
        link = "/users/dheffren/data/dheffren/"
    np.save(link + "dift/Points/" + name, points)
def loadPoints(name, oscar=False):
    link = "/mnt/c/Users/dheff/CodingProjects/PythonProjects/PALM Research/GlobusToOscar/"  
    if oscar:
       link = "/users/dheffren/data/dheffren/" 
    clicksArray = np.load(link + "dift/Points/" + name + ".npy")
    return clicksArray
def saveResults(results, name, oscar=True):
    link = "/mnt/c/Users/dheff/CodingProjects/PythonProjects/PALM Research/GlobusData/"
    if oscar:
        link = "/users/dheffren/scratch/"
    np.save(link + "dift/Results/" + name, results)
def loadResults(name, oscar=False):
    link = "/mnt/c/Users/dheff/CodingProjects/PythonProjects/PALM Research/GlobusData/"
    if oscar:
        link = "/users/dheffren/scratch/"
    clicksArray = np.load( link + "dift/Results/"+ name + ".npy")
    return clicksArray
def saveImages(name, beginImage, endImage, oscar=False):
    link = "/mnt/c/Users/dheff/CodingProjects/PythonProjects/PALM Research/GlobusToOscar/"
    if oscar:
        link = "/users/dheffren/data/dheffren/"
    beginImage.save(link + "/dift/Images/" + "begin" + name + ".jpg")
    endImage.save(link + "/dift/Images/"+ "end" + name + ".jpg")  
def loadImages(name, oscar=False):
    link = "/mnt/c/Users/dheff/CodingProjects/PythonProjects/PALM Research/GlobusToOscar/"
    if oscar:
        link = "/users/dheffren/data/dheffren/" 
    beginImage = Image.open(link + "/dift/Images/" + "begin" + name + ".jpg")
    endImage = Image.open(link + "/dift/Images/"+ "end" + name + ".jpg")
    return beginImage, endImage