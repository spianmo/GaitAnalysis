# ==================================================================================
#                               VISUALIZER
# ----------------------------------------------------------------------------------
#                    Input: JSON, Output: Debugging plots / Gifs
#               Visualizes saved graph structure of poses, as well as
#               saved raw kinematics, and processed kinematics
# ==================================================================================
#                                   Imports
# ==================================================================================
import numpy as np
import matplotlib.pyplot as plt
import json
import io
from PIL import Image
import imageio
from tqdm import trange
import matplotlib.gridspec as gridspec

# ==================================================================================
#                                   Constants
# ==================================================================================
joint_pairs = [[0, 1], [1, 3], [0, 2], [2, 4],
               [5, 6], [5, 7], [7, 9], [6, 8], [8, 10],
               [5, 11], [6, 12], [11, 12],
               [11, 13], [12, 14], [13, 15], [14, 16]]
colormap_index = np.linspace(0, 1, len(joint_pairs))

ptID = {
    'nose': 0,
    'eye_L': 1, 'eye_R': 2,
    'ear_L': 3, 'ear_R': 4,
    'shoulder_L': 5, 'shoulder_R': 6,
    'elbow_L': 7, 'elbow_R': 8,
    'wrist_L': 9, 'wrist_R': 10,
    'hip_L': 11, 'hip_R': 12,
    'knee_L': 13, 'knee_R': 14,
    'ankle_L': 15, 'ankle_R': 16
}

red = "#FF4A7E"
blue = "#72B6E9"


# ==================================================================================
#                                   Methods
# ==================================================================================
# Speeds up gif
def gif_speedup(filename):
    gif = imageio.mimread(filename, memtest=False)
    imageio.mimsave(filename, gif, duration=1 / 30)


# Saves gif of pose estimation in a capture
def gif_pose(poseFile, i, outpath):
    with open(poseFile, 'r') as f:
        jsonPose = json.load(f)

    dataS = jsonPose[i - 1]['dataS']
    dimS = jsonPose[i - 1]['dimS']
    dataF = jsonPose[i - 1]['dataF']
    dimF = jsonPose[i - 1]['dimF']
    capId = jsonPose[i - 1]['capId']
    partId = jsonPose[i - 1]['partId']

    filename = outpath + partId + '-' + capId + '-PE.gif'
    ims = []  # List of images for gif

    print('Visualizing poses...')
    for i in trange(len(dataS), ncols=100):
        fig, (axF, axS) = plt.subplots(1, 2, figsize=(10, 4), constrained_layout=True)
        fig.suptitle('Pose estimation of \"' + partId + '-' + capId + '\"')

        axF.set_xlabel('Front view')
        axF.set(xlim=(0, dimF[0]), ylim=(0, dimF[1]))

        axS.set_xlabel('Side view')
        axS.set(xlim=(0, dimS[0]), ylim=(0, dimS[1]))

        # Front view
        pose = dataF[i]
        for cm_ind, jp in zip(colormap_index, joint_pairs):
            joint1 = pose[jp[0]]
            joint2 = pose[jp[1]]
            if (joint1 > [-1, -1] and joint2 > [-1, -1]):
                x = [joint1[0], joint2[0]]
                y = [joint1[1], joint2[1]]
                axF.plot(x, y, linewidth=3.0, alpha=0.7, color=plt.cm.cool(cm_ind))
                axF.scatter(x, y, s=20)

        # Side view
        pose = dataS[i]
        for cm_ind, jp in zip(colormap_index, joint_pairs):
            joint1 = pose[jp[0]]
            joint2 = pose[jp[1]]
            if (joint1 > [-1, -1] and joint2 > [-1, -1]):
                x = [joint1[0], joint2[0]]
                y = [joint1[1], joint2[1]]
                axS.plot(x, y, linewidth=3.0, alpha=0.7, color=plt.cm.cool(cm_ind))
                axS.scatter(x, y, s=20)

        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        im = Image.open(buf)
        im = im.convert('RGB')
        ims.append(im)
        plt.close()
    im.save(filename, save_all=True, append_images=ims, duration=0, loop=0)
    buf.close()
    gif_speedup(filename)
    print('Saved as', '\"' + filename + '\"')


