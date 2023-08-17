def processVideoSimple(link, indices, desiredSize):
    """
    Simpler version without threading, extracts the indices from the video. 
    WANT NOT JUST THE FIRST FRAME FROM EACH SECOND< PICK THE MIDDLE FRAME. 

    Annotation starts at 0 so to get the beginning of the desired second specified by 
    indices, do fps*indices


    """
    print("begin process info")
    try:
        ydl_opts = {}
        ydl = yt_dlp.YoutubeDL(ydl_opts)
        info_dict = ydl.extract_info(link, download=False)
        formats = info_dict.get('formats', None)
    except:
        print("YOUTUBE DOWNLOAD FAILED")
        return None
    print("done that part. ")
    formatList = ['720p', '480p', '360p', '144p']
    #maybe try a specific format. 
    for f in formats:
        #pick a format, initially was 144p
        if f.get('format_note', None) in formatList:
            print("in format")
            url = f.get('url', None)
            cap = cv2.VideoCapture(url)
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            #indices in which second the frame occurs in. 
            #hould get the FIRST frame in each interval, if want something else, change it. 
            frameForEach = fps*indices
            listFrames = []
            for i in range(3):
                print("i is : ", i)
                #leftmost middle frame of the given second. 
                cap.set(cv2.CAP_PROP_POS_FRAMES, frameForEach[i] + fps//2)
                """
                unattained = True
                count = 0
                
                #only stay within the second. 
                originalFrame = None
                while unattained and count<fps:
                    ret, frame = cap.read()
                    print(frame)
                    if ret:
                        print("returned")
                        unattained = False
                        #720p is y vert direciton, so 720 y 1080 x. 
                        #(480 x 270 y)
                        #changes it to y then x. 
                        image  = cv2.resize(frame, desiredSize)
                        imageColorChanged = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                        
                        listFrames.append(imageColorChanged)
                    count = count+1
                if unattained:
                    raise Exception("Couldn't find a viable frame")
                """
                #want this block to assuem teh first frame alwasy works. 
                ret, frame = cap.read()
                if not ret:
                    raise Exception("Frame didn't work")
                image  = cv2.resize(frame, desiredSize)
                imageColorChanged = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)   
                listFrames.append(imageColorChanged)
            frames = np.stack(listFrames)
            print("frames shape: ", frames.shape)
            return frames
        #need way to find other formats once we're done with 720p
    print("Failed video format")
    return None
def loadAndProcessAnnotations(csvLink):
    """

    picks the first occurence of each of initial state, final state, and action. 
    If one of these doesn't occur in the video, gives an index of -1. 
    also return boolean if VALID or not. For now ,valid means it has all 3 states, maybe not later. 
    """
    #0 = nothing 1= initial 2 = action 3 = final. 
    annotationCSV = pd.read_csv(csvLink)
    #should be list of values for states. 
    #convert to ints i think. 
    #dataframe -> numpy -> list
    listAnnotations = annotationCSV.iloc(axis=1)[1].values.tolist()
    indices = -1*np.ones(shape = (3,), dtype=int)
    for i in range(3):
        try:
            #if the given index doesn't exist in the labels, give it a dne. 
            index = listAnnotations.index(i+1)
            indices[i] = index
        except:
            print("label: ", i+1, " dne")
    valid = True
    if -1 in indices:
        valid = False
    return indices, valid
    

