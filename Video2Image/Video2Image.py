#!/usr/bin/env python
# coding: utf-8

# In[1]:


###############################################
#           H E A D E R   F I L E S
###############################################
import os
import shutil
import numpy as np
from tqdm.notebook import tqdm


# In[2]:


###############################################
#          F U N C T I O N   L I S T
###############################################
## @brief Description: 取得CMD大小
#  @param None
#  
#  @return col
#  @date 20220318  danielwu
def GetCmdSize():
    col, _ = shutil.get_terminal_size()
    col = col - 21
    return col

## @brief Description: 建立資料夾
#  @param folder
#  
#  @return None
#  @date 20220321  danielwu
def MakeDirs(folder):
    if not os.path.isdir(folder):
        os.makedirs(folder)

## @brief Description: 取得母資料夾內所有特定格式檔案路徑
#  @param [in] folder     母資料夾路徑
#  @param [in] extension  副檔名
#  
#  @return paths
#  @date 20220321  danielwu
def GetPaths(folder, extension='.MOV'):
    paths = []

    for response in os.walk(folder):        # response = (dirpath, dirname, filenames)
        if response[2] != []:               # look for filenames
            for f in response[2]:
                if f.endswith(extension):  # only append .MOV file in paths 
                    paths.append(os.path.join(response[0], f))
    
    return paths

## @brief Description: 比較兩影像之差異
#
#  @param [in] imageA  影像 A
#  @param [in] imageB  影像 B
#
#  @return change 影像 A與影像 B之差異性
#  @date  20230316  danielwu 
def DiffImages(imageA, imageB):
    # convert the images to grayscale
    grayA = cv2.cvtColor(imageA, cv2.COLOR_BGR2GRAY)
    grayB = cv2.cvtColor(imageB, cv2.COLOR_BGR2GRAY)

    # blur the imagess
    kernelB = (5, 5)
    blurA = cv2.GaussianBlur(grayA, kernelB, 0)
    blurB = cv2.GaussianBlur(grayB, kernelB, 0)

    # erode the images
    kernelE = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
    erodeA = cv2.erode(blurA, kernelE)
    erodeB = cv2.erode(blurB, kernelE)

    # compare the two images using cv2.absdiff
    diffErode = cv2.absdiff(erodeA, erodeB)
    changeErode = np.average(diffErode)
    
    return changeErode

## @brief Description: 調整影像尺寸(補上黑邊)
#
#  @param [in] image     輸入影像
#  @param [in] new_size  欲調整尺寸
#
#  @return resized_image 調整後之影像
#  @date  20230516  danielwu 
def ResizeImagewithBorder(image, new_size):
    # get the input image size
    h, w = image.shape[:2]

    # get the scaled size
    if w > h:
        new_w = new_size
        new_h = int(h * new_size / w)
    else:
        new_h = new_size
        new_w = int(w * new_size / h)

    # scale the input image
    resized_image = cv2.resize(image, (new_w, new_h), interpolation=interpolation)

    # fill the black border
    if is_Border:
        border_w = (new_size - new_w) // 2
        border_h = (new_size - new_h) // 2
        border_type = cv2.BORDER_CONSTANT
        border_color = (0, 0, 0)
        resized_image = cv2.copyMakeBorder(resized_image, border_h, border_h, border_w, border_w, border_type, value=border_color)

    return resized_image

