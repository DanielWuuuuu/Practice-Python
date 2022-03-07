#!/usr/bin/env python
# coding: utf-8

# In[ ]:


'''
REFERENCE

[1] A. Kathuria. "How to Train YOLO v5 on a Custom Dataset." 2021.
    [Online]. Available: https://blog.paperspace.com/train-yolov5-custom-data/
    [Accessed March 2, 2022]

[2] mjahanifar, S. Gupta. "goodhamgupta/yolo_to_voc.py" 2021.
    [Online]. Available: https://gist.github.com/goodhamgupta/7ca514458d24af980669b8b1c8bcdafd?permalink_comment_id=3247266#gistcomment-3247266
    [Accessed March 2, 2022]

'''


# In[ ]:


'''
dataset           # clone_dir  
├ 0               ## clone_images_folder  
│ ├ img           ### clone_images_folder, clone_images_folder_dir  
│ │ ├ 0000.jpg    #### clone_images_absolute_paths[0]  
│ │ ├ ..  
│ │ └ 1999.jpg  
│ └ vocAnots      ### clone_annotations_folder, clone_annotations_folder_dir  
│   ├ 0000.xml    #### clone_labels_absolute_paths[0]  
│   ├ ..  
│   └ 1999.xml  
├ 1               ## clone_images_folder  
├ ..              ## clone_images_folder    
└ 18
'''


# In[ ]:


'''
new_dataset      # save_dataset_dir  
├ images          ## save_images_folder  
│ ├ train         ### data_split['train']  
│ │ ├ 0000.jpg  
│ │ └ ..  
│ ├ val           ### data_split['val']  
│ │ ├ 0001.jpg  
│ │ └ ..  
│ └ test          ### data_split['test']  
│   ├ 0003.jpg  
│   └ ..  
└ labels          ## save_annotations_folder  
  ├ train  
  ├ val 
  └ test
'''


# In[ ]:


import os
import glob # 使用glob模組中的glob函式來進行篩選。glob函式會回傳目前工作目錄中與條件符合的檔案
import shutil # 搬移、複製、修改檔名或刪除檔案
import random
from tqdm.notebook import tqdm # jupyter notebook的進度條
from PIL import Image
from math import floor
import xml.etree.ElementTree as ET


# In[ ]:


# VARIABLE
## Directory
clone_dir = 'C:\\Users\\danielwu\\Desktop\\dataset'
save_dataset_dir = 'C:\\Users\\danielwu\\Desktop\\new_dataset'

## Clone folder name
clone_images_folder = 'img'
clone_annotations_folder = 'vocAnots'

## Clone file format
clone_images_format = '.jpg'
clone_annotations_format = '.xml'

## Save folder name
save_images_folder = 'images'
save_annotations_folder = 'labels'

## Split ratio
data_split = {'train': 0.6,
              'val':   0.2,
              'test':  0.2}

## Convert format or not
isConvert_format = True

## Dictionary that maps IDs to class names
class_mapping = {'0': 'person'}


# In[ ]:


# Check if save folders exist, if not make the folders
def check_save_folders_isExist():
    # make save directory
    if not os.path.isdir(save_dataset_dir):
        os.makedirs(save_dataset_dir)

    for sub_dir in [save_images_folder, save_annotations_folder]:
        # make save images folder and save annotations folder
        if not os.path.isdir(os.path.join(save_dataset_dir, sub_dir)):
            os.makedirs(os.path.join(save_dataset_dir, sub_dir))

        # make train folder, val folder and test folder
        for split_folder in data_split.keys():
            if not os.path.isdir(os.path.join(save_dataset_dir, sub_dir, split_folder)):
                os.makedirs(os.path.join(save_dataset_dir, sub_dir, split_folder))


# In[ ]:


