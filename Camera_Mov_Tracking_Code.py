#################################################################
#Vars

#capturing timing
keyFrameRatio = 1/24 #(24Fps Capture a keyframe each 1/24 second)
viewPointRatio = 1 #(time for the viewpoint creation in second. 1 viewpoint each X )

#max capturing. used for avoiding endless capturing
maxVPCaptured = 10
maxKFCaptured = 240

#capturing activation
captureKeyFrames = 1
captureViewPoints = 1


#################################################################
#Func

# Camera Tracking Functions
def createNewTrack():
    global newTrackForCamerTracking
    global curCamera
    global curTime
    
    #Create a new camera Track. A suffix is added to not overwrite
    curCameraTracks = curCamera.getCameraTrackCount()
    trackSuffix = "_" + str(curCameraTracks)
    newTrackName = curCamera.getName() + "_Captured_Track" + trackSuffix
    #print(newTrackName)
    newTrackForCamerTracking = vrCameraService.createCameraTrack(newTrackName, curCamera)
    print("New Track " + newTrackName + " Created.")

#create a viewpoint each second
def createVP():
    global viewpointCounter
    global newTrackForCamerTracking
    global curCamera
    global VPTimeCounter
    global VPtimer
    
    VPTimeCounter = VPTimeCounter + 1
    
    #create a new Viewpoint based on the curent view
    if not trackingStoppedByUser:
        viewpointCounter = viewpointCounter + 1
        viewpointCounter_str = str(viewpointCounter)
        zerFilledCounter = viewpointCounter_str.zfill(3)
        newVPName = curCamera.getName() + "_Captured_VP" + zerFilledCounter
        vrCameraService.createViewpoint(newVPName, newTrackForCamerTracking)
    
    #stop the timer after a fixed number of Kframe capured
    if VPTimeCounter > maxVPCaptured-1:
        VPtimer.setActive(False)
        print("Capturing Viewpoints for Camera " + curCamera.getName() + " Ended.")

def createKeyFrame():
    global curCamera
    global KFTimeCounter
    global maxKFReached
    global KFtimer
    
    KFTimeCounter = KFTimeCounter + 1
    curTimeRatio = KFTimeCounter * keyFrameRatio
    
    #create a new keyframe based on the curent view
    oldNodePtr = toNode(curCamera.getObjectId())
    if not maxKFReached and not trackingStoppedByUser:
        curCameraTrans = oldNodePtr.getTranslation()
        curCameraRot = oldNodePtr.getRotation()
        addTranslationControlPoint(curCamera, curTimeRatio , Vec3f(curCameraTrans[0], curCameraTrans[1], curCameraTrans[2]), False)
        addRotationControlPoint(curCamera, curTimeRatio, Vec3f(curCameraRot[0], curCameraRot[1], curCameraRot[2]))
    
    #stop the timer after a fixed number of Kframe capured
    if KFTimeCounter > maxKFCaptured:
        KFtimer.setActive(False)
        if not maxKFReached:
            # Curve Block Creation
            createAnimationBlockForNode(oldNodePtr, True)
            maxKFReached = 1
            print("Capturing KeyFrame for Camera " + curCamera.getName() + " Ended.")
            

def startCameraTracking():
    global newTrackForCamerTracking
    global viewpointCounter
    global curCamera
    global VPTimeCounter
    global KFTimeCounter
    global maxKFReached
    global trackingStoppedByUser
    global KFtimer
    global VPtimer
    
    curCamera = None
    newTrackForCamerTracking = None
    maxKFReached = None
    trackingStoppedByUser = None
    viewpointCounter = 0
    VPTimeCounter = 0
    KFTimeCounter = -1
    
    #current camera
    curCamera = vrCameraService.getActiveCamera(False)
    #print(curCamera.getName())
    print("Capturing Camera " + curCamera.getName() + " Started...")
    
    #create timers
    KFtimer = vrTimer(keyFrameRatio)
    KFtimer.connect(createKeyFrame)
    VPtimer = vrTimer(viewPointRatio)
    VPtimer.connect(createVP)
     
    # Start a timer and create a viewpoint each second
    if captureViewPoints:
        #creation of a new track on the current camera
        createNewTrack()
        VPtimer.setActive(True)
    
    # Start a timer and create a keyframe each time
    if captureKeyFrames:
        KFtimer.setActive(True)
    
def stopCameraTracking():
    global curCamera
    global trackingStoppedByUser
    global KFtimer
    global VPtimer
    
    trackingStoppedByUser = 1
    
    VPtimer.setActive(False)
    KFtimer.setActive(False)
    
    # Curve Block Creation
    if captureKeyFrames:
        oldNodePtr = toNode(curCamera.getObjectId())
        createAnimationBlockForNode(oldNodePtr, True)
    
    print("Capturing Camera " + curCamera.getName() + " Ended.")
    
#################################################################
#Keys

# Start Capturing
keyQ_CT = vrKey(Key_Q)
keyQ_CT.connect("startCameraTracking()")

# Stop Capturing
keyW_CT = vrKey(Key_W)
keyW_CT.connect("stopCameraTracking()")
