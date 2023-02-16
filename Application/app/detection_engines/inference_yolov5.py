import numpy as np
from utils.utils import scale_coords,non_max_suppression,get_xyxy
import cv2
from openvino.runtime import Core, Type, Layout
from openvino.preprocess import PrePostProcessor, ColorFormat
from utils import Profiler,bcolors
# import torch
class YOLOV5_s:

    def __init__(self, config) :
        self._input_w = config["input_w"]
        self._input_h = config["input_h"]
        self._conf_thres = config["conf_thres"]
        self._iou_thres = config["iou_thres"]
        
        self._class_names = np.array(config["names"])
        self._model_type = 'openvino'#config["model_type"]
        self._throughput = config["throughput"]

        self._model_base_path = config["model_base_path"]
        self._model_input_size = config["model_input_size"]
        self._precision = config["precision"]

        self._model_dir = f"{self._model_base_path}/{self._precision}/{self._model_input_size}"
        self._input_shape = None
        # self._device = torch.device('cpu')
        self._model = self.attempt_load_openvino()


    @property
    def classes(self):
        return self._class_names
    
    def attempt_load_openvino(self):
        model_bin = self._model_dir + "/model.bin"
        # Loading the Inference Engine API
        ie = Core()
        # Loading IR files
        net = ie.read_model(model=self._model_dir+"/model.xml", weights=model_bin)
        ppp = PrePostProcessor(net)
        
        # if self._precision == "int8":
        #     ele_type = Type.i8
        # elif self._precision == "fp16":
        #     ele_type = Type.f16
        # else:
        #     ele_type = Type.f32
        
        ele_type = Type.f16
        ppp.input().tensor() \
            .set_element_type(ele_type) \
            .set_shape([1, 3, self._input_w, self._input_h]) \
            .set_layout(Layout('NCHW')) \
            .set_color_format(ColorFormat.BGR)
        model = ppp.build()

        # input_shape = net.inputs["img_placeholder"].shape
        # input_blob = next(iter(net.input_info))
        # Loading the network to the inference engine
        config = {"PERFORMANCE_HINT": "THROUGHPUT"}
        try:
            if self._throughput:
                compiled_model = ie.compile_model(model, self._device,config)
            else:
                compiled_model = ie.compile_model(model, self._device)
            infer_request = compiled_model.create_infer_request()
        except:
            print(f"{bcolors.WARNING}[Model] Warning: NO GPU FOUND.{bcolors.ENDC}")
            if self._throughput:
                compiled_model = ie.compile_model(model, 'CPU',config)
            else:
                compiled_model = ie.compile_model(model, 'CPU')
            infer_request = compiled_model.create_infer_request()
        print(f"{bcolors.OKGREEN}[Model] Info: IR successfully loaded into Inference Engine.{bcolors.ENDC}")

        # return exec_net, input_blob
        return infer_request
    def predict_openvino(self,frame):
        
        frame = self._preprocess_image(frame)
        
        #     pred = self._model.infer(inputs={self._input_blob: frame})
        # pred = np.array(pred["output"])
        # pred = torch.tensor(pred)
        # print(pred)
        with Profiler('inference'):
            self._model.infer(inputs= {0:frame})
        # if self._precision == "int8":
        #     with Profiler('inference_int8'):
        #         pred = self._model.get_output_tensor()
        # else:
        
        pred = self._model.get_output_tensor()
                # print(f"FP - {pred.data}")
        #print(pred,frame)
        return pred.data,frame
        # return pred,frame
    def _do_inference(self,frame):

        
        pred, img = self.predict_openvino(frame)

        # Apply NMS
        with Profiler('non_max'):
            pred = non_max_suppression(pred, self._conf_thres, self._iou_thres)
        with Profiler('post_process_image'):
            result_boxes, result_scores, result_classid = self._postprocess_img(pred, img, frame, self._class_names)
        # if self._precision == "int8":
        #     print(f"Pred - {result_classid}")
        return result_boxes, result_classid, result_scores

    def _preprocess_image(self, image_raw):
        """
        Read an image from image path, convert it to RGB, resize and pad
        it to target size, normalize to [0,1],transform to NCHW format.
        :params:
            image_raw: a opencv image object
        :returns:
            image    : the preprocessed image
        """
        
        h, w, c = image_raw.shape
        image = cv2.cvtColor(image_raw, cv2.COLOR_BGR2RGB)

        # Calculate widht and height and paddings
        r_w = self._input_w / w
        r_h = self._input_h / h
        if r_h > r_w:
            tw = self._input_w
            th = int(r_w * h)
            tx1 = tx2 = 0
            ty1 = int((self._input_h - th) / 2)
            ty2 = self._input_h - th - ty1
        else:
            tw = int(r_h * w)
            th = self._input_h
            tx1 = int((self._input_w - tw) / 2)
            tx2 = self._input_w - tw - tx1
            ty1 = ty2 = 0

        # Resize the image with long side while maintaining ratio
        image = cv2.resize(image, (tw, th))

        # Pad the short side with (128,128,128)
        image = cv2.copyMakeBorder(
            image, ty1, ty2, tx1, tx2, cv2.BORDER_CONSTANT, (128, 128, 128)
        )
        image = image.astype(np.float32)

        # Normalize to [0,1]
        image /= 255.0

        # HWC to CHW format:
        image = np.transpose(image, [2, 0, 1])

        # CHW to NCHW format
        image = np.expand_dims(image, axis=0)

        # Convert the image to row-major order, also known as "C order":
        image = np.ascontiguousarray(image)
        return image
    

    def _postprocess_img(self,pred,  img, frame, names):
        a = 0
        xywh_bboxs = []
        confs = []
        classes = []
        for i, det in enumerate(pred):

            # s = '%gx%g ' % img.shape[2:]  # print string
            if det is not None and len(det):

                det[:, :4] = scale_coords(
                        img.shape[2:], det[:, :4], frame.shape).round()
                # # Print results
                # for c in det[:, -1].unique():
                #     n = (det[:, -1] == c).sum()  # detections per class
                #     s += f"{n} {names[int(c)]}{'s' * (n > 1)}, "  # add to string

                # Adapt detections to deep sort input format
                for *xyxy, conf, cls in (det):
                    # to deep sort format
                    #x_c, y_c, bbox_w, bbox_h = xyxy_to_xywh(*xyxy)
                    x1,y1,x2,y2 = get_xyxy(*xyxy)
                    xywh_obj = [x1,y1,x2,y2]
                    xywh_bboxs.append(xywh_obj)
                    confs.append(conf.item())
                    classes.append(names[int(cls)])
        
        y = np.zeros((len(xywh_bboxs),4),dtype='float64')

        if xywh_bboxs:
            y = np.array([np.array(xi) for xi in xywh_bboxs])
        labels = np.array(classes)
        scores = np.array(confs,dtype='float64')
        
        return y,scores,labels
    
    