def process_video_parallel(url, desiredSize, process_number):
    """
    Called by each thread to load the video frames as desired. Use this when you want a frame for 
    each second of the video, not when you just want the 3 desired frames. Too slow and inefficient for that. 

    """
    print("SHOULDN'T BE CALLED")
    cap = cv2.VideoCapture(url)
    num_processes = os.cpu_count()
    
    #divides total frames in video into num cpus amounts.
    frames_per_process = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))//num_processes
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    print("fps: " , fps)
    #cap_PROP_POS_FRAMES = 0 based index of frame to  be decoded/captured next. 
    #processes labelled starting at 0, so it allocates frames_per_Process frames for each. 
    
    print("frame count: ", cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print("frames per process: ", frames_per_process)
    #want to round up to nearest whole number. 

    #method wrong if already is a whole number. 
    numberOfFramesFromDesired = 0
    modulo = (frames_per_process*process_number)%fps
    if(modulo != 0):
        numberOfFramesFromDesired = fps - (frames_per_process*(process_number))%fps
    startingIndex = frames_per_process*(process_number) + numberOfFramesFromDesired
    print("starting index: ", startingIndex)
    
    print("begin interval: ", frames_per_process*(process_number))
    print("end interval: ", frames_per_process*(process_number+1))
    endIndex = frames_per_process*(process_number+1)
    if(endIndex>cap.get(cv2.CAP_PROP_FRAME_COUNT)):
        endIndex = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    count = 0
    listFrames = []
    listStarting = []
    cap.set(cv2.CAP_PROP_POS_FRAMES, startingIndex)
    while count+startingIndex<endIndex:
        ret,frame = cap.read()
        if not ret:
            break
        #automatically makes the image 270x480. Not sure which dimension is which. 
        image = cv2.resize(frame, desiredSize)
        print(image.shape)
        value = np.array(image, np.uint8)
        print("value shape: ", value.shape)
        listFrames.append(value)
        listStarting.append(startingIndex+count)
        count+=fps
        cap.set(cv2.CAP_PROP_POS_FRAMES,startingIndex + count)
    cap.release()
    frameArray = np.stack(listFrames, dtype=np.uint8)
    print("frame array shape: ", frameArray.shape)
    print("starting list: ", listStarting)
    assert(len(frameArray.shape) ==4)
    return frameArray
def youtubeLoadDirect(link, indices):

    """
    Given a youtube video link, and list of indices to extract frames for initial, action, and end states, 
    downloads those frames without saving the video into storage, makes it so you can do everything at once. 

    Loads a frame for each second.  
    Uses multiprocessing. 
    Partially derived from:
    https://stackoverflow.com/questions/66272740/extract-specific-frames-of-youtube-video-without-downloading-video
    Had to change some of the stuff in the link. 
    ALSO, CHANGE THE FORMAT. FIGURE OUT HOW TO MAKE IT BETTER THEN DOWNSIZE. 
    """
    ydl_opts = {}
    ydl = yt_dlp.YoutubeDL(ydl_opts)
    info_dict = ydl.extract_info(link, download=False)
    desiredSize = (480, 270)
    formats = info_dict.get('formats', None)
    #save the 3 desired frames from this video. 
    for f in formats:
        #pick a format, initially was 144p
        if f.get('format_note', None)=='720p':
            url = f.get('url', None)
            cpu_count = os.cpu_count()
            #allows for accessing the whole video with all frames potentially. 
            with Pool(cpu_count) as pool:
                #divides total frames into groups based on number of cpus, explain this later. 
                videoImagesArray = np.concatenate(pool.map(partial(process_video_parallel, url, desiredSize), range(cpu_count)), axis=0)
            return videoImagesArray
def loadAndProcessAnnotationsMiddle(csvLink):
    """
    Picks middle occurence of each state (continuous display). 

    Should we assume labels are in ONE continuous, ie 2 never repeats once its done? 
    If not, which one do we pick? First, or the one that occurs in the right order? 
    DOESN't. SECOND APPLE goes 3 2 3. Dont want to average because that'd be a frame in the 2. 
    Should we go 1 then 3? 

    Chooses the left middle of the first contiguous section of each category. 
    Maybe should preserve locality? Choose the close ones? 

    care about actions? 
    """
    #0 = nothing 1= initial 2 = action 3 = final. 
    annotationCSV = pd.read_csv(csvLink)
    listAnnotations = annotationCSV.iloc(axis=1)[1].values.tolist()
    print("list annotations: ", listAnnotations)
    indices = -1*np.ones(shape = (3,), dtype=int)
    rightMost = False
    for i in range(3):
        try:
            #if the given index doesn't exist in the labels, give it a dne. 
            index = listAnnotations.index(i+1)
            print("index for {}: {}".format(i+1, index))
            #if this does exist, want this CONTIGUOUS stretch of frames, and to find the middle.
            newArrayDiff = np.diff(listAnnotations[index:])
            #starts with 0s until end
            #where is the change. List indices in order of where it isn't 0. 
            #gets first where there is a difference. 
            endIndex = np.nonzero(newArrayDiff !=0)[0][0]
            print("endIndex: ", endIndex)
            #if first index is nonzero, means there was just ONE. 
        
            #to get the leftmost, take (endIndex)//2, rightmost endIndex + 1//2
            indexChoice = (endIndex+ int(rightMost))//2
            print("index choice: ", indexChoice)
            #choose rightmost value in the middle 2. 
            #indexChoice = (endIndex + 1)/2
            chosenIndex = index + indexChoice
            print("chosen index: ", chosenIndex)
            indices[i] = chosenIndex
        except:
            print("label: ", i+1, " dne")
    valid = True
    if indices[1] ==-1:
        print("got in this area")
        indices[1] == indices[0]

    if indices[0] == -1 or indices[2]==-1:
        valid = False
    return indices, valid


def processVideoSimpleNoLoop(link, indices, desiredSize):
    try:
        ydl_opts = {}
        ydl = yt_dlp.YoutubeDL(ydl_opts)
        info_dict = ydl.extract_info(link, download=False)
        formats = info_dict.get('formats', None)
    except:
        print("YOUTUBE DOWNLOAD FAILED")
        return None
    formatList = ['720p', '480p', '144p']
    for format in formatList:
        try:
            frames = processVideoHelper(format, formats, indices, desiredSize)
        except:
            continue
        if frames is not None:
            print("returning resolution: ", format)
            return frames
    print("Operation failed, no valid formats")
    return None

def processVideoHelper(formatName, formats, indices, desiredSize):
    for f in formats:
        if f.get('format_note', None)== formatName:
            print("in format: ", formatName)
            #fps varies with resolution. 
            url = f.get('url', None)
            cap = cv2.VideoCapture(url)
            print("post capture")
            fps = int(cap.get(cv2.CAP_PROP_FPS))    
            #indices in which second the frame occurs in. 
            #should get the FIRST frame in each interval. 
            frameForEach = fps*indices
            listFrames = []
            for i in range(3):
                #leftmost frame of middle second. 
                print("pre set cap")
                cap.set(cv2.CAP_PROP_POS_FRAMES, frameForEach[i] + fps//2)
                print("pre read")
                ret, frame = cap.read()
                print("post read")
                if not ret:
                    raise Exception("Frame didn't work")
                image  = cv2.resize(frame, desiredSize)
                imageColorChanged = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)   
                listFrames.append(imageColorChanged)
            frames = np.stack(listFrames, dtype= np.uint8)
            print("frames shape: ", frames.shape)
            return frames
    print("no format of type: ", formatName)
    return None
def loadCategoryAnnotated(category, path, desiredSize):
    """
    Loads all the desired frames from valid annotated videos of a given video with the right
    size and as 8 bit integers. 
    """
    link = path + "annotations/" + category
    listFilesAnnotated = os.listdir(link)
    preset = "https://www.youtube.com/watch?v="
    #each ends with .fps1.csv 9 characters
    listFrames = []
    count = 0
    for video in listFilesAnnotated:
        print("video: ", video)
        #should i exclude videos without all 3? 
        indices, valid = loadAndProcessAnnotationsMiddle(link+ "/" + video)
        if valid: 
            videoLink = preset + video[0:-9]
            #extracts those indices from the video. 
            frames = processVideoSimpleNoLoop(videoLink, indices, desiredSize)
            
            if frames is not None:
                #displayFrames(frames)
                listFrames.append(frames)
                count+=1
    print("numframes: ", len(listFrames))
    return np.stack(listFrames, dtype = np.uint8)

