from abc import ABC, abstractmethod
import requests
import io

class AbstractObjectDetection(ABC):

    # constructor
    @abstractmethod  # Decorator to define an abstract method
    def __init__(self, url, fieldId):
        self.url = url
        self.json = None
        self.fieldId = fieldId

    # invoke the model using a REST API
    def invokeModel(self, image):
        # call inference REST API
        # params = {}
        # params[self.fieldId] = open(photo, 'rb')
        buf = io.BytesIO(image)
        # image.save(buf, format='JPEG')
        # params[self.fieldId] = 'photo'
        stream = buf.getvalue()
        response = requests.post(
            self.url,
            # files = {'data': ('photo.jpg', stream, 'image/jpeg')},
            files=((self.fieldId , stream),)
            # headers = {'Content-Type' : 'image/jpeg'},
            # data=buf.getvalue()
        )
        self.json = response.json()

    # Get the minimal info needed for the trackRobotsApp
    @abstractmethod  # Decorator to define an abstract method
    def getNameCenterAndConfidence(self):
        pass