## @brief Description: 影片轉成影像
#
#  @param [in] video_path  影片路徑
#  @param [in] save_dir    儲存影像之路徑
#  @param [in] interval    幀數間格
#
#  @return None
#  @date  20230316  danielwu 
def CutVideo(video_path, save_dir, interval=1):
    frame_count = 0  # 保存幀的索引
    frame_index = 0  # 原影片的幀樹索引 ( interval * frame_count = frame_index )
    
    cap = cv2.VideoCapture(video_path)

    if cap.isOpened():
        ret = True
    else:
        ret = False
        print('{} 讀取失敗!\n'.format(video_path))

    while(ret):
        ret, frame = cap.read()
        if ret == False:
            continue
        if frame_index % interval == 0:
            if is_Resize:
                if is_KeepRatio:
                    if is_Border:
                        image_name = f'resize_{single_resize}p_border_{frame_count:06d}.jpg'
                    else:
                        image_name = f'resize_{single_resize}_{frame_count:06d}.jpg'
                else:
                    image_name = f'resize_{resize_shape[1]}p_{frame_count:06d}.jpg'
            else:
                image_name = f'{frame_count:06d}.jpg'
            
            if frame_count == 0:
                pre_frame = frame
                
                if is_Resize:
                    if is_KeepRatio:
                        frame = ResizeImagewithBorder(frame, single_resize)
                    else:
                        frame = cv2.resize(frame, resize_shape, interpolation=interpolation)
                
                cv2.imwrite(os.path.join(save_dir, image_name), frame)
                frame_count += 1
            else:
                # compare pre-frame and current frame 
                # if difference value over than thresth,
                # save current frame
                change = DiffImages(pre_frame, frame)
                pre_frame = frame
                
                if change < 1.5:
                    continue
                
                if is_Resize:
                    if is_KeepRatio:
                        frame = ResizeImagewithBorder(frame, single_resize)
                    else:
                        frame = cv2.resize(frame, resize_shape, interpolation=interpolation)
                
                cv2.imwrite(os.path.join(save_dir, image_name), frame)
                frame_count += 1
        frame_index += 1
    cap.release()

## @brief Description: 影片轉成影像(影片有4個子畫面,各別儲存影像)
#
#  @param [in] video_path  影片路徑
#  @param [in] save_dir    儲存影像之路徑
#  @param [in] interval    幀數間格
#
#  @return None
#  @date  20230316  danielwu 
def FourinOneCutVideo(video_path, save_dir, interval=1):
    frame_count = 0
    frame_index = 0
    
    cap = cv2.VideoCapture(video_path)
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    dw = w//2
    dh = h//2
    
    cuts = ['left_top', 'right_top', 'left_bottom', 'right_bottom', 'all_in_one']
    coordinates = {cuts[0] : [0, 0, dw, dh],
                   cuts[1] : [dw, 0, dw, dh],
                   cuts[2] : [0, dh, dw, dh],
                   cuts[3] : [dw, dh, dw, dh],
                   cuts[4] : [0, 0, w, h],}
        
    if cap.isOpened():
        ret = True
    else:
        ret = False
        print('{} 讀取失敗!\n'.format(video_path))
        return
    
    for cut in cuts:
        MakeDirs(os.path.join(save_dir, cut))
        
    pre_subframe = []
    
    while(ret):
        ret, frame = cap.read()
        if ret == False:
            continue
        
        if frame_index % interval == 0:
            if is_Resize:
                if is_KeepRatio:
                    if is_Border:
                        image_name = f'resize_{single_resize}p_border_{frame_count:06d}.jpg'
                    else:
                        image_name = f'resize_{single_resize}_{frame_count:06d}.jpg'
                else:
                    image_name = f'resize_{resize_shape[1]}p_{frame_count:06d}.jpg'
            else:
                image_name = f'{frame_count:06d}.jpg'
            
            for i, cut in enumerate(cuts):
                x, y, w, h = coordinates[cut]
                subframe = frame[y : y+h, x : x+w]
                
                # 'left_top', 'right_top', 'left_bottom', 'right_bottom'
                if i != 4:
                    if frame_count == 0:
                        pre_subframe.append(subframe)
                        
                        if is_Resize:
                            if is_KeepRatio:
                                subframe = ResizeImagewithBorder(subframe, single_resize)
                            else:
                                subframe = cv2.resize(subframe, resize_shape, interpolation=interpolation)
                        
                        cv2.imwrite(os.path.join(save_dir, cut, image_name), subframe)
                        
                    else:
                        # compare pre-frame and current frame 
                        # if difference value over than thresth,
                        # save current frame
                        change = DiffImages(pre_subframe[i], subframe)
                        pre_subframe[i] = subframe
                        
                        if change < 1.5:
                            continue
                        
                        if is_Resize:
                            if is_KeepRatio:
                                subframe = ResizeImagewithBorder(subframe, single_resize)
                            else:
                                subframe = cv2.resize(subframe, resize_shape, interpolation=interpolation)
                        
                        cv2.imwrite(os.path.join(save_dir, cut, image_name), subframe)
                
                # 'all_in_one'
                elif i == 4:
                    if is_Resize:
                        if is_KeepRatio:
                            subframe = ResizeImagewithBorder(subframe, single_resize)
                        else:
                            subframe = cv2.resize(subframe, resize_shape, interpolation=interpolation)
                    
                    cv2.imwrite(os.path.join(save_dir, cut, image_name), subframe)
                    frame_count += 1
        frame_index += 1
    cap.release()

