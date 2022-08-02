import json
import os

# key为MediaPipe BlazePose的原始pose keyPoint的名称，value为对应的Coco的keyPoint的名称
import time

from kinematics_extraction import kinematics_extract
from kinematics_processing import kinematics_process
from visualizer_common import plot_avg_gcLR_all, gif_pose, gif_flexext, gif_abdadd

key_blaze_value_coco = {
    0: 0,
    2: 1,
    5: 2,
    7: 3,
    8: 4,
    11: 5,
    12: 6,
    13: 7,
    14: 8,
    15: 9,
    16: 10,
    23: 11,
    24: 12,
    25: 13,
    26: 14,
    27: 15,
    28: 16
}


# 将空间中的点投影到二维平面
def project_point_to_plane(point, axis):
    point_projected = []
    if axis == 'F':
        point_projected.append(point[0])
        point_projected.append(point[1])
    elif axis == 'S':
        point_projected.append(point[2])
        point_projected.append(point[1])
    return point_projected


# 3D动作根据投影方向转换为2D动作
def convert_plot3D_to_plot2D(keyPoints, dim, axis):
    _point = [keyPoints[0] * (dim[0]),
              keyPoints[1] * (dim[1]),
              keyPoints[2] * (dim[2])]
    if _point[2] < 0:
        _point[2] = abs(_point[2])
    if _point[0] < 0 or _point[1] < 0:
        _point[0] = -1
        _point[1] = -1
        _point[2] = -1
    keyPoints_converted = project_point_to_plane(_point, axis)
    return keyPoints_converted


# 将BlazePose的pose转换为Coco的pose
def covert_blaze_to_coco(blaze_pose, dim, axis):
    coco_pose = []
    for i in range(len(blaze_pose)):
        # 判断key是否在key_blaze_value_coco中
        if i in key_blaze_value_coco:
            coco_pose.append(convert_plot3D_to_plot2D(blaze_pose[key_blaze_value_coco[i]], dim, axis))
    return coco_pose


def dump_coco_from_blaze_json(file_path, poseFile):
    cocoData = {}

    if not os.path.exists(file_path):
        print(file_path + ' not exist')
        exit(1)
    # 读取BlazePose的json文件
    with open(file_path, 'r') as f:
        blazePoseRaw = json.load(f)
    cocoData['partId'] = blazePoseRaw['partId']
    cocoData['capId'] = blazePoseRaw['capId']
    cocoData['dimF'] = [blazePoseRaw['dim'][0], blazePoseRaw['dim'][1]]
    cocoData['dimS'] = [blazePoseRaw['dim'][2], blazePoseRaw['dim'][1]]
    cocoData['dataF'] = []
    cocoData['dataS'] = []

    # 遍历blazePoseRaw中的每一个pose
    for pose in blazePoseRaw['data']:
        pose_converted_axis_F = covert_blaze_to_coco(pose, blazePoseRaw['dim'], 'F')
        cocoData['dataF'].append(pose_converted_axis_F)
        pose_converted_axis_S = covert_blaze_to_coco(pose, blazePoseRaw['dim'], 'S')
        cocoData['dataS'].append(pose_converted_axis_S)

    cocoData['lenF'] = len(cocoData['dataF'])
    cocoData['lenS'] = len(cocoData['dataS'])

    # 保存json
    with open(poseFile, 'w') as f:
        json.dump([cocoData], f)


if __name__ == '__main__':
    basePath = './test/'
    file_path = basePath + 'cv-data-2022.08.01.16.54'

    # dump coco from blaze json
    poseFile = file_path + '_pose.json'
    dump_coco_from_blaze_json(file_path, poseFile)

    # kinematics angles extraction
    anglesFile = file_path + '_angles.json'
    start_time = time.time()
    kinematics_extract(poseFile, anglesFile)
    print('Kinematics extracted and saved in', '\"' + anglesFile + '\"', '[Time:',
          '{0:.2f}'.format(time.time() - start_time), 's]')

    # kinematics processing
    gcFile = file_path + '_gc.json'
    start_time = time.time()
    kinematics_process(poseFile, anglesFile, gcFile)
    print('Kinematics processed and saved in', '\"' + gcFile + '\"', '[Time:',
          '{0:.2f}'.format(time.time() - start_time), 's]')

    # plot average gcLR
    # plot_avg_gcLR_all(gcFile)

    # gif_pose(poseFile, basePath)
    # gif_flexext(poseFile, anglesFile, basePath)
    # gif_abdadd(poseFile, anglesFile, basePath)
