import json
from AbstractObjectDetection import AbstractObjectDetection

class YoloObjectDetection(AbstractObjectDetection):

    # constructor
    def __init__(self, url, fieldId):
        super().__init__(url, fieldId)

    # Get the minimal info needed for the trackRobotsApp
    def getNameCenterAndConfidence(self):
        list = []
        for d in self.json:
            row = []
            r = json.loads(json.dumps(d))

            # locate center of the robot
            x = int(r['xmin']) + (int(r['xmax'] - r['xmin'])) / 2
            y = int(r['ymin']) + (int(r['ymax'] - r['ymin'] ))/ 2

            # top left-hand corner
            corner = (int(r['xmin']), int(r['ymin']))

            row.append(r['name'])
            row.append(corner)
            row.append([int(x), int(y)])
            row.append(float(r['confidence']))

            list.append(row)

        return list
        
if __name__ == '__main__':
    # Execute when the module is not initialized from an import statement.
    # this is a test of this class
    detect = YoloObjectDetection("http://127.0.0.1:5000/v1/object-detection/yolov5", "image")         
    detect.invokeModel("yoloSample.jpg")
    for r in detect.getNameCenterAndConfidence():
        (name, corner, center, confidence) = r
        print(name)
        print(center)
        print(corner)
        print(confidence)