def StartVideo2Image(ROOT, videos_folder, cut_method, file_exe='.MOV'):
    # Get Video Paths from ROOT (Video is .MOV file)
    videos_folder_path = os.path.join(ROOT, videos_folder)
    video_paths = GetPaths(videos_folder_path, extension=file_exe)
    
    if video_paths == []:
        print('There is not any {} file in the {}'.format(file_exe, videos_folder_path))
        print('Please put the video you want to cut into this folder!')
        return

    if isLog:
        print('== Info ' + '='*(col-8))
        print('There are {} videos in dir: {}'.format(len(video_paths), videos_folder_path))
        print('='*col)

    all_image_paths = []
    for video_path in tqdm(video_paths):
        basename = os.path.basename(video_path)        # videoXX.MOV
        name = os.path.splitext(basename)[0]           # videoXX
        save_path = video_path.replace(videos_folder, '{}_video2image'.format(videos_folder), 1)
        save_path = save_path.replace(basename, name)  # ~\videos_folder_video2image\~\videoXX
        save_images_path = os.path.join(save_path, 'images')
        MakeDirs(save_images_path)         # ~\videos_folder_video2image\~\videoXX\images

        # Cut video, save images and move the original video to the created image folder
        if cut_method == 'normal':
            CutVideo(video_path, save_images_path, interval)
        elif cut_method == 'four_in_one':
            FourinOneCutVideo(video_path, save_images_path, interval)
        else:
            print('Cutting method is wrong! Please select "normal" or "four_in_one"!\n')
            return
        
        if not is_Sound:
            # is_Sound == False: output video without sound
            video_save_path = os.path.join(save_path, basename)
            with VideoFileClip(video_path) as video:
                video = video.without_audio()
                video.write_videofile(video_save_path, codec="libx264", logger=None)
            try:
                os.remove(video_path)
            except:
                print(f'Can not remove {video_path}')
        else:
            shutil.move(video_path, save_path)
        
        # Create the .txt file and write image paths into the file
        txt_file = '{}_image_paths.txt'.format(name)
        txt_path = os.path.join(save_path, txt_file)
        image_paths = GetPaths(save_images_path, extension='.jpg')
        all_image_paths.extend(image_paths)
        with open(txt_path, 'w') as f:
            for image_path in image_paths:
                if image_path != image_paths[-1]:
                    f.write('{}\n'.format(image_path))
                else:
                    f.write(image_path)

    # Remove original video folder (it's an empty folders)
    shutil.rmtree(videos_folder_path)

    # Create the .txt file and write all image paths into the file
    txt_file = '{}_video2image_image_paths.txt'.format(videos_folder)
    txt_path = os.path.join(ROOT, txt_file)
    with open(txt_path, 'w') as f:
        for image_path in all_image_paths:
            if image_path != all_image_paths[-1]:
                f.write('{}\n'.format(image_path))
            else:
                f.write(image_path)
    
    if isLog:
        print('Remove {} folder'.format(os.path.basename(videos_folder_path)))
        print('='*col)
        print('case: Video2Image done!')