# Returns x and y lists of leg catering for no keypoint detection
def leg_points(pose, L_or_R):
    x, y = [], []

    hip = pose[ptID['hip_' + L_or_R]]
    knee = pose[ptID['knee_' + L_or_R]]
    ankle = pose[ptID['ankle_' + L_or_R]]

    if (hip != [-1, -1]):
        x.append(hip[0])
        y.append(hip[1])
    if (knee != [-1, -1]):
        x.append(knee[0])
        y.append(knee[1])
    if (ankle != [-1, -1]):
        x.append(ankle[0])
        y.append(ankle[1])

    return x, y


# Saves gif describing flexion/extension angle extraction from side view
def gif_flexext(poseFile, anglesFile, i, outpath):
    with open(poseFile, 'r') as f:
        jsonPose = json.load(f)
    with open(anglesFile, 'r') as f:
        jsonAngles = json.load(f)

    dataS = jsonPose[i - 1]['dataS']
    dimS = jsonPose[i - 1]['dimS']
    capId = jsonPose[i - 1]['capId']
    partId = jsonPose[i - 1]['partId']
    knee_FlexExt = jsonAngles[i - 1]['knee_FlexExt']
    hip_FlexExt = jsonAngles[i - 1]['hip_FlexExt']

    filename = outpath + partId + '-' + capId + '-FE.gif'
    ims = []  # List of images for gif
    gs = gridspec.GridSpec(2, 2)

    print('Visualizing flexion and extension...')
    for i in trange(len(dataS), ncols=100):
        fig = plt.figure(figsize=(12, 6))
        ax1 = fig.add_subplot(gs[:, 0])
        ax2 = fig.add_subplot(gs[0, 1])
        ax3 = fig.add_subplot(gs[1, 1])

        # ax1: Leg poses
        ax1.set_title('Flexion and Extension from Side View')
        ax1.set(xlim=(0, dimS[0]), ylim=(0, dimS[1]))
        pose = dataS[i]
        x_L, y_L = leg_points(pose, 'L')
        x_R, y_R = leg_points(pose, 'R')
        ax1.scatter(x_L, y_L, s=20, color=red)
        ax1.scatter(x_R, y_R, s=20, color=blue)
        ax1.plot(x_L, y_L, color=red)
        ax1.plot(x_R, y_R, color=blue)

        # ax2: Knee flexion / extension
        ax2.set_title('Knee Flexion/Extension')
        ax2.set_ylabel(r"${\Theta}$ (degrees)")
        ax2.set(xlim=(0, len(dataS)), ylim=(-20, 80))
        ax2.plot(knee_FlexExt[0][0:i], color=red)
        ax2.plot(knee_FlexExt[1][0:i], color=blue)

        # ax3: Hip flexion / extension
        ax3.set_title('Hip Flexion/Extension')
        ax3.set_ylabel(r"${\Theta}$ (degrees)")
        ax3.set_xlabel('Frame (count)')
        ax3.set(xlim=(0, len(dataS)), ylim=(-30, 60))
        ax3.plot(hip_FlexExt[0][0:i], color=red)
        ax3.plot(hip_FlexExt[1][0:i], color=blue)

        buf = io.BytesIO()
        plt.tight_layout()
        plt.savefig(buf, format='png')
        buf.seek(0)
        im = Image.open(buf)
        im = im.convert('RGB')
        ims.append(im)
        plt.close()
    im.save(filename, save_all=True, append_images=ims, duration=0, loop=0)
    buf.close()
    gif_speedup(filename)
    print('Saved as', '\"' + filename + '\"')


