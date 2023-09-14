# YOLOv5 Model Serving on RHODS

This repository provides instructions and examples on how to deploy a YOLOv5 model (or a model retrained from it) using RHODS Model Serving, and how to query it both with and **gRPC** and **REST**.

## YOLO and YOLOv5

YOLO (You Only Look Once) is a popular object detection and image segmentation model developed by Joseph Redmon and Ali Farhadi at the University of Washington. The first version of YOLO was released in 2015 and quickly gained popularity due to its high speed and accuracy.

YOLOv2 was released in 2016 and improved upon the original model by incorporating batch normalization, anchor boxes, and dimension clusters. YOLOv3 was released in 2018 and further improved the model's performance by using a more efficient backbone network, adding a feature pyramid, and making use of focal loss.

In 2020, YOLOv4 was released which introduced a number of innovations such as the use of Mosaic data augmentation, a new anchor-free detection head, and a new loss function.

In 2021, Ultralytics released [YOLOv5](https://github.com/ultralytics/yolov5/), which further improved the model's performance and added new features such as support for panoptic segmentation and object tracking.

YOLO has been widely used in a variety of applications, including autonomous vehicles, security and surveillance, and medical imaging. It has also been used to win several competitions, such as the COCO Object Detection Challenge and the DOTA Object Detection Challenge.

## Working with YOLOv5 on RHODS

As YOLOv5 is based on PyTorch, you can use the built-in **PyTorch notebook container image** to work with the provided files.

We are going to serve our model using the [ONNX](https://onnx.ai/) format, a general purpose open format built to represent machine learning models. RHODS Model Serving includes the OpenVino serving runtime that accepts two formats for models: OpenVino IR, its own format, and ONNX.

**NOTE**: Many files and code in this repo, especially the ones from the `utils` and `models` folders, come directly from the YOLOv5 repository. They includes many utilities and functions needed for image pre-processing and post-processing. I kept only what is needed, rearranged in a way easier to follow with notebooks. YOLOv5 includes many different tools and CLI commands that are worth learning, so don't hesitate to have a look at it directly.

## Converting a YOLOv5 model to ONNX

YOLOv5 is based on PyTorch. So base YOLOv5 models, or the ones you retrain using this framework, will come in the form of a `model.pt` file.

To convert this model to the ONNX format, you can use the notebook [`01-yolov5_to_onnx.ipynb`](01-yolov5_to_onnx.ipynb).

The notebook will guide you through all the steps for the conversion. If you don't want to do it at this time, you can also find in this repo the original YOLOv5 "nano" model, `yolov5n.pt`, and its already converted ONNX version, `yolov5n.onnx`.

Once converted, you can save/upload your ONNX model to the storage you will use in your Data Connection on RHODS.

## Model serving

Here we can use the standard configuration path for RHODS Model Serving:

- Create a Data Connection to the storage where you saved your model. In this example we don't need to expose an external Route, but of course you can. In this case though, you won't be able to directly see the internal gRPC and REST endpoints in the RHODS UI, you will have to get them from the Network->Services panel in the OpenShift Console.
- Create a Model Server, then deploy the model using the ONNX format. In the case of object storage, the location of the model must be `/` if you put it at the root, or `path/subpath`, without any leading `/` if it is in a folder.

## gRPC connection

With the gRPC interface, you have access to different Services. They are described, along with their format, in the [`grpc_predict_v2.proto`](grpc_predict_v2.proto) file.

There are lots of important information in this file: how to query the service, how to format the data,... This is really important as the data format is not something you can "invent", and not exactly the same compared as the REST interface (!).

This proto file, which is a service description meant to be used with any programming language, has already been converted to usable Python modules defining objects and classes to be used to interact with the service: [`grpc_predict_v2_pb2.py`](grpc_predict_v2_pb2.py) and [`grpc_predict_v2_pb2_grpc.py`](grpc_predict_v2_pb2_grpc.py). If you want to learn more about this, the conversion can be done using the [protoc](https://grpc.io/docs/protoc-installation/) tool.

You can use the notebook [`02-grpc.ipynb`](02-grpc.ipynb) to connect to the interface and test some of the services. You will see that many "possible" services from ModelMesh are unfortunately simply not implemented with the OpenVino backend at the time of this writing. But at least `ModelMetadata` will give some information on the formats we have to use for inputs and outputs when doing the inference.

## Consuming the model over gRPC

In the [`03-remote_inference_grpc.ipynb`](03-remote_inference_grpc.ipynb) notebook, you will find a full example on how to query the grpc endpoint to make an inference. It is backed by the file [`remote_infer_grpc.py`](remote_infer_grpc.py), where most of the relevant code is:

- Image preprocessing on L35: reads the image and transforms it in a proper numpy array
- gRPC request content building on L44: transforms the array in the expected input shape (refer to model metadata obtained in the previous notebook), then flatten it as expected by ModelMesh.
- gRPC calling on L58.
- Response processing on L73: reshape the response from flat array to expected output shape (refer to model metadata obtained in the previous notebook), run NMS to remove overlapping boxes, draw the boxes from results.

The notebook gives the example for one image, as well as the processing of several ones from the `images` folder. This allows for a small benchmark on processing/inference time.

## Consuming the model over REST

In the [`04-remote_inference_rest.ipynb`](04-remote_inference_rest.ipynb) notebook, you will find a full example on how to query the gRPC endpoint to make an inference. It is backed by the file [`remote_infer_rest.py`](remote_infer_rest.py), where most of the relevant code is:

- Image preprocessing on L30: reads the image and transforms it in a proper numpy array
- Payload building on L39: transforms the array in the expected input shape (refer to model metadata obtained in the previous notebook).
- REST calling on L54.
- Response processing on L60: reshape the response from flat array to expected output shape (refer to model metadata obtained in the previous notebook), run NMS to remove overlapping boxes, draw the boxes from results.

The notebook gives the example for one image, as well as the processing of several ones from the `images` folder. This allows for a small benchmark on processing/inference time.

## gRPC vs REST

Here are a few elements to help you choose between the two available interfaces to query your model:

- REST is easier to implement: it is a much better known protocol for most people, and involves a little bit less programming. There is no need to create a connection, instantiate objects,... So it's often easier to use.
- If you want to query the model directly from outside OpenShift, you have to use REST which is the only one exposed. You can expose gRPC too, but it's kind of difficult right now.
- gRPC is **wwwwwaaaayyyyy much faster** than REST. With the exact same model serving instance, as showed in the notebooks, inferences are about 30x faster. That is huge when you have score of images to process.