def StartImageAllInOne(ROOT, videos_folder):
    info_txt_path = os.path.join(ROOT, '{}_video2image_image_paths.txt'.format(videos_folder))
    all_image_paths = []
    
    if os.path.isfile(info_txt_path):
        # Get all image paths from the video2image_image_paths.txt file
        with open(info_txt_path, 'r') as f:
            line = f.readline()
            while line:
                line = line.split('\n')[0]
                all_image_paths.append(line)
                line = f.readline()
        if all_image_paths != []:
            if isLog:
                print('Get image paths from the {}'.format(info_txt_path))
    if not os.path.isfile(info_txt_path) or all_image_paths == []:
        # Get all image paths from the video2image folder using func. GetPaths():
        video2image_path = os.path.join(ROOT, '{}_video2image'.format(videos_folder))
        all_image_paths = GetPaths(video2image_path, extension='.jpg')
        if all_image_paths != []:
            if isLog:
                print('Get image paths from video2image folder using func. GetPaths()')
        else:
            print('There is empty in the {}'.format(info_txt_path))
            print('There is not any .jpg file in the {}'.format(video2image_path))
            print('Please do the case: "Video2Image" first!')
            return

    save_path = os.path.join(ROOT, '{}_all_images'.format(videos_folder))
    MakeDirs(save_path)
    
    # Remove 'all_in_one' images
    all_image_paths = [path for path in all_image_paths if 'all_in_one' not in path]
    
    # Copy images from video2image folder to all_images folder
    for count, image_path in enumerate(tqdm(all_image_paths)):
        basename = os.path.basename(image_path)
        save_image_path = os.path.join(save_path, '{}.jpg'.format(str(count).zfill(6)))
        shutil.copy(image_path, save_image_path)

    # Create the .txt file and write (new image name: image original path)
    txt_file = '{}_allinone_image_paths.txt'.format(videos_folder)
    txt_path = os.path.join(ROOT, txt_file)
    with open(txt_path, 'w') as f:
        flag = ''
        f.write('## # <video2image Relative Path>\n')
        f.write('## image basename of all_images: image relative paht of video2image')
        for count, image_path in enumerate(all_image_paths):
            relative_path = image_path.split(ROOT)[1]
            dirname = os.path.dirname(relative_path)
            if dirname != flag:
                f.write('\n\n# {}'.format(dirname))
                flag = dirname
            f.write('\n{}.jpg : {}'.format(str(count).zfill(6), relative_path))
            count += 1
    
    if isLog:
        print('case: ImageAllInOne done!')

# Create .xml root: base info (for .txt to .xml: part 1)
def CreateRoot(image_path, width, height, imgChnls=3):
    root = ET.Element("annotations")
    ET.SubElement(root, "filename").text = os.path.basename(image_path)
    ET.SubElement(root, "folder").text = os.path.dirname(image_path)
    ET.SubElement(root, 'segmented').text = str(0)
    size = ET.SubElement(root, "size")
    ET.SubElement(size, "width").text = str(width)
    ET.SubElement(size, "height").text = str(height)
    ET.SubElement(size, "depth").text = str(imgChnls)
    return root

# Create .xml root: object annotation (for .txt to .xml: part 2)
def CreateObjectAnnotation(root, voc_labels):
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

# Pretty .xml root: indent and newline (for .txt to .xml: part 3)
def PrettyXml(element,indent='\t', newline='\n', level = 0): # elemnt為傳進來的Elment類，引數indent用於縮排，newline用於換行
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
        PrettyXml(subelement, level = level + 1)

# Create .xml file (for .txt to .xml: part 4) 
def CreateFile(image_path, save_folder, file_prefix, width, height, voc_labels):
    root = CreateRoot(image_path, width, height)
    root = CreateObjectAnnotation(root, voc_labels)
    PrettyXml(root)
    save_path = os.path.join(save_folder, '{}.xml'.format(file_prefix))
    tree = ET.ElementTree(root)
    tree.write(save_path)

# Create .xml file: caculate bndbox (for .txt to .xml: part 5)
def Yolo2Voc(label_path, image_path, save_folder):
    basename = os.path.basename(label_path)  # xxxxxx.txt
    file_prefix = basename.split('.')[0]     # xxxxxx
    img = Image.open(image_path)
    w, h = img.size
    
    with open(label_path) as f:
        lines = f.readlines()
        voc_labels = []
        for line in lines:
            voc = []
            line = line.strip() # Remove space or newline
            data = line.split() # Split space or newline
            if not len(data):
                continue
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
        CreateFile(image_path, save_folder, file_prefix, w, h, voc_labels)

#     print('Processing complete for file: {}'.format(basename))

def StartYolo2Voc(ROOT, videos_folder):
    check_images_path = os.path.join(ROOT, '{}_check_images'.format(videos_folder))
    yolo_labels_path = os.path.join(ROOT, '{}_all_yolo_labels'.format(videos_folder))
    image_replace = False
    
    if os.path.isdir(yolo_labels_path):
        txt_paths = GetPaths(yolo_labels_path, extension='.txt')
        
        if not os.path.isdir(check_images_path):
            image_replace = True
            print('Yolo label folder is exist, but check image folder is not exist')
            print('Check image folder is replaced by all image folder')
            
        if txt_paths == []:
            print('There is not any .txt file in the {}'.format(yolo_labels_path))
            print('Skip case: Yolo2Voc')
            print('='*col)
            return
    else:
        print('Yolo label folder is not exist')
        print('Skip case: Yolo2Voc')
        print('='*col)
        return
    
    voc_labels_path = os.path.join(ROOT, '{}_all_voc_labels'.format(videos_folder))
    MakeDirs(voc_labels_path)

    for txt_path in tqdm(txt_paths):
        # txt_path = '~/video_folder_all_yolo_labels/xxxxxx.txt'
        # image_path = '~/video_folder_check_images/xxxxxx.jpg'
        
        if image_replace:
            image_path = txt_path.replace('all_yolo_labels', 'all_images')
        else:
            image_path = txt_path.replace('all_yolo_labels', 'check_images')
        image_path = image_path.replace('.txt', '.jpg')
        
        Yolo2Voc(txt_path, image_path, voc_labels_path)
    
    if isLog:
        print('case: Yolo2Voc done!')
        print('='*col)