# Check A and B whether matching
def symmetric_difference(A_paths, B_paths):
    A_basename_splitexts = [os.path.basename(basename).split('.')[0] for basename in A_paths]
    B_basename_splitexts = [os.path.basename(basename).split('.')[0] for basename in B_paths]
    
    # a ^ b: symmetric difference; a ^ b = a.symmetric_difference(b)
    symdifference = set(A_basename_splitexts) ^ set(B_basename_splitexts)
    
    # not match
    remove_paths = []
    if symdifference != set():
        # remove not-match paths
        A_remove_idx = []
        B_remove_idx = []
        
        for rm in symdifference:
            if rm in A_basename_splitexts:
                A_remove_idx.append(A_basename_splitexts.index(rm))
            if rm in B_basename_splitexts:
                B_remove_idx.append(B_basename_splitexts.index(rm))
        
        for idx in sorted(A_remove_idx, reverse=True):
            remove_paths.append(A_paths[idx])
            del A_paths[idx]
        
        for idx in sorted(B_remove_idx, reverse=True):
            remove_paths.append(B_paths[idx])
            del B_paths[idx]
        
        print('There is not match!')
        for rm in remove_paths:
            print('remove: ', rm)


# In[ ]:


# Clone images paths and labels paths
def clone_paths():
    clone_images_absolute_paths = [] # absolute paths of images to be cloned
    clone_labels_absolute_paths = [] # absolute paths of images to be cloned

    for subdata_dirs in os.listdir(clone_dir):
        clone_images_folder_dir = os.path.join(clone_dir, subdata_dirs, clone_images_folder)
        clone_annotations_folder_dir = os.path.join(clone_dir, subdata_dirs, clone_annotations_folder)

        # save images paths: absolute paths and name without file extension
        for basename in os.listdir(clone_images_folder_dir):
            # only save file extension of images equaling clone_images_format
            if basename.split('.')[1] == clone_images_format.split('.')[1]:
                clone_images_absolute_paths.append(os.path.join(clone_images_folder_dir, basename))

        # save labels paths: relative paths and name without file extension
        for basename in os.listdir(clone_annotations_folder_dir):
            # only save file extension of annotations equaling clone_annotations_format
            if basename.split('.')[1] == clone_annotations_format.split('.')[1]:
                clone_labels_absolute_paths.append(os.path.join(clone_annotations_folder_dir, basename))

    print('There are {} images'.format(len(clone_images_absolute_paths)))
    print('There are {} labels'.format(len(clone_labels_absolute_paths)))

    # check images and labels whether matching
    symmetric_difference(clone_images_absolute_paths, clone_labels_absolute_paths)
    
    return clone_images_absolute_paths, clone_labels_absolute_paths


# In[ ]:


# Function to get the data from XML Annotation (for .xml to .txt: part 1)
def extract_info_from_xml(xml_file):
    root = ET.parse(xml_file).getroot()
    
    # Initialise the info dict 
    info_dict = {}
    info_dict['bboxes'] = []
    
    # Get the file name 
    info_dict['filename'] = os.path.basename(xml_file)

    # Parse the XML Tree
    for elem in root:      
        # Get the image size
        if elem.tag == "size":
            image_size = []
            for subelem in elem:
                image_size.append(int(subelem.text))
            
            info_dict['image_size'] = tuple(image_size)
        
        # Get details of the bounding box 
        elif elem.tag == "object":
            bbox = {}
            for subelem in elem:
                if subelem.tag == "name":
                    bbox["class"] = subelem.text
                    
                elif subelem.tag == "bndbox":
                    for subsubelem in subelem:
                        bbox[subsubelem.tag] = int(subsubelem.text)            
            info_dict['bboxes'].append(bbox)
    
    return info_dict


# In[ ]:


# Convert the info dict to the required yolo format and write it to disk (for .xml to .txt: part 2)
def voc_to_yolo(info_dict, file_path):
    print_buffer = []
    reverse_class_mapping = {}
    
    for item in class_mapping.items():
        reverse_class_mapping[item[1]] = int(item[0])
    
    # For each bounding box
    for b in info_dict["bboxes"]:
        try:
            class_id = reverse_class_mapping[b["class"]]
        except KeyError:
            print("Invalid Class. Must be one from ", reverse_class_mapping.keys())
        
        # Transform the bbox co-ordinates as per the format required by YOLO v5
        b_center_x = (b["xmin"] + b["xmax"]) / 2 
        b_center_y = (b["ymin"] + b["ymax"]) / 2
        b_width    = (b["xmax"] - b["xmin"])
        b_height   = (b["ymax"] - b["ymin"])
        
        # Normalise the co-ordinates by the dimensions of the image
        image_w, image_h, image_c = info_dict["image_size"]  
        b_center_x /= image_w 
        b_center_y /= image_h 
        b_width    /= image_w 
        b_height   /= image_h 
        
        #Write the bbox details to the file 
        print_buffer.append("{} {:.3f} {:.3f} {:.3f} {:.3f}".format(class_id, b_center_x, b_center_y, b_width, b_height))
            
    # Save the annotation to disk
    print("\n".join(print_buffer), file= open(file_path, "w"))


# In[ ]:


# Start voc to yolo (for .xml to .txt: final)
def start_voc_to_yolo(path):
    # Read .xml information
    info_dict = extract_info_from_xml(path)

    # Convert read path to save path
    basename = os.path.basename(path).replace('.xml', '.txt')
    path = os.path.join(save_dataset_dir, save_annotations_folder, key, basename)

    # Save annotation
    voc_to_yolo(info_dict, path)


# In[ ]:


# Create .xml root: base info (for .txt to .xml: part 1)
def create_root(image_path, width, height, imgChnls = 3):
    root = ET.Element("annotations")
    ET.SubElement(root, "filename").text = os.path.basename(image_path)
    ET.SubElement(root, "folder").text = image_path
    ET.SubElement(root, 'segmented').text = str(0)
    size = ET.SubElement(root, "size")
    ET.SubElement(size, "width").text = str(width)
    ET.SubElement(size, "height").text = str(height)
    ET.SubElement(size, "depth").text = str(imgChnls)
    return root


# In[ ]:


# Create .xml root: object annotation (for .txt to .xml: part 2)
def create_object_annotation(root, voc_labels):
    for voc_label in voc_labels:
        obj = ET.SubElement(root, "object")
        ET.SubElement(obj, "name").text = voc_label[0]
        ET.SubElement(obj, "pose").text = "Unspecified"
        ET.SubElement(obj, "truncated").text = str(0)
        ET.SubElement(obj, "difficult").text = str(0)
        bbox = ET.SubElement(obj, "bndbox")
        ET.SubElement(bbox, "xmin").text = str(voc_label[1])
        ET.SubElement(bbox, "ymin").text = str(voc_label[2])
        ET.SubElement(bbox, "xmax").text = str(voc_label[3])
        ET.SubElement(bbox, "ymax").text = str(voc_label[4])
    return root


# In[ ]:


# Pretty .xml root: indent and newline (for .txt to .xml: part 3)
def pretty_xml(element,indent='\t', newline='\n', level = 0): # elemnt為傳進來的Elment類，引數indent用於縮排，newline用於換行
    # 判斷element是否有子元素
    if element:
        # 如果element的text沒有內容
        if element.text == None or element.text.isspace():
            element.text = newline + indent * (level + 1)
        
        # 如果element的text有內容
        else:
            element.text = newline + indent * (level + 1) + element.text.strip() + newline + indent * (level + 1)
    
    # 此處兩行如果把註釋去掉，Element的text也會另起一行
#     else:
#         element.text = newline + indent * (level + 1) + element.text.strip() + newline + indent * level

    temp = list(element)
    for subelement in temp:
        # 如果不是list的最後一個元素，說明下一個行是同級別元素的起始，縮排應一致
        if temp.index(subelement) < (len(temp) - 1):
            subelement.tail = newline + indent * (level + 1)
            
        # 如果是list的最後一個元素， 說明下一行是母元素的結束，縮排應該少一個
        else:
            subelement.tail = newline + indent * level
        
        # 對子元素進行遞迴操作
        pretty_xml(subelement, level = level + 1)


# In[ ]:


# Create .xml file (for .txt to .xml: part 4) 
def create_file(image_path, file_prefix, width, height, voc_labels):
    root = create_root(image_path, file_prefix, width, height)
    root = create_object_annotation(root, voc_labels)
    pretty_xml(root)
    tree = ET.ElementTree(root)
    tree.write(os.path.join(save_dataset_dir, save_annotations_folder, key, '{}.xml'.format(file_prefix)))


# In[ ]:


# Create .xml file: caculate bndbox (for .txt to .xml: part 5)
def start_yolo_to_voc(label_path):
    basename = os.path.basename(label_path)
    file_prefix = basename.split('.')[0]
    image_path = label_path.replace(clone_annotations_folder, clone_images_folder)
    image_path = image_path.replace(clone_annotations_format, clone_images_format)
    img = Image.open(image_path)
#     print(img)

    w, h = img.size
#     print(label_path)
    with open(label_path) as file:
        lines = file.readlines()
        voc_labels = []
        for line in lines:
            voc = []
            line = line.strip()
            data = line.split()
            voc.append(class_mapping.get(data[0]))
            bbox_width = float(data[3]) * w
            bbox_height = float(data[4]) * h
            center_x = float(data[1]) * w
            center_y = float(data[2]) * h
            voc.append(floor(center_x - (bbox_width / 2)))
            voc.append(floor(center_y - (bbox_height / 2)))
            voc.append(floor(center_x + (bbox_width / 2)))
            voc.append(floor(center_y + (bbox_height / 2)))
            voc_labels.append(voc)
        create_file(image_path, file_prefix, w, h, voc_labels)

#     print('Processing complete for file: {}'.format(basename))


# In[ ]:


# Save files
def save_files(files_paths, save_dataset_dir, save_files_folder, files):
    # save train dataset, val dataset and test dataset
    for key in list(files_paths.keys()):
        # set images tqdm progress
        images_progress = tqdm(total = len(files_paths[key]), desc='clone {} {}'.format(key, files))
        
        for file_path in files_paths[key]:
            # clone and save files (clone path, save path)
            shutil.copy(file_path, os.path.join(save_dataset_dir, save_files_folder, key))
            
            # update progress
            images_progress.update(1)


# In[ ]:


# Read absolute paths of images and annotations
clone_images_paths, clone_annotations_paths = clone_paths()

# Random paths
random.seed(random.random())
random.shuffle(clone_images_paths)

total_image_number = len(clone_images_paths)
number_train = round(total_image_number*data_split['train'])
number_test = round(total_image_number*data_split['test'])

# Images paths to tmp annotations paths
tmp_annotations_paths = [tmp_path.replace(clone_images_folder, clone_annotations_folder).replace(clone_images_format, clone_annotations_format) for tmp_path in clone_images_paths]

# Split images paths
save_images_paths = {'train': clone_images_paths[:number_train],
                     'val':   clone_images_paths[number_train:-number_test],
                     'test':  clone_images_paths[-number_test:]}

# Split annotations paths
save_annotations_paths = {'train': tmp_annotations_paths[:number_train],
                          'val':   tmp_annotations_paths[number_train:-number_test],
                          'test':  tmp_annotations_paths[-number_test:]}

# Check folders isExist
check_save_folders_isExist()

# Save images
save_files(save_images_paths, save_dataset_dir, save_images_folder, files='images')

# Save annotations (not need to convert)
if isConvert_format == False:
    save_files(save_annotations_paths, save_dataset_dir, save_annotations_folder, files='labels')

# Save annotations (need to convert)
if isConvert_format == True:
    # Convert VOC format to YOLO format and save the annotations
    if clone_annotations_format == '.xml':
        print('Convert VOC format(.xml) to YOLO format(.txt)')
        for key in save_annotations_paths.keys():
            for path in tqdm(save_annotations_paths[key], desc='clone {} annotations'.format(key)):
                start_voc_to_yolo(path)
        
    # Convert YOLO format to VOC format and save the annotations
    if clone_annotations_format == '.txt':
        print('Convert YOLO format(.txt) to VOC format(.xml)')
        for key in save_annotations_paths.keys():
            for path in tqdm(save_annotations_paths[key], desc='clone {} annotations'.format(key)):
                start_yolo_to_voc(path)


