from __future__ import print_function
import sys
import os
import cv2
import time
import datetime
from openvino.inference_engine import IENetwork, IEPlugin
import numpy as np
from centroidtracker import CentroidTracker

model_xml = 'FP16/person-detection-retail-0013-fp16.xml'
model_bin = 'FP16/person-detection-retail-0013-fp16.bin'

# Plugin initialization for specified device and load extensions library if specified
plugin = IEPlugin(device='MYRIAD', plugin_dirs=None)

# Read IR
net = IENetwork(model=model_xml, weights=model_bin)

assert len(net.inputs.keys()) == 1, "Demo supports only single input topologies"
assert len(net.outputs) == 1, "Demo supports only single output topologies"
input_blob = next(iter(net.inputs))
out_blob = next(iter(net.outputs))
exec_net = plugin.load(network=net, num_requests=2)
# Read and pre-process input image
n, c, h, w = net.inputs[input_blob].shape
del net


model_xml = 'FP16/face-detection-adas-0001.xml'
model_bin = 'FP16/face-detection-adas-0001.bin'

# Read IR
net = IENetwork(model=model_xml, weights=model_bin)

assert len(net.inputs.keys()) == 1, "Demo supports only single input topologies"
assert len(net.outputs) == 1, "Demo supports only single output topologies"
input_blob_face = next(iter(net.inputs))
out_blob_face = next(iter(net.outputs))
exec_net_face = plugin.load(network=net)
# Read and pre-process input image
n, c2, h2, w2 = net.inputs[input_blob_face].shape
del net

model_xml = 'FP16/age-gender-recognition-retail-0013-fp16.xml'
model_bin = 'FP16/age-gender-recognition-retail-0013-fp16.bin'

# Read IR
net = IENetwork(model=model_xml, weights=model_bin)

# assert len(net.inputs.keys()) == 1, "Demo supports only single input topologies"
# assert len(net.outputs) == 1, "Demo supports only single output topologies"
input_blob_agegender = next(iter(net.inputs))
out_blob_agegender = next(iter(net.outputs))
exec_net_agegender = plugin.load(network=net)
# Read and pre-process input image
n, c3, h3, w3 = net.inputs[input_blob_agegender].shape
del net

def get_agegender(face_img, exec_net, c, h, w):
    GENDER = ['FEMALE', 'MALE']
    # Resize image
    processedImg = cv2.resize(face_img, (h, w))

    # Change data layout from HWC to CHW
    processedImg = processedImg.transpose((2, 0, 1))
    processedImg = processedImg.reshape((1, c, h, w))

    ag_res = exec_net.infer(inputs={input_blob_agegender: processedImg})
    # print('ag_res',ag_res,'<<<')
    # Handling age
    age = ag_res['age_conv3']
    age = int(age * 100)

    # Handling gender
    gender = ag_res['prob']
    gender = np.argmax(gender)
    gender = GENDER[gender]

    return age, gender

out_w = 640
out_h = 480

video_path = 'kizon7_通路4_2019-05-10T12-20-00.ts' # '/home/thaopn/Downloads/face_agender/video.mp4'
video_path = 'model_test.mp4'
cap = cv2.VideoCapture(video_path)
initial_w = cap.get(3)
initial_h = cap.get(4)
fps = cap.get(cv2.CAP_PROP_FPS)
fourcc = cv2.VideoWriter_fourcc(*'XVID')
writer = cv2.VideoWriter('output.avi', fourcc, fps, (int(initial_w), int(initial_h)))

ct = CentroidTracker(10)

f = open('inference_time_log.txt', 'w')

while cv2.waitKey(1) < 0:
    person_rect = []

    hasFrame, frame = cap.read()
    #frame = cv2.resize(frame, (out_w, out_h))
    if not hasFrame:
        break

    inf_start = time.time()
    # Person detection
    person_in_frame = cv2.resize(frame, (w, h))
    person_in_frame = person_in_frame.transpose((2, 0, 1))  # Change data layout from HWC to CHW
    person_in_frame = person_in_frame.reshape((n, c, h, w))

    face_in_frame = cv2.resize(frame, (w2, h2))
    face_in_frame = face_in_frame.transpose((2, 0, 1))  # Change data layout from HWC to CHW
    face_in_frame = face_in_frame.reshape((n, c2, h2, w2))

    res = exec_net.infer(inputs={input_blob: person_in_frame})
    output_node_name = list(res.keys())[0]
    res = res[output_node_name]

    for obj in res[0][0]:
        # Draw only objects when probability more than specified threshold
        if obj[2] > 0.5:
            xmin = int(obj[3] * initial_w)
            ymin = int(obj[4] * initial_h)
            xmax = int(obj[5] * initial_w)
            ymax = int(obj[6] * initial_h)


            person_rect.append((xmin, ymin, xmax, ymax))

            class_id = 21
            # Draw box and label\class_id
            color = (min(class_id * 12.5, 255), min(class_id * 7, 255), min(class_id * 5, 255))
            cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), color, 2)
            det_label = 'person'
            cv2.putText(frame, det_label + ' ' + str(round(obj[2] * 100, 1)) + ' %', (xmin, ymin - 7),
                        cv2.FONT_HERSHEY_COMPLEX, 0.6, color, 1)

    objects = ct.update(person_rect)
    # loop over the tracked objects
    for (objectID, centroid) in objects.items():
        # draw both the ID of the object and the centroid of the
        # object on the output frame
        text = "ID {}".format(objectID)
        cv2.putText(frame, text, (centroid[0] - 10, centroid[1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        cv2.circle(frame, (centroid[0], centroid[1]), 4, (0, 255, 0), -1)
    # Face detection
    res = exec_net_face.infer(inputs={input_blob_face: face_in_frame})
    output_node_name = list(res.keys())[0]
    res = res[output_node_name]

    for obj in res[0][0]:
        # Draw only objects when probability more than specified threshold
        if obj[2] > 0.5:
            xmin = int(obj[3] * initial_w)
            ymin = int(obj[4] * initial_h)
            xmax = int(obj[5] * initial_w)
            ymax = int(obj[6] * initial_h)

            face_croped = frame[ymin:ymax, xmin:xmax]
            age, gender = get_agegender(face_croped, exec_net_agegender, c3, h3, w3)

            class_id = 5
            # Draw box and label\class_id
            color = (min(class_id * 12.5, 255), min(class_id * 7, 255), max(class_id * 5, 255))
            cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), color, 2)
            text = 'face:{}%{}-{}'.format(round(obj[2] * 100, 1), age, gender)  # labels_map[class_id] if labels_map else str(class_id)
            cv2.putText(frame, text, (xmin, ymin - 7),
                        cv2.FONT_HERSHEY_COMPLEX, 0.6, color, 1)
    inf_end = time.time()
    det_time = inf_end - inf_start
    print(datetime.timedelta(seconds=det_time).total_seconds())
    print(datetime.timedelta(seconds=det_time).total_seconds(), file=f)
    # writer.write(frame)
    # cv2.imshow('results', frame)

writer.release()
cap.release()
cv2.destroyAllWindows()