def StartAllocateData(ROOT, videos_folder):
    check_images_path = os.path.join(ROOT, '{}_check_images'.format(videos_folder))
    help_check_path = os.path.join(ROOT, '{}_help_check_labels'.format(videos_folder))
    yolo_labels_path = os.path.join(ROOT, '{}_all_yolo_labels'.format(videos_folder))
    image_replace = False
    
    if not os.path.isdir(check_images_path):
        image_replace = True
        check_images_path = os.path.join(ROOT, '{}_all_images'.format(videos_folder))
        
    image_paths = GetPaths(check_images_path, extension='.jpg')
    
    for count, image_path in enumerate(tqdm(image_paths)):
        folder_idx = count // members                          # 一個資料夾members筆資料
        save_image = os.path.join(help_check_path, str(folder_idx), 'images')
        save_label = os.path.join(help_check_path, str(folder_idx), 'labels')
        for f in [save_image, save_label]:
            MakeDirs(f)
            
        if image_replace:
            label_path = image_path.replace('all_images', 'all_voc_labels')
        else:
            label_path = image_path.replace('check_images', 'all_voc_labels')
        label_path = label_path.replace('.jpg', '.xml')
        
        # copy Original Image To New Folder
        shutil.copy(image_path, save_image)
        # copy Original Label To New Folder
        if os.path.isfile(label_path):
            shutil.copy(label_path, save_label)
    
    if isLog:
        print('Create {} folder'.format(os.path.basename(help_check_path)))
        print('case: AllocateData done!')
        print('='*col)

def StartUpdateLabels(ROOT, videos_folder):
    help_check_path = os.path.join(ROOT, '{}_help_check_labels'.format(videos_folder))
    info_txt_path = os.path.join(ROOT, '{}_allinone_image_paths.txt'.format(videos_folder))
    
    # Read the allinone_image_paths.txt file,
    # and create a dictionary: relative_path, its key and value are:
    # image basename of all_images: image relative paht of video2image
    with open(info_txt_path, 'r') as f:
        relative_path = {}
        line = f.readline()
        while line:
            if '#' in line:             # ignore comments
                line = f.readline()
                continue
            line = line.split('\n')[0]  # remove '\n' in each line
            if line == '':              # ignore empty line
                line = f.readline()
                continue
            relative_path[line.split('.')[0]] = line.split(' : ')[1]
            line = f.readline()
    
    # Get .xml file paths from help_check_labels folder
    xml_paths = GetPaths(help_check_path, extension='.xml')
    
    for xml_path in tqdm(xml_paths):
        basename = os.path.basename(xml_path)      # xxxxxx.xml
        prefix_basename = basename.split('.')[0]   # xxxxxx
        
        # Using path of .xml file to get original image relative path
        # relative_path[xxxxxx] = '~/videoXX/images/yyyyyy.jpg'
        # split_relative_path = [~, videoXX, images]
        # save_basename = 'yyyyyy.xml'
        split_relative_path = os.path.dirname(relative_path[prefix_basename]).split('\\')
        save_basename = os.path.splitext(os.path.basename(relative_path[prefix_basename]))[0] + '.xml'
        
        # Update saving .xml file folder path and create the folder
        save_path = ROOT
        for path in split_relative_path:
            save_path = os.path.join(save_path, path)
        save_path = save_path.replace('images', 'voc_labels')
        MakeDirs(save_path)
        save_path = os.path.join(save_path, save_basename)
        
        # Cut .xml file from help_check_labels folder to video2image folder
        shutil.move(xml_path, save_path)


    # Remove help_check_labels folder (the folder is for staged mission)
    shutil.rmtree(help_check_path)
        
    if isLog:
        print('Remove {} folder'.format(os.path.basename(help_check_path)))
        print('case: UpdateLabels done!')
        print('='*col)