# Saves gif describing flexion/extension angle extraction from side view
def gif_abdadd(poseFile, anglesFile, i, outpath):
    with open(poseFile, 'r') as f:
        jsonPose = json.load(f)
    with open(anglesFile, 'r') as f:
        jsonAngles = json.load(f)

    dataF = jsonPose[i - 1]['dataF']
    dimF = jsonPose[i - 1]['dimF']
    capId = jsonPose[i - 1]['capId']
    partId = jsonPose[i - 1]['partId']
    knee_AbdAdd = jsonAngles[i - 1]['knee_AbdAdd']
    hip_AbdAdd = jsonAngles[i - 1]['hip_AbdAdd']

    filename = outpath + partId + '-' + capId + '-AA.gif'
    ims = []  # List of images for gif
    gs = gridspec.GridSpec(2, 2)

    print('Visualizing flexion and extension...')
    for i in trange(len(dataF), ncols=100):
        fig = plt.figure(figsize=(12, 6))
        ax1 = fig.add_subplot(gs[:, 0])
        ax2 = fig.add_subplot(gs[0, 1])
        ax3 = fig.add_subplot(gs[1, 1])

        # ax1: Leg poses
        ax1.set_title('Abduction and Adduction from Front View')
        ax1.set(xlim=(0, dimF[0]), ylim=(0, dimF[1]))
        pose = dataF[i]
        x_L, y_L = leg_points(pose, 'L')
        x_R, y_R = leg_points(pose, 'R')
        ax1.scatter(x_L, y_L, s=20, color=red)
        ax1.scatter(x_R, y_R, s=20, color=blue)
        ax1.plot(x_L, y_L, color=red)
        ax1.plot(x_R, y_R, color=blue)

        # ax2: Knee abduction / adduction
        ax2.set_title('Knee Abduction/Adduction')
        ax2.set_ylabel(r"${\Theta}$ (degrees)")
        ax2.set(xlim=(0, len(dataF)), ylim=(-20, 20))
        ax2.plot(knee_AbdAdd[0][0:i], color=red)
        ax2.plot(knee_AbdAdd[1][0:i], color=blue)

        # ax3: Hip abduction / adduction
        ax3.set_title('Hip Abduction/Adduction')
        ax3.set_xlabel('Frame (count)')
        ax3.set_ylabel(r"${\Theta}$ (degrees)")
        ax3.set(xlim=(0, len(dataF)), ylim=(-20, 30))
        ax3.plot(hip_AbdAdd[0][0:i], color=red)
        ax3.plot(hip_AbdAdd[1][0:i], color=blue)

        buf = io.BytesIO()
        plt.tight_layout()
        plt.savefig(buf, format='png')
        buf.seek(0)
        im = Image.open(buf)
        im = im.convert('RGB')
        ims.append(im)
        plt.close()
    im.save(filename, save_all=True, append_images=ims, duration=0, loop=0)
    buf.close()
    gif_speedup(filename)
    print('Saved as', '\"' + filename + '\"')


# Plots kinematics of left or right leg, used for viewing all gait cycles
def plot_angles(angleList, title, isRed):
    if (isRed):
        color = red
    else:
        color = blue
    fig, ax = plt.subplots()
    ax.set_title(title)
    ax.set_xlabel('Time (%)')  #
    ax.set_ylabel(r"${\Theta}$ (degrees)")
    ax.plot(angleList, color=color)
    #plt.show()
    plt.savefig('./Part/' + title.replace('/', '-') + '.png', format='png')  # 保存图⽚完整
    plt.close()


# Plots kinematics of left or right leg, used for viewing all gait cycles
def plot_anglesLR(angleList, title, xlabel):
    xmax = max(len(angleList[0]), len(angleList[1]))
    fig, ax = plt.subplots()
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(r"${\Theta}$ (degrees)")
    ax.plot(angleList[0], color=red, label='Left')
    ax.plot(angleList[1], color=blue, label='Right')
    ax.legend()
    #plt.show()
    plt.savefig('./Part/' + title.replace('/', '-') + '.png', format='png')  # 保存图⽚完整
    plt.close()


# Plots each angle list gait cycle in list
def plot_gc(gc, title, isRed):
    for angleList in gc:
        plot_angles(angleList, title, isRed)


# Plots left and right gait cycles
def plot_gcLR(gcLR, title):
    plot_gc(gcLR[0], title, True)
    plot_gc(gcLR[1], title, False)


# Plots average as well as standard deviation
def plot_avg(avg, std, title, N, isRed):
    if (isRed):
        color = red
    else:
        color = blue

    xmax = len(avg)
    fig, ax = plt.subplots()
    ax.set_title(title + ' (' + str(N) + ' Gait Cycles)')
    ax.set_xlabel('Time (%)')
    ax.set_ylabel(r"${\Theta}$ (degrees)")
    ax.set_xlim(0, 100)
    ax.plot(avg, color=color)

    std1_gcL = (np.array(avg) + np.array(std)).tolist()
    std2_gcL = (np.array(avg) - np.array(std)).tolist()
    ax.plot(std1_gcL, '--', color=color)
    ax.plot(std2_gcL, '--', color=color)


