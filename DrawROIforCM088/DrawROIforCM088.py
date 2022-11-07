#!/usr/bin/env python
# coding: utf-8

# In[6]:


###############################################
# In the project : CM088, we only focus on 
# region of interest (ROI). For example, in 
# the image size is 1280x720, ROI is including 
# six points (two area) : (220, 340), (1060, 
# 340), (1240, 700), (40, 700), (175, 175), 
# (1105, 175). In addition, we usually execude 
# auto label image first, and results often  
# not very good, so we have to check again.

# Therefore, to save time, We execute 
# DrawROIforCM088.py to remove bounding box 
# which out of ROI and draw ROI in the image.
#
# NOTE:
# 1. Before execute this file, we have to 
# modify 'ROOT' which is in GLOBAL VARIABLE.
# 2. images are in the ROOT/, and labels are in 
# the ROOT/labels/
#
# File:   DrawROIforCM088
# Author: DanielWu
# Date  : 20221101
#
###############################################

###############################################
#           H E A D E R   F I L E S
###############################################
import cv2
import os
import numpy as np
import math
from tqdm.notebook import tqdm

###############################################
#          F U N C T I O N   L I S T
###############################################
def GetPaths(folder, extension='.jpg'):
    paths = []

    for response in os.walk(folder):        # response = (dirpath, dirname, filenames)
        if response[2] != []:               # look for filenames
            for f in response[2]:
                if f.endswith(extension):  # only append .jpg file in paths 
                    paths.append(os.path.join(response[0], f))
    
    return paths

def DrawLines(image, points):
    overlay = image.copy()
    
    # this part is smaller area
    point_color = (200, 40, 8) # (B, G, R)
    thickness = 3
    alpha = 0.35
    
    cv2.line(overlay, points[0], points[1], point_color, thickness)
    cv2.line(overlay, points[1], points[2], point_color, thickness)
    cv2.line(overlay, points[2], points[3], point_color, thickness)
    cv2.line(overlay, points[3], points[0], point_color, thickness)
    
    # this part is larger area
    point_color = (255, 0, 255)
    thickness = 3
    alpha = 0.5
    
    cv2.line(overlay, points[4], points[5], point_color, thickness)
    cv2.line(overlay, points[5], points[2], point_color, thickness)
    cv2.line(overlay, points[3], points[4], point_color, thickness)
    
    # mix original image and drawing image
    overlay = cv2.addWeighted(overlay, alpha, image, 1-alpha, 0)
    
    return overlay

def ROIFunc(k, x, y, paras):
    if k == 'k1':
        return y + paras['m1']*x + paras['b1']
    if k == 'k2':
        return y + paras['m2']*x + paras['b2']
    if k == 'k3':
        return y + paras['b3']
    if k == 'k4':
        return y + paras['b4']

def ROI(line, points):
    # label from txt file
    line = line.split('\n')[0]
    data = line.split(' ')
    
    # yolov5 formate to left, top, right, bottom, width, height
    bbox_width = float(data[3]) * w
    bbox_height = float(data[4]) * h
    center_x = float(data[1]) * w
    center_y = float(data[2]) * h
    left = math.floor(center_x - (bbox_width / 2))
    top = math.floor(center_y - (bbox_height / 2))
    right = math.floor(center_x + (bbox_width / 2))
    bottom = math.floor(center_y + (bbox_height / 2))
        
    # roi
    paras = {
        'm1': round(((points[3][1]-points[4][1])/(points[4][0]-points[3][0])), 1),
        'm2': round(((points[2][1]-points[5][1])/(points[5][0]-points[2][0])), 1),
        'b1': 0,
        'b2': 0,
        'b3': -(points[4][1]),
        'b4': -(points[3][1])
    }
    
    paras['b1'] = -(points[3][1] + paras['m1']*points[3][0])
    paras['b2'] = -(points[2][1] + paras['m2']*points[2][0])