# Function to get the data from XML Annotation (for .xml to .txt: part 1)
def ExtractInfoFromXml(xml_file):
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

# Convert the info dict to the required yolo format and write it to disk (for .xml to .txt: part 2)
def Voc2Yolo(info_dict, txt1_path, txt2_path):
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
    print("\n".join(print_buffer), end='', file= open(txt1_path, "w"))
    print("\n".join(print_buffer), end='', file= open(txt2_path, "w"))

# Start voc to yolo (for .xml to .txt: final)
def StartVoc2Yolo(ROOT, videos_folder):
    video2image_path = os.path.join(ROOT, '{}_video2image'.format(videos_folder))
    
    # Get .xml file paths from video2image folder
    xml_paths = GetPaths(video2image_path, extension='.xml')
    
    for xml_path in tqdm(xml_paths):
        # Read .xml information
        info_dict = ExtractInfoFromXml(xml_path)
        
        # Convert xml path to save txt path
        # xml_path = '~\videoXX\voc_labels\xxxxxx.xml'
        # dir_xml_path = '~\videoXX\voc_labels'
        # save_basename = xxxxxx.txt
        # save_path_fimages = '~\videoXX\images\xxxxxx.txt'
        # save_path_flabels = '~\videoXX\labels\xxxxxx.txt'
        dir_xml_path = os.path.dirname(xml_path)
        save_basename = os.path.basename(xml_path).replace('.xml', '.txt')
        
        # Update saving .txt file folder path and create the folder
        save_path_fimages = os.path.join(dir_xml_path.replace('voc_labels', 'images'), save_basename)
        save_path_flabels = os.path.join(dir_xml_path.replace('voc_labels', 'labels'), save_basename)
        
        MakeDirs(os.path.dirname(save_path_flabels))
        
        # Save annotation
        Voc2Yolo(info_dict, save_path_fimages, save_path_flabels)
    
    if isLog:
        print('case: Voc2Yolo done!')
        print('='*col)

def StartCreateNullTxt(ROOT, videos_folder):
    info_txt_path = os.path.join(ROOT, '{}_video2image_image_paths.txt'.format(videos_folder))
    video2image_path = os.path.join(ROOT, '{}_video2image'.format(videos_folder))
    all_image_paths=[]
    
    # Get absolate paths of image file
    if os.path.isfile(info_txt_path):
        # Get all image paths from the video2image_image_paths.txt file
        with open(info_txt_path, 'r') as f:
            line = f.readline()
            while line:
                line = line.split('\n')[0]
                all_image_paths.append(line)
                line = f.readline()
        if all_image_paths:
            if isLog:
                print('Get image paths from the {}'.format(info_txt_path))
    if not os.path.isfile(info_txt_path) or all_image_paths == []:
        # Get all image paths from the video2image folder using func. GetPaths():
        all_image_paths = GetPaths(video2image_path, extension='.jpg')
        if all_image_paths:
            if isLog:
                print('Get image paths from video2image folder using func. GetPaths()')
        else:
            print('There is empty in the {}'.format(info_txt_path))
            print('There is not any .jpg file in the {}'.format(video2image_path))
            print('Error: Can not do the case: "CreateNullTxt"!')
            return
    
    # exclude all_in_one images
    all_image_paths = [path for path in all_image_paths if 'all_in_one' not in path]
    
    # Create null txt file
    for image_path in tqdm(all_image_paths):        
        # Convert image path to yolo label path
        # image_path = '~\videoXX\images\xxxxxx.jpg'
        # save_path_fimages = '~\videoXX\images\xxxxxx.txt'
        save_path_fimages = image_path.split('.')[0] + '.txt'
        
        # save_path_flabels = '~\videoXX\labels\xxxxxx.txt'
        save_path_flabels = save_path_fimages.replace('images', 'labels')
        MakeDirs(os.path.dirname(save_path_flabels))
        
        # Create null txt file
        if not os.path.isfile(save_path_fimages):
            print('', end= '', file= open(save_path_fimages, 'w'))
        if not os.path.isfile(save_path_flabels):
            print('', end= '', file= open(save_path_flabels, 'w'))
    
    if isLog:
        print('case: StartCreateNullTxt done!')
        print('='*col)


# In[12]:


