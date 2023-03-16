import json
from AbstractObjectDetection import AbstractObjectDetection

class ApriltagObjectDetection(AbstractObjectDetection):

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
            center = r['center']

            # top left-hand corner
            corner = r['corners'][0]

            row.append("robot-{}".format(r['tag_id']))
            row.append(corner)
            row.append(center)
            row.append(float(r['decision_margin']))

            list.append(row)

        return list
        
if __name__ == '__main__':
    # Execute when the module is not initialized from an import statement.
    # this is a test of this class
    detect = ApriltagObjectDetection("http://localhost:6000/v1/object-detection/apriltag", "image")         
    detect.invokeModel("apriltagSample.jpg")
    for r in detect.getNameCenterAndConfidence():
        (name, corner, center, confidence) = r
        print(name)
        print(center)
        print(corner)
        print(confidence)