"""
API exposing the apriltag detection functionality
"""
import argparse
import io
import apriltag
import cv2
import numpy

from flask import Flask, request, jsonify

app = Flask(__name__)

APRILTAG_URL = "/v1/object-detection/apriltag"


@app.route(APRILTAG_URL, methods=["POST"])
def detect():
    if not request.method == "POST":
        return

    if request.files.get("image"):
        image_bytes = request.files["image"].read()
        image = cv2.imdecode(numpy.fromstring(image_bytes, numpy.uint8), cv2.IMREAD_UNCHANGED)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        results = detector.detect(gray)

        # loop over the apriltag detection results
        # reformat the info in results for conversion to JSON
        value = []
        for r in results:
            info = {}

            info['tag_id'] = r.tag_id
            info['tag_family'] = str(r.tag_family)
            info['hamming'] = r.hamming
            info['goodness'] = r.goodness
            info['decision_margin'] = r.decision_margin

            # extract the center of the apriltag
            # ptCenter = r.center
            ptCenter = [round(float(i)) for i in r.center]
            info['center'] = ptCenter

            # extract the corners of the bounding box for the apriltag
            (ptA, ptB, ptC, ptD) = r.corners
            ptA = [round(float(i)) for i in ptA]
            ptB = [round(float(i)) for i in ptB]
            ptC = [round(float(i)) for i in ptC]
            ptD = [round(float(i)) for i in ptD]
            cornersList = []
            cornersList.append(ptA)
            cornersList.append(ptB)
            cornersList.append(ptC)
            cornersList.append(ptD)
            info['corners'] = cornersList

            # extract the homography matrix
            # and convert each row to floats
            (row1, row2, row3) = r.homography
            row1 = list(map(float, row1))
            row2 = list(map(float, row2))
            row3 = list(map(float, row3))
            rowList = []
            rowList.append(row1)
            rowList.append(row2)
            rowList.append(row3)
            info['homography'] = rowList

            value.append(info)

        return jsonify(value)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Flask api exposing apriltag detection")
    parser.add_argument("--port", default=6000, type=int, help="port 6000")
    parser.add_argument('--family', default='tag36h11', help='apriltag family, e.g. --family tag36h11')
    args = parser.parse_args()

    options = apriltag.DetectorOptions(families=args.family)
    detector = apriltag.Detector(options)

    app.run(host="0.0.0.0", port=args.port)  # debug=True causes Restarting with stat