#     k1 = y + m1*x + b1 >= 0
#     k2 = y + m2*x + b2 >= 0
#     k3 = y + b3 >= 0
#     k4 = y + b4 <= 0

    # bbox in the left of image, use (right, bottom) to calculate roi
    if center_x < w/2:
        # check using center point
        k1 = ROIFunc('k1', center_x, center_y, paras)
        k3 = ROIFunc('k3', _, center_y, paras)
        k4 = ROIFunc('k4', _, center_y, paras)
        if k1 >= 0 and k3 >= 0 and k4 <= 0:
            return True
        
        # check using point:(right, bottom)
        k1 = ROIFunc('k1', right, bottom, paras)
        k3 = ROIFunc('k3', _, bottom, paras)
        k4 = ROIFunc('k4', _, bottom, paras)
        if k1 >= 0 and k3 >= 0 and k4 <= 0:
            return True
    # bbox in the right of image, use (left, bottom) to calculate roi
    else:
        # check using center point
        k2 = ROIFunc('k2', center_x, center_y, paras)
        k3 = ROIFunc('k3', _, center_y, paras)
        k4 = ROIFunc('k4', _, center_y, paras)
        if k2 >= 0 and k3 >= 0 and k4 <= 0:
            return True
        
        # check using point:(left, bottom)
        k2 = ROIFunc('k2', left, bottom, paras)
        k3 = ROIFunc('k3', _, bottom, paras)
        k4 = ROIFunc('k4', _, bottom, paras)
        if k2 >= 0 and k3 >= 0 and k4 <= 0:
            return True
    
    return False

###############################################
#              C O N S T A N T S
###############################################
# ROI for image size is 1280x720
points = [(220,  340),
          (1060, 340),
          (1240, 700),
          (40,   700),
          (175,  175),
          (1105, 175)]

###############################################
#        G L O B A L   V A R I A B L E
###############################################
ROOT = 'C:\\code\\c_yolov5\\yolov5-6.1\\runs\\detect\\221026_test001'

###############################################
#                   M A I N
###############################################
if __name__ == '__main__':
    # Get all images in the ROOT folder
    imgs_path = GetPaths(ROOT, '.jpg')
    
    for img_path in tqdm(imgs_path):
        # read input image size
        img = cv2.imread(img_path)
        h, w, _ = img.shape
        
        # scaling ROI: 1280 x 720 to w x h
        vetor = [(w/1280, h/720)] # scaling factor (1280 and 720 is according to CONSTANTS ROI image size)

        new_points = np.multiply(points, vetor)
        new_points = [(math.ceil(new_points[0][0]) , math.ceil(new_points[0][1])),
                      (math.floor(new_points[1][0]) , math.ceil(new_points[1][1])),
                      (math.floor(new_points[2][0]) , math.floor(new_points[2][1])),
                      (math.ceil(new_points[3][0]) , math.floor(new_points[3][1])),
                      (math.ceil(new_points[4][0]) , math.ceil(new_points[4][1])),
                      (math.floor(new_points[5][0]) , math.ceil(new_points[5][1]))]
        
        # drawing ROI in the original image
        overlay = DrawLines(img, new_points)
        
        # save image
        cv2.imwrite(img_path, overlay)
        
        # image path to label path : ~/xxxxxx.jpg -> ~/label/xxxxxx.txt
        dirname = os.path.dirname(img_path)
        basename = os.path.splitext(os.path.basename(img_path))[0] + '.txt'
        label_path = os.path.join(dirname, 'labels', basename)
        
        # read input image's label file if it exist
        if not os.path.isfile(label_path):
            continue
        
        with open(label_path, 'r') as f:
            lines = [line.rstrip() for line in f]
        
        # store index which out of ROI bbox
        del_idx = []
        for i, line in enumerate(lines):
            flag = ROI(line, new_points)
            if not flag:
                del_idx.append(i)
        
        # if del_idx is null, skip remove bbox
        if not del_idx:
            continue
        
        # remove out of ROI bbox and write in the original label file
        del_idx.reverse()
        for i in del_idx:
            lines.pop(i)

        with open(label_path, 'w') as f:
            for line in lines:
                f.write(line + '\n')