# Plots left and right average as well as standard deviation
def plot_avg_gcLR(avg_LR, title, plotSep):
    avg_gcL = avg_LR['gcL_avg']
    avg_gcR = avg_LR['gcR_avg']
    std_gcL = avg_LR['gcL_std']
    std_gcR = avg_LR['gcR_std']
    N_L = avg_LR['gcL_count']
    N_R = avg_LR['gcR_count']

    if (not plotSep):
        leftMax = len(avg_gcL) - 1
        rightMax = len(avg_gcR) - 1
        xmax = max(leftMax, rightMax)
        fig, ax = plt.subplots()
        ax.set_title(title + ' (' + str(N_L) + 'L, ' + str(N_R) + 'R Gait Cycles)')
        ax.set_xlabel('Frame')  # Time (%)
        ax.set_ylabel(r"${\Theta}$ (degrees)")
        ax.plot(avg_gcL, color=red)
        ax.plot(avg_gcR, color=blue)
        ax.set_xlim(0, 100)
        #plt.show()
        plt.savefig('./Part/' + title.replace('/', '-') + '.png', format='png')  # 保存图⽚完整
        plt.close()
    else:
        plot_avg(avg_gcL, std_gcL, title, N_L, isRed=True)
        plot_avg(avg_gcR, std_gcR, title, N_R, isRed=False)
        #plt.show()
        plt.savefig('./Part/' + title.replace('/', '-') + '.png', format='png')  # 保存图⽚完整
        plt.close()


def plot_avg_gcLR_all(gcFile):
    with open(gcFile, 'r') as f:
        gc = json.load(f)

    knee_FlexExt_avg = gc['knee_FlexExt_avg']
    hip_FlexExt_avg = gc['hip_FlexExt_avg']
    knee_AbdAdd_avg = gc['knee_AbdAdd_avg']
    hip_AbdAdd_avg = gc['hip_AbdAdd_avg']

    plot_avg_gcLR(knee_FlexExt_avg, 'Knee Flexion/Extension', plotSep=False)
    plot_avg_gcLR(hip_FlexExt_avg, 'Hip Flexion/Extension', plotSep=False)
    plot_avg_gcLR(knee_AbdAdd_avg, 'Knee Abduction/Adduction', plotSep=False)
    plot_avg_gcLR(hip_AbdAdd_avg, 'Hip Abduction/Adduction', plotSep=False)

    # Uncomment what is necessary for gait cycle display
    # plot_gcLR(gc['knee_FlexExt_gc'], 'Knee Flexion/Extension')
    # plot_gcLR(gc['hip_FlexExt_gc'], 'Hip Flexion/Extension')
    # plot_gcLR(gc['knee_AbdAdd_gc'], 'Knee Abduction/Adduction')
    # plot_gcLR(gc['hip_AbdAdd_gc'], 'Knee Flexion/Extension')


def plot_raw_all(kneeFlexExt, hipFlexExt, kneeAbdAdd, hipAbdAdd):
    plot_anglesLR(kneeFlexExt, 'Knee Flexion/Extension', 'Frame')
    plot_anglesLR(hipFlexExt, 'Hip Flexion/Extension', 'Frame')
    plot_anglesLR(kneeAbdAdd, 'Knee Abduction/Adduction', 'Frame')
    plot_anglesLR(hipAbdAdd, 'Hip Abduction/Adduction', 'Frame')


def plot_raw_all_file(anglesFile, i):
    with open(anglesFile, 'r') as f:
        jsonAngles = json.load(f)
    plot_raw_all(jsonAngles[i]['knee_FlexExt'], jsonAngles[i]['hip_FlexExt'], jsonAngles[i]['knee_AbdAdd'],
                 jsonAngles[i]['hip_AbdAdd'])


def main():
    i = '01'  # input('Enter participant code')
    path = '.\\Part\\Part' + str(i) + '\\'
    poseFile = path + 'Part' + str(i) + '_pose.json'
    anglesFile = path + 'Part' + str(i) + '_angles.json'
    # gcFile = path + 'Part' + str(i) + '_gc.json'
    # plot_avg_gcLR_all(gcFile)
    # plot_raw_all_file(anglesFile, 2)

    i = 1  # The gait number
    gif_pose(poseFile, i, path)
    gif_flexext(poseFile, anglesFile, i, path)
    gif_abdadd(poseFile, anglesFile, i, path)


# ==================================================================================
#                                   Main
# ==================================================================================
if __name__ == '__main__':
    main()
