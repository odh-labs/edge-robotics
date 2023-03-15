from abc import ABC, abstractmethod
import requests

class AbstractObjectDetection(ABC):

    # constructor
    @abstractmethod  # Decorator to define an abstract metho
    def __init__(self, url, fieldId):
        self.url = url
        self.json = None
        self.fieldId = fieldId

    # invoke the model using a REST API
    def invokeModel(self, photo):
        # call inference REST API
        params = {}
        params[self.fieldId] = open(photo, 'rb')
        response = requests.post(
        self.url,
            files=params,
        )
        self.json = response.json()

    # Get the minimal info needed for the trackRobotsApp
    @abstractmethod  # Decorator to define an abstract method
    def getNameCenterAndConfidence(self):
        pass
