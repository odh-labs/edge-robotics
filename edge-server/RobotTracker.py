import math
import time
from enum import Enum
 
class State(Enum):
    DETECTED = 1
    OUT_OF_VIEW = 2
    STOPPED = 3
    MOVING = 4

class RobotTracker:
    # threshold for movement in number of pixels
    distanceThreshold = 5

    # time threshold in seconds beyond which the robot is considered STOPPED
    stopThreshold = 2.

    # The init method or constructor
    def __init__(self, name, state):
 
        # Instance Variable
        self.name = name
        self.state = state
        self.centerX = -1
        self.centerY = -1
        self.startTime = 0.
        self.tracking = False
 
    # Adds an instance variable
    # def setName(self, name):
    #     self.name = name

    # def setState(self, state):
    #     self.state = state        
 
    # Retrieves instance variable
    def getName(self):
        return self.name
    
    def getState(self):
        return self.state
    
    # get the time that the robot has stayed stationary
    def getStoppageTime(self):
        if self.state == State.STOPPED:
            return time.time() - self.startTime

        return 0.
    
    # explicitly change the state of the robot
    # return True if there is a stat change
    # return False otherwise
    def updateStateDirect(self, state):
        if state == self.state:
            return False
        
        self.state = state
        return True
    
    # update the state of the robot based on its movement (distance moved between frames)
    # return True if there is a stat change
    # return False otherwise
    def updateStateTrackingCenter(self, centerX, centerY):
        if self.state == State.OUT_OF_VIEW:
            self.state = State.DETECTED
            self.centerX = centerX
            self.centerY = centerY
            return True
        
        if (((self.state == State.DETECTED) or (self.state == State.MOVING)) and not self.tracking):
            # center not indentified yet
            self.centerX = centerX
            self.centerY = centerY
            self.startTime = time.time()
            self.tracking = True
            return False
        
        movedDistance = round(math.sqrt((centerX - self.centerX) ** 2 +
                                  (centerY - self.centerY) ** 2))
        
        if movedDistance <= RobotTracker.distanceThreshold:
            if (time.time() - self.startTime) >= RobotTracker.stopThreshold:
                return self.updateStateDirect(State.STOPPED)
        else:
            self.tracking = False
            return self.updateStateDirect(State.MOVING)
            
        return False
    
    # datetime.now().strftime("%H:%M:%S")