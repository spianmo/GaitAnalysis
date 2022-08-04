from pose_estimation import estimate_poses
import time
import os

path = '.\\Part\\'


def step1():
    if not os.path.exists(path):
        os.makedirs(path)

    writeFile = path + 'Part01_pose.json'
    if not os.path.exists(writeFile):
        f = open(writeFile, 'w')
        f.close()

    start_time = time.time()
    estimate_poses(path, writeFile)
    print('Poses estimated and saved in', '\"' + writeFile + '\"', '[Time:',
          '{0:.2f}'.format(time.time() - start_time), 's]')


from kinematics_extraction import kinematics_extract


def step2():
    readFile = path + 'Part01_pose.json'
    writeFile = path + 'Part01_angles.json'
    start_time = time.time()
    kinematics_extract(readFile, writeFile)
    print('Kinematics extracted and saved in', '\"' + writeFile + '\"', '[Time:',
          '{0:.2f}'.format(time.time() - start_time), 's]')


from kinematics_processing import kinematics_process


def step3():
    poseFile = path + 'Part01_pose.json'
    anglesFile = path + 'Part01_angles.json'
    writeFile = path + 'Part01_gc.json'
    start_time = time.time()
    kinematics_process(poseFile, anglesFile, writeFile)
    print('Kinematics processed and saved in', '\"' + writeFile + '\"', '[Time:',
          '{0:.2f}'.format(time.time() - start_time), 's]')


from visualizer import gif_flexext, gif_abdadd, gif_pose, plot_avg_gcLR_all, plot_raw_all_file


def step4():
    poseFile = path + 'Part01_pose.json'
    anglesFile = path + 'Part01_angles.json'
    gcFile = path + 'Part01_gc.json'
    plot_avg_gcLR_all(gcFile)

    i = 1  # The gait number
    gif_pose(poseFile, i, path)
    gif_flexext(poseFile, anglesFile, i, path)
    gif_abdadd(poseFile, anglesFile, i, path)


if __name__ == '__main__':
    step1()
    step2()
    step3()
    step4()
