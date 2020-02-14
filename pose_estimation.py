#==================================================================================
#                               POSE ESTIMATION
#----------------------------------------------------------------------------------
#                           Input: Video x 2, Output: JSON
#               Given a front/back view and side view video of someone
#               walking, this will generate a json, describing the pose
#               via key-points in graph form, throughout every frame.
#----------------------------------------------------------------------------------
#==================================================================================
# TODO: Later expand to store more than just one pair of videos per person (for average)

#==================================================================================
#                                   Imports
#==================================================================================
from __future__ import division
from gluoncv.data.transforms.pose import detector_to_alpha_pose, heatmap_to_coord_alpha_pose
from gluoncv.utils.viz import cv_plot_image, cv_plot_keypoints
from gluoncv.model_zoo import get_model
import matplotlib.pyplot as plt
import gluoncv as gcv
import numpy as np
import mxnet as mx
import time, cv2
import json

#==================================================================================
#                                   AI Detectors
#                        Object detector; YOLO via GPU.
#                Pose Estimator; AlphaPose via CPU (no GPU support).
#==================================================================================
ctx = mx.gpu(0)
detector = get_model('yolo3_mobilenet1.0_coco', pretrained=True, ctx=ctx)
detector.reset_class(classes=['person'], reuse_weights={'person': 'person'})
estimator = get_model('alpha_pose_resnet101_v1b_coco', pretrained='de56b871')
detector.hybridize()
estimator.hybridize()

#==================================================================================
#                                   Methods
#==================================================================================
# Currently for debugging, seeing that everything is spotted well
def plot_debug(img, coords, confidence, class_ids, bboxes, scores,
                   box_thresh=0.5, keypoint_thresh=0.2):

    if isinstance(coords, mx.nd.NDArray):
        coords = coords.asnumpy()
    if isinstance(bboxes, mx.nd.NDArray):
        bboxes = bboxes.asnumpy()
    if isinstance(scores, mx.nd.NDArray):
        scores = scores.asnumpy()
    if isinstance(confidence, mx.nd.NDArray):
        confidence = confidence.asnumpy()

    joint_visible = confidence[:, :, 0] > keypoint_thresh
    joint_pairs = [[0, 1], [1, 3], [0, 2], [2, 4],
                   [5, 6], [5, 7], [7, 9], [6, 8], [8, 10],
                   [5, 11], [6, 12], [11, 12],
                   [11, 13], [12, 14], [13, 15], [14, 16]]

    bbox_first = bboxes[0][0]
    x_min = bbox_first[0]
    y_min = bbox_first[1]
    x_max = bbox_first[2]
    y_max= bbox_first[3]

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1) # img.shape[1], img.shape[0] (BELOW)
    ax.set(xlim=(0, img.shape[1]), ylim = (0, img.shape[0])) # setting width and height of plot
    #ax.invert_yaxis()

    i = scores.argmax() # gets index of most confident bbox estimation
    colormap_index = np.linspace(0, 1, len(joint_pairs))
    pts = coords[i]

    for cm_ind, jp in zip(colormap_index, joint_pairs):
        if joint_visible[i, jp[0]] and joint_visible[i, jp[1]]:

            ax.plot(pts[jp, 0] - x_min, y_max - pts[jp, 1],
                    linewidth=3.0, alpha=0.7, color=plt.cm.cool(cm_ind))
            ax.scatter(pts[jp, 0] - x_min, y_max - pts[jp, 1], s=20)

    return ax

# Given one video, returns list of pose information in preparation for json file
def video_to_listPose(vid):
    cap = cv2.VideoCapture(vid) # load video

    # Iterate through every frame in video
    while(cap.isOpened()):
        ret, frame = cap.read() # read current frame
        if (frame is None): break # If current frame doesn't exist, finished
        frame = mx.nd.array(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)).astype('uint8') # mxnet readable

        # Object detection
        x, frame = gcv.data.transforms.presets.yolo.transform_test(frame)  # short=512, max_size=350
        class_IDs, scores, bounding_boxs = detector(x.as_in_context(ctx))

        # Pose estimation
        pose_input, upscale_bbox = detector_to_alpha_pose(frame, class_IDs, scores, bounding_boxs,
                                                          output_shape=(320, 256))

        if len(upscale_bbox) > 0: # person detected
            predicted_heatmap = estimator(pose_input)
            pred_coords, confidence = heatmap_to_coord_alpha_pose(predicted_heatmap, upscale_bbox)

            img = cv_plot_keypoints(frame, pred_coords, confidence, class_IDs, bounding_boxs, scores,
                                    box_thresh=0.5, keypoint_thresh=0.2)
            ax = plot_debug(img, pred_coords, confidence, class_IDs, bounding_boxs, scores, box_thresh=0.5,
                            keypoint_thresh=0.2)
        cv_plot_image(img)
        plt.show()
        cv2.waitKey(1)
    cap.release()

# Given two videos it will output the json describing all poses in both videos
def videos_to_jsonPose(vidSide, vidFront):
    video_to_listPose(vidSide)
    #frontView_list = video_to_listPose(vidFront)


#==================================================================================
#                                   Main
#==================================================================================
path = '../Test/'
vidSide = path + 'Part01test-side.avi'
vidFront = path + 'Part01test-front.avi'
videos_to_jsonPose(vidSide, vidFront)