###############################################
#             D A T A   T Y P E S
###############################################
case_list = {
    'Video2ImageAndAll'    : 0,
    'Yolo2VocAllocateData' : 1,
    'UpdateTransformCreate': 2,
}

###############################################
#              C O N S T A N T S
###############################################

###############################################
#        G L O B A L   V A R I A B L E
###############################################
isLog = True # print log
case = case_list['Video2ImageAndAll']
ROOT = 'E:\\Dataset\\DMS\\'
videos_folder = 'EBDD'

## CASE: 'Video2Image'
if case == 0:
    import cv2
    
    interval = 10 # Save an image every <interval> frames
    cut_method = 'normal' # Select "normal" or "four_in_one"
    file_exe = '.MP4' # video extension
    is_Resize = False
    is_KeepRatio = True # father factor is is_Resize, it will keep aspect ratio
    is_Border = False # father factor is is_Resize / is_KeepRatio, it will fill black border if input image is not a square
    single_resize = 640 # use it when is_KeepRatio is true
    resize_shape = (640, 480) # use it when is_KeepRatio is false
    interpolation = cv2.INTER_AREA # zoom out image usually set to cv2.INTER_AREA, zoom in image usually set to cv2.INTER_CUBIC
    is_Sound = False # video with sound or not. True: output video equal original video, False: output video without sound

## For CASE: 'Yolo2Voc', 'Voc2Yolo'
# Dictionary that maps IDs to class names
if case != 0:
    members = 1000 # 一個資料夾 members 筆資料

# prj: DMS, for case: Yolo2VocAllocateData
    class_mapping = {
        '0': 'normal_face',
        '1': 'mask_face',
        '2': 'opened_eye',
        '3': 'closed_eye',
        '4': 'nose',
        '5': 'yawning',
        '6': 'handing',
        '7': 'smoking',
        '8': 'phone',
        '9': 'cigarette',
        '10': 'vape',
        '11': 'cup',
        '12': 'bottle'
    }


# In[13]:


###############################################
#                   M A I N
###############################################
if __name__ == '__main__':
    if isLog:
        col = GetCmdSize()
    
    # Case: Video2ImageAndAll
    if case == 0:
        if not is_Sound:
            from moviepy.editor import VideoFileClip
        
        StartVideo2Image(ROOT, videos_folder, cut_method, file_exe)
        StartImageAllInOne(ROOT, videos_folder)
    
    # Case: Yolo2VocAllocateData
    if case == 1:
        from PIL import Image
        from math import floor
        import xml.etree.ElementTree as ET
        
        StartYolo2Voc(ROOT, videos_folder)
        StartAllocateData(ROOT, videos_folder)
        
        try:
            # Remove all_images folder
            all_images = os.path.join(ROOT, f'{videos_folder}_all_images')
            shutil.rmtree(all_images)
            
            if isLog:
                print(f'Remove {os.path.basename(all_images)} folder')
        except:
            pass
        
        try:
            # Remove check_images and all_voc_labels folder (they are empty folders)
            check_images_path = os.path.join(ROOT, f'{videos_folder}_check_images')
            shutil.rmtree(check_images_path)
            
            if isLog:
                print(f'Remove {os.path.basename(check_images_path)} folder')
        except:
            pass
        
        try:
            # Remove old .txt files (using yolo to auto labeling)
            yolo_labels_path = os.path.join(ROOT, f'{videos_folder}_all_yolo_labels')
            shutil.rmtree(yolo_labels_path)
            
            if isLog:
                print(f'Remove {os.path.basename(yolo_labels_path)}')
        except:
            pass
        
        try:
            # Remove voc files (yolo to voc)
            voc_labels_path = os.path.join(ROOT, f'{videos_folder}_all_voc_labels')
            shutil.rmtree(voc_labels_path)
            
            if isLog:
                print(f'Remove {os.path.basename(voc_labels_path)}')
        except:
            pass
        
#         # Save labels name
#         labels_name = os.path.join(ROOT, 'labels.name')
#         with open(labels_name, 'w') as f:
#             for name in class_mapping.values():
#                 f.write(name + '\n')
    
    # Case: UpdateTransformCreate
    if case == 2:
        import xml.etree.ElementTree as ET
        
        StartUpdateLabels(ROOT, videos_folder)
        StartVoc2Yolo(ROOT, videos_folder)
        StartCreateNullTxt(ROOT, videos_folder)
