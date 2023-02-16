import cv2


class Object:
    def __init__(self, box, label, score):
        """Initialize object class.
        Args:
            box (list): bounding box.
            label (list): label.
            score (list): score.
        """
        self._bbox = None
        self.set_box(box)
        self._label = label
        self._score = score
        self._color = (1, 15, 255)  # default red color

    def get_box(self):
        return self._bbox

    def set_color(self, **kwargs):
        """Set color of bounding box
        """
        if kwargs.get('valid'):
            self._color = (100, 255, 71)  # green color
        else:
            self._color = (1, 15, 255)  # red color

    def _get_roi(self):
        """Get ROI of the object.
        Returns:
            tuple: top-left & bottom-right coordinates of bounding box.
        """
        x1, y1, x2, y2 = int(self._bbox[0]), int(self._bbox[1]), int(self._bbox[2]), int(self._bbox[3])
        w, h = x2 - x1, y2 - y1
        if w <= 0 or h < 0:
            return 0, 0, 0, 0
        if x1 < 0:
            x1 = 0
        if y1 < 0:
            y1 = 0

        return x1, y1, x2, y2

    def set_box(self, new_box):
        x1, y1, x2, y2 = int(new_box[0]), int(new_box[1]), int(new_box[2]), int(new_box[3])
        w, h = x2 - x1, y2 - y1
        if w <= 0 or h <= 0:
            self._bbox = [0, 0, 0, 0]
            return
        if x1 < 0:
            x1 = 0
        if y1 < 0:
            y1 = 0
        self._bbox = [x1, y1, x2, y2]

    def update_label(self, label, confidence):
        if confidence > self._score:
            self._label = label
            self._score = confidence

    def _draw_corners(self, frame, coord, thick=-1):
        """Draw corners on the frame.
        Args:
            frame (numpy.ndarray): Frame to draw on.
            coord (list): bounding box coordinates
            thick (int, optional): Fill the corner. Defaults to cv2.FILLED.
        """
        # DRAW CORNERS
        # top-left
        cv2.rectangle(frame, (coord[0] - 10, coord[1] - 10), (coord[0] + 10, coord[1] + 10),
                      self._color, thickness=thick)
        # top-right
        cv2.rectangle(frame, (coord[2] - 10, coord[1] - 10), (coord[2] + 10, coord[1] + 10),
                      self._color, thickness=thick)
        # bottom-left
        cv2.rectangle(frame, (coord[0] - 10, coord[3] - 10), (coord[0] + 10, coord[3] + 10),
                      self._color, thickness=thick)
        # bottom-right
        cv2.rectangle(frame, (coord[2] - 10, coord[3] - 10), (coord[2] + 10, coord[3] + 10),
                      self._color, thickness=thick)

    def process(self, **kwargs):
        pass
