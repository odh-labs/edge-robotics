import apriltag
import argparse
import cv2
import os

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True,
	help="path to image")
ap.add_argument("-s", "--show", dest='show', action='store_true')
args = vars(ap.parse_args())

# load image
image = cv2.imread(args["image"])
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# define options for apriltag detector
options = apriltag.DetectorOptions(families="tag36h11")
detector = apriltag.Detector(options)
results = detector.detect(gray)

print('*' * 25)
print("{} apriltags detected:".format(len(results)))

# post-processing the image
for r in results:
	# Get the 4 corners of the bounding box and convert to integers
	(ptA, ptB, ptC, ptD) = r.corners
	ptA = [round(float(i)) for i in ptA]
	ptB = [round(float(i)) for i in ptB]
	ptC = [round(float(i)) for i in ptC]
	ptD = [round(float(i)) for i in ptD]

	
	# draw bounding box around the apriltag
	cv2.line(image, ptA, ptB, (0, 255, 0), 2)
	cv2.line(image, ptB, ptC, (0, 255, 0), 2)
	cv2.line(image, ptC, ptD, (0, 255, 0), 2)
	cv2.line(image, ptD, ptA, (0, 255, 0), 2)
	
	# draw the center of the apriltag
	(x, y) = (int(r.center[0]), int(r.center[1]))
	cv2.circle(image, (x, y), 4, (0, 0, 255), -1)
	
	# draw tag Id
	tagId =r.tag_id;
	tagIdStr = "Id=%s" %(tagId)
	cv2.putText(image, tagIdStr, (ptA[0], ptA[1] - 15),
		cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
	print("Tag Id: {}".format(tagId))

print('*' * 25)

# show the output image is -s option has been specified
# otherwise save output image to file
if args['show']:
	cv2.imshow("Image", image)
	cv2.waitKey(10000)
	cv2.destroyAllWindows()
else:
	# save apriltags with bounding box in current directory
	# with filename prfixed with '_'
	cv2.imwrite("_" + os.path.basename(args["image"]), image)


