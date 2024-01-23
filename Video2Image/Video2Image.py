#!/usr/bin/env python
# coding: utf-8

###############################################
#           H E A D E R   F I L E S
###############################################
import os
import cv2
import shutil
import numpy as np
from tqdm.notebook import tqdm

###############################################
#          F U N C T I O N   L I S T
###############################################
## @brief Description: Get the cmd size
#  @param None
#  
#  @return col
#  @date 20220318  danielwu
def get_cmd_size():
    col, _ = shutil.get_terminal_size()
    col = col - 21
    return col

## @brief Description: Create the folder
#  @param [in] path     folder path
#  
#  @return None
#  @date 20220321  danielwu
def make_dirs(path):
    os.makedirs(path) if not os.path.isdir(path) else None

## @brief Description: Get the paths in specific extensions in the parent folder
#  @param [in] folder       parent folder path
#  @param [in] extensions   file extension
#  
#  @return paths
#  @date 20220321  danielwu
def get_paths(folder, extensions=['MOV', 'MP4', 'mp4']):
    return [os.path.join(dirpath, f) for dirpath, _, filenames in os.walk(folder) 
            for f in filenames if f.endswith(tuple(extensions))]

## @brief Description: Set the saving image name
#
#  @param [in] resize       is it resize or not
#  @param [in] keepRatio    is it keep ratio or not
#  @param [in] border       is it add border or not
#  @param [in] size         resize value
#  @param [in] index        frame index
#
#  @return image name
#  @date  20240118  danielwu
def set_image_name(resize=False, keep_ratio=False, border=False, size=None, index=0):
    if resize:
        if keep_ratio:
            if border:
                # resize + keep ratio + border
                return f'resize_{size}x{size}_border_{index:06d}.jpg'
            else:
                # resize + keep ratio
                return f'resize_{size}p_{index:06d}.jpg'
        else:
            # customized size, e.g. 300x200
            return f'resize_{size[0]}x{size[1]}_{index:06d}.jpg'
    else:
        # original size
        return f'{index:06d}.jpg'

## @brief Description: Calculate the similarity between two image
#
#  @param [in] image_1      the first image
#  @param [in] image_2      the second image
#
#  @return the similarity score
#  @date  20240112  danielwu
def calculate_similarity_images(image_1, image_2, resize_width=16, resize_height=16):
    def dHash(image):
        image = cv2.resize(image, (resize_width + 1, resize_height), interpolation=cv2.INTER_CUBIC)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return np.where(image[:, :-1] > image[:, 1:], 1, 0).flatten().tolist()
    
    def hamin_dist(hash_1, hash_2):
        return 1 - np.count_nonzero(np.bitwise_xor(hash_1, hash_2)) / len(hash_1)
    
    dhash_str_1 = dHash(image_1)
    dhash_str_2 = dHash(image_2)
    return hamin_dist(dhash_str_1, dhash_str_2)

## @brief Description: Resize the image (and fill block border)
#
#  @param [in] image        input image
#  @param [in] new_size     new size
#
#  @return the adjusted image
#  @date  20240118  danielwu
def resize_image_with_border(image, new_height, border=False, interpolation=cv2.INTER_AREA):
    # get the input image size
    h, w = image.shape[:2]

    # get the scaled size
    new_w = round(new_height * (w / h))
    new_h = new_height

    # scale the input image
    resized_image = cv2.resize(image, (new_w, new_h), interpolation)

    # fill the black border
    if border:
        if w > h:
            resized_image = cv2.resize(image, (new_height, int(new_height * h/w)), interpolation)
            border_w = 0
            border_h = round(new_height * (1 - h/w) / 2)
        elif h > w:
            resized_image = cv2.resize(image, (int(new_height * w/h), new_height), interpolation)
            border_w = round(new_height * (1 - w/h) / 2)
            border_h = 0
        border_type = cv2.BORDER_CONSTANT
        border_color = (0, 0, 0)
        resized_image = cv2.copyMakeBorder(resized_image, border_h, border_h, border_w, border_w,
                                           border_type, value=border_color)

    return resized_image

## @brief Description: resize the image and save it
#
#  @param [in] image            image
#  @param [in] save_dir         directory path of saving image
#  @param [in] image_name       image name
#  @param [in] cut              cut position: top, bottom, left, right, ..., whole
#  @param [in] resize           is it resize or not
#  @param [in] keepRatio        is it keep ratio or not
#  @param [in] border           is it add border or not
#  @param [in] size             resize value
#  @param [in] interpolation    interpolation when zoom-in or zoom-out
#
#  @return image name
#  @date  20240118  danielwu
def resize_and_save_image(
        image, save_dir, image_name, cut=None, resize=False,
        keep_ratio=False, border=False, size=None, interpolation=cv2.INTER_AREA):
    if resize:
        if keep_ratio:
            # resize + keep ratio (+ border)
            image = resize_image_with_border(image, size, border, interpolation)
        else:
            # resize + keep ratio
            image = cv2.resize(image, size, interpolation)

    # save the image
    save_image_path = os.path.join(save_dir, cut, image_name) if cut else os.path.join(save_dir, image_name)
    cv2.imwrite(save_image_path, image)

## @brief Description: Convert video to images
#
#  @param [in] video_path               video path
#  @param [in] save_dir                 saving directory path
#  @param [in] cut                      cut method: 1. None 2. top + bottom + whole 3. left + right + whole
#                                                   4. left-top + right-top + left-bottom + right-bottom + whole
#  @param [in] interval                 frame interval
#  @param [in] similarity_threshold     threshold for similarity
#  @param [in] interpolation            interpolation for resizing images
#
#  @return None
#  @date  20240118  danielwu
def cut_video(video_path, save_dir, cuts=None, interval=1, similarity_threshold=0.75, interpolation=cv2.INTER_AREA):    
    # open the video file
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print(f'[ERROR] Can not read: {video_path}')
        return

    # get the video frame size
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # set the focus size for comparing similarity    
    focus_top,  focus_bottom= int(0.18*h), int(0.82*h)
    focus_left, focus_right = int(0.2*w),  int(0.8*w)

    # initialise the index
    frame_count = 0  # index of saved frame
    frame_index = 0  # frame index of the original video (frame_index = interval * frame_count)

    # initialise value for comparing similarity
    sub_frame = [255 * np.ones((h, w, 3), np.uint8)] * len(cuts) if cuts else [255 * np.ones((h, w, 3), np.uint8)]
    pre_frame = sub_frame
    sim_score = [0] * len(cuts) if cuts else [0]

    if cuts:
        # set the cutting coordinates ([x, y, w, h])
        '''
        there is 3 situations:
        1. ['top', 'bottom', 'whole']
        2. ['left', 'right', 'whole']
        3. ['left_top', 'right_top', 'left_bottom', 'right_bottom', 'whole']
        '''
        dw, dh = round(w/2), round(h/2)
        cuts_mapping = {
            'top'         : [0, 0, w, dh],
            'bottom'      : [0, dh, w, dh],
            'left'        : [0, 0, dw, h],
            'right'       : [dw, 0, dw, h],
            'left_top'    : [0, 0, dw, dh],
            'right_top'   : [dw, 0, dw, dh],
            'left_bottom' : [0, dh, dw, dh],
            'right_bottom': [dw, dh, dw, dh],
            'whole'       : [0, 0, w, h],
        }
        coordinates = {cut:cuts_mapping[cut] for cut in cuts if cut in cuts_mapping}

        if not coordinates:
            print(f'[ERROR] Set wrong cuts!')
            return
        
        # create the cut subfolder
        [make_dirs(os.path.join(save_dir, cut)) for cut in cuts]

    while cap.isOpened():
        _, frame = cap.read()
        if frame is None:
            break
            
        if frame_index % interval:
            frame_index += 1
            continue

        # set the image name
        image_name = set_image_name(IS_RESIZE, IS_KEEP_RATIO, IS_BORDER, IMAGE_SIZE, frame_count)

        # set sub frame
        if cuts:
            for i, cut in enumerate(cuts):
                x, y, w, h = coordinates[cut]
                sub_frame[i] = frame[y : y+h, x : x+w]
        else:
            sub_frame = [frame]

        # check similarity
        '''
        1. compare pre-frame and current frame 
        if similarity value over than thresth,
        do NOT save current frame
        2. save the whole image when cutting
        '''
        for i in range(len(sub_frame)): # 1, 3, 5
            cut = cuts[i] if cuts else None
            sim_score[i] = calculate_similarity_images(pre_frame[i], sub_frame[i][focus_top:focus_bottom, focus_left:focus_right])
            pre_frame[i] = sub_frame[i][focus_top:focus_bottom, focus_left:focus_right]

            if sim_score[i] > similarity_threshold and (cut is None or cut != 'whole'):
                continue

            resize_and_save_image(sub_frame[i], save_dir, image_name, cut,
                                  IS_RESIZE, IS_KEEP_RATIO, IS_BORDER, IMAGE_SIZE, interpolation)
        frame_count += 1

        frame_index += 1
    cap.release()

## @brief Description: Get video paths and convert it to image
#
#  @param [in] root             the parent folder path
#  @param [in] videos_folder    which folder want to convert
#  @param [in] file_ext         which file extension want to convert
#
#  @return None
#  @date  20240119  danielwu
def run_video2image(root, videos_folder, file_ext):
    if IS_LOG:
        print('='*col)
        print('[INFO] Start converting video to images...')

    # initialise the paths
    video_paths = []
    all_image_paths = []

    # get video paths from root
    videos_folder_path = os.path.join(root, videos_folder)
    video_paths = get_paths(videos_folder_path, file_ext)
    
    assert video_paths, f'[ERROR] There is no {file_ext} file in {videos_folder_path}\n    Please put the video you want to cut into this folder!'

    if IS_LOG:
        print(f'[INFO] There are {len(video_paths)} videos in dir: {videos_folder_path}')
    
    # cut video process
    for video_path in tqdm(video_paths):
        basename = os.path.basename(video_path)         # videoXX.MOV
        name = os.path.splitext(basename)[0]            # videoXX
        save_path = video_path.replace(videos_folder, f'{videos_folder}_video2image', 1)
        save_path = save_path.replace(basename, name)   # ~/{videos_folder}_video2image/~/videoXX
        save_images_path = os.path.join(save_path, 'images')
        make_dirs(save_images_path)                     # ~/{videos_folder}_video2image/~/videoXX/images

        # cut video, save images and move the original video to the created image folder
        cut_video(video_path, save_images_path, CUT_METHOD, INTERVAL, SIMILARITY_THRESHOLD)

        # remove the audio and then move the video into the new folder
        video = VideoFileClip(video_path)
        if not IS_SOUND and video.audio:
            # set the video saving path
            video_save_path = os.path.join(save_path, basename)

            # remove the audio
            without_audio_video = video.without_audio()
            without_audio_video.write_videofile(video_save_path, codec='libx264', logger=None)

            # close the video
            video.close()

            # try to remove the old video
            try:
                os.remove(video_path)
            except:
                print(f'[ERROR] Can not remove: {video_path}')
        else:
            video.close()
            shutil.move(video_path, save_path)

        # create the txt file and write image paths into the file
        txt_file = f'{name}_image_paths.txt'
        txt_path = os.path.join(save_path, txt_file)
        image_paths = get_paths(save_images_path, 'jpg')
        all_image_paths.extend(image_paths)
        with open(txt_path, 'w') as f:
            for image_path in image_paths:
                if image_path != image_paths[-1]:
                    f.write('{}\n'.format(image_path))
                else:
                    f.write(image_path)

    # create the txt file and write all image paths into the file
    txt_file = f'{videos_folder}_video2image_image_paths.txt'
    txt_path = os.path.join(root, txt_file)
    with open(txt_path, 'w') as f:
        for image_path in all_image_paths[:-1]:
            f.write(f'{image_path}\n')
        f.write(all_image_paths[-1])

    # remove original video folder (it's an empty folder)
    if not os.listdir(videos_folder_path):
        shutil.rmtree(videos_folder_path)
        print(f'[INFO] Remove the folder: {videos_folder_path}') if IS_LOG else None
    else:
        print(f'[WARNING][{run_video2image.__name__}] There are some files in {videos_folder_path}')
    
    if IS_LOG:
        print('[INFO] Converting video to images is done!')
        print('='*col)

## @brief Description: Copy every images to the same one folder
#
#  @param [in] root             the parent folder path
#  @param [in] videos_folder    which folder want to run
#
#  @return None
#  @date  20240119  danielwu
def run_image_in_one_folder(root, videos_folder):
    if IS_LOG:
        print('='*col)
        print('[INFO] Start copying images into the same folder...')
        
    # initialise the paths
    all_image_paths = []
    
    # get all image paths from the video2image_image_paths.txt file
    ref_info_file_path = os.path.join(root, f'{videos_folder}_video2image_image_paths.txt')
    if os.path.isfile(ref_info_file_path):
        with open(ref_info_file_path, 'r') as f:
            line = f.readline()
            while line:
                line = line.split('\n')[0]
                all_image_paths.append(line)
                line = f.readline()
        if IS_LOG and all_image_paths:
            print(f'[INFO] Get image paths from {ref_info_file_path}')

    # get all image paths from the video2image folder using func. get_paths():
    if not os.path.isfile(ref_info_file_path) or not all_image_paths:
        video2image_path = os.path.join(root, f'{videos_folder}_video2image')
        all_image_paths = get_paths(video2image_path, ['jpg'])
        if IS_LOG and all_image_paths:
            print('[INFO] Get image paths from video2image folder using func get_paths()')
        
    assert all_image_paths, f'[ERROR] There is empty in {ref_info_file_path}\n        There is not any jpg file in {video2image_path}\n        Please do the case: start_video2image first!'

    all_images_path = os.path.join(root, f'{videos_folder}_all_images')
    make_dirs(all_images_path)
    
    # remove images from the 'all_in_one' or 'whole' folder, there is no need to auto-label
    image_paths = [path for path in all_image_paths if not any(key in path for key in ['all_in_one', 'whole'])]
    
    # copy images from video2image folder to all_images folder
    for count, image_path in enumerate(tqdm(image_paths)): 
        save_image_path = os.path.join(all_images_path, f'{count:06d}.jpg')
        shutil.copy(image_path, save_image_path)

    # create and write the txt file (new_image_name: image_original_path)
    txt_file = f'{videos_folder}_allinone_image_paths.txt'
    txt_path = os.path.join(root, txt_file)
    with open(txt_path, 'w') as f:
        flag = ''
        f.write('## # <video2image Relative Path>\n')
        f.write('## image basename of all_images: image relative paht of video2image')
        for count, image_path in enumerate(image_paths):
            relative_path = image_path.split(root)[1]
            dirname = os.path.dirname(relative_path)
            if dirname != flag:
                f.write(f'\n\n# {dirname}')
                flag = dirname
            f.write(f'\n{count:06d}.jpg : {relative_path}')
            count += 1
    
    if IS_LOG:
        print(f'[INFO] Create the folder: {all_images_path}')
        print('[INFO] Copying images into the same folder is done!')
        print('='*col)
        print(f'[INFO] 1. Please manually enter yolov5 command for auto-labeling:')
        print('       $ python detect.py --weights best.pt --source path/ --conf-thres 0.5' , end='')
        print('--save-txt --project save/to/dir_path/ --name xxx --line-thickness 1 --hide-labels')
        print(f'       2. Copy save/to/dir_path/xxx to {os.path.join(root, videos_folder)}_auto_labeled_images')
        print(f'       3. Copy save/to/dir_path/xxx/labels to {os.path.join(root, videos_folder)}_auto_labeled_labels')
        print('='*col)

## @brief Description: Create xml root: base info (for txt to xml: part 1)
#
#  @return root
#  @date  20240119  danielwu
def create_root(image_path, width, height, image_channel=3):
    root = ET.Element('annotations')
    ET.SubElement(root, 'filename').text = os.path.basename(image_path)
    ET.SubElement(root, 'folder').text = os.path.dirname(image_path)
    ET.SubElement(root, 'segmented').text = str(0)
    size = ET.SubElement(root, 'size')
    ET.SubElement(size, 'width').text = str(width)
    ET.SubElement(size, 'height').text = str(height)
    ET.SubElement(size, 'depth').text = str(image_channel)
    return root

## @brief Description: Create xml root: object annotation (for txt to xml: part 2)
#
#  @return root
#  @date  20240119  danielwu
def create_object_annotation(root, voc_labels):
    for voc_label in voc_labels:
        obj = ET.SubElement(root, 'object')
        ET.SubElement(obj, 'name').text = voc_label[0]
        ET.SubElement(obj, 'pose').text = 'Unspecified'
        ET.SubElement(obj, 'truncated').text = str(0)
        ET.SubElement(obj, 'difficult').text = str(0)
        bbox = ET.SubElement(obj, 'bndbox')
        ET.SubElement(bbox, 'xmin').text = str(voc_label[1])
        ET.SubElement(bbox, 'ymin').text = str(voc_label[2])
        ET.SubElement(bbox, 'xmax').text = str(voc_label[3])
        ET.SubElement(bbox, 'ymax').text = str(voc_label[4])
    return root

## @brief Description: Pretty xml root: indent and newline (for txt to xml: part 3)
#
#  @date  20240119  danielwu
def pretty_xml(element, indent='\t', newline='\n', level=0): # elemnt為傳進來的Elment類，引數indent用於縮排，newline用於換行
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

## @brief Description: Create xml file (for txt to xml: part 4)
#
#  @date  20240119  danielwu
def create_xml_file(image_path, save_folder, file_prefix, width, height, voc_labels):
    root = create_root(image_path, width, height)
    root = create_object_annotation(root, voc_labels)
    pretty_xml(root)
    save_path = os.path.join(save_folder, f'{file_prefix}.xml')
    tree = ET.ElementTree(root)
    tree.write(save_path)

## @brief Description: Create xml file: caculate bndbox (for txt to xml: part 5)
#
#  @date  20240119  danielwu
def yolo2voc_format(label_path, image_path, class_mapping, save_folder):
    basename = os.path.basename(label_path)  # xxxxxx.txt
    file_prefix = basename.split('.')[0]     # xxxxxx
    image = Image.open(image_path)
    w, h = image.size
    
    with open(label_path) as f:
        lines = f.readlines()
        voc_labels = []
        for line in lines:
            voc = []
            line = line.strip() # remove space or newline
            data = line.split() # split space or newline
            if not len(data):
                continue
            voc.append(class_mapping.get(int(data[0])))
            bbox_width = float(data[3]) * w
            bbox_height = float(data[4]) * h
            center_x = float(data[1]) * w
            center_y = float(data[2]) * h
            voc.append(floor(center_x - (bbox_width / 2)))
            voc.append(floor(center_y - (bbox_height / 2)))
            voc.append(floor(center_x + (bbox_width / 2)))
            voc.append(floor(center_y + (bbox_height / 2)))
            voc_labels.append(voc)
        create_xml_file(image_path, save_folder, file_prefix, w, h, voc_labels)

## @brief Description: Convert yolo format to voc format
#
#  @param [in] root             the parent folder path
#  @param [in] videos_folder    which folder want to convert
#  @param [in] class_mapping    class {number}: {name}
#
#  @return None
#  @date  20240122  danielwu
def run_yolo2voc_format(root, videos_folder, class_mapping):
    if IS_LOG:
        print('='*col)
        print('[INFO] Start converting yolo format to voc format...')

    # initialise paths
    auto_labeled_images_path = os.path.join(root, f'{videos_folder}_auto_labeled_images')
    auto_labeled_labels_path = os.path.join(root, f'{videos_folder}_auto_labeled_labels')
    voc_labels_path = os.path.join(root, f'{videos_folder}_auto_labeled_voc_labels')
    image_replace = False
    
    # check the auto-labeled labels folder exist or not (it is yolo format)
    assert os.path.isdir(auto_labeled_labels_path), f'The auto-labeled labels folder does not exist: {auto_labeled_labels_path}'

    # get the paths of yolo format label produced by auto labeled, and check whether any file in the auto-labeled labels folder
    txt_paths = get_paths(auto_labeled_labels_path, ['txt'])
    assert txt_paths, f'There are no auto-labeled label files in {auto_labeled_labels_path}'
    
    # check the auto-labeled images folder exist or not
    if not os.path.isdir(auto_labeled_images_path):
        image_replace = True
        print(f'[WARRNING][{run_yolo2voc_format.__name__}] The auto-labeled labels folder is exist, but the auto-labeled images folder does not exist!')
        print('           It will use the original images, not auto-labeled images.')

    make_dirs(voc_labels_path)

    # processing: yolo format to voc format
    for txt_path in tqdm(txt_paths):
        # set the corresponding path
        """
        txt_path = ~/{video_folder}_auto_labeled_labels/xxxxxx.txt
        image_path = ~/{video_folder}_auto_labeled_images/xxxxxx.jpg
        """
        image_path = txt_path.replace('auto_labeled_labels',
                                      'auto_labeled_images' if not image_replace else 'all_images').replace('txt', 'jpg')
        
        yolo2voc_format(txt_path, image_path, class_mapping, voc_labels_path)
    
    if IS_LOG:
        print(f'[INFO] Create the folder: {voc_labels_path}')
        print('[INFO] Converting yolo format to voc format is done!')
        print('='*col)

## @brief Description: Allocate data so others can conveniently re-check the labels
#
#  @param [in] root             the parent folder path
#  @param [in] videos_folder    which folder want to allocate
#
#  @return None
#  @date  20240122  danielwu
def run_allocate_data(root, videos_folder):
    if IS_LOG:
        print('='*col)
        print('[INFO] Start allocating data...')

    # initialise paths
    auto_labeled_images_path = os.path.join(root, f'{videos_folder}_auto_labeled_images')
    help_check_path = os.path.join(root, f'{videos_folder}_help_check_labels')
    image_replace = False

    # check the auto-labeled images folder exist or not
    if not os.path.isdir(auto_labeled_images_path):
        image_replace = True
        auto_labeled_images_path = os.path.join(root, f'{videos_folder}_all_images')
        print(f'[WARRNING][{run_allocate_data.__name__}] The auto-labeled labels folder is exist, but the auto-labeled images folder does not exist!')
        print('           It will use the original images, not auto-labeled images.')
        
    image_paths = get_paths(auto_labeled_images_path, ['jpg'])
    
    # processing: allocate data
    for count, image_path in enumerate(tqdm(image_paths)):
        # initialise index and paths
        folder_idx = count // MEMBERS # {MEMBERS} datas in per folder
        save_image_path = os.path.join(help_check_path, str(folder_idx), 'images')
        save_label_path = os.path.join(help_check_path, str(folder_idx), 'labels')
        
        # create folders
        [make_dirs(f) for f in [save_image_path, save_label_path]]

        # set the corresponding path
        label_path = image_path.replace('auto_labeled_images' if not image_replace else 'all_images',
                                        'auto_labeled_voc_labels').replace('jpg', 'xml')
        
        # copy the original image into allocating folder
        shutil.move(image_path, save_image_path)
        # copy the voc label into allocating folder
        shutil.move(label_path, save_label_path) if os.path.isfile(label_path) else None
    
    print(f'[INFO] Create the folder: {help_check_path}') if IS_LOG else None
    
    # remove the folders for the staged mission
    all_images_path = os.path.join(root, f'{videos_folder}_all_images')
    auto_labeled_labels_path = os.path.join(root, f'{videos_folder}_auto_labeled_labels')
    auto_labeled_voc_labels_path = os.path.join(root, f'{videos_folder}_auto_labeled_voc_labels')
    remove_folders = (all_images_path, auto_labeled_images_path, auto_labeled_labels_path, auto_labeled_voc_labels_path)

    for folder_path in remove_folders:
        try:
            shutil.rmtree(folder_path)
            print(f'[INFO] Remove the folder: {folder_path}') if IS_LOG else None
        except:
            print(f'[WARNING][{run_allocate_data.__name__}] Can not remove the folder: {folder_path}')

    if IS_LOG:
        print('[INFO] Allocating data is done!')
        print('='*col)

## @brief Description: Update the labels from 'help_check_labels' to the 'video2images' folder
#
#  @param [in] root             the parent folder path
#  @param [in] videos_folder    which folder want to update
#
#  @return None
#  @date  20240122  danielwu
def run_update_labels(root, videos_folder):
    if IS_LOG:
        print('='*col)
        print('[INFO] Start update labels...')

    # initialise paths
    help_check_path = os.path.join(root, f'{videos_folder}_help_check_labels')
    ref_info_file_path = os.path.join(root, f'{videos_folder}_allinone_image_paths.txt')
    
    with open(ref_info_file_path, 'r') as f:
        """
        read the file: allinone_image_paths.txt,
        and create a dictionary: relative_path, its key and value are:
        image basename of all_images: image relative paht of video2image
        """
        relative_path = {}
        line = f.readline()
        while line:
            # ignore comments
            if '#' in line:
                line = f.readline()
                continue

            line = line.split('\n')[0] # remove '\n' in each line

            # ignore empty line
            if not line :
                line = f.readline()
                continue

            relative_path[line.split('.')[0]] = line.split(' : ')[1]
            line = f.readline()
    
    # get xml file paths from help_check_labels folder
    xml_paths = get_paths(help_check_path, ['xml'])
    
    # processing: update labels
    for xml_path in tqdm(xml_paths):
        """
        using path of xml file to get original image relative path
        relative_path[xxxxxx] = ~/videoXX/images/yyyyyy.jpg
        split_relative_path = [~, videoXX, images]
        save_basename = yyyyyy.xml
        """
        basename = os.path.basename(xml_path) # xxxxxx.xml
        file_prefix = basename.split('.')[0] # xxxxxx
        split_relative_path = os.path.dirname(relative_path[file_prefix]).split('\\')
        save_basename = os.path.splitext(os.path.basename(relative_path[file_prefix]))[0] + '.xml'
        
        # update saving xml file folder path and create the folder
        save_path = root
        for path in split_relative_path:
            save_path = os.path.join(save_path, path)
        save_path = save_path.replace('images', 'voc_labels')
        make_dirs(save_path)
        
        # copy xml file from help_check_labels folder to video2image folder
        save_path = os.path.join(save_path, save_basename)
        shutil.copy(xml_path, save_path)

    # remove help_check_labels folder that is the staged mission
    try:
        shutil.rmtree(help_check_path)
        print(f'[INFO] Remove the folder: {help_check_path}') if IS_LOG else None
    except:
        print(f'[WARNING][{run_update_labels.__name__}] Can not remove the folder: {help_check_path}')
        
    if IS_LOG:
        print('[INFO] Updating labels is done!')
        print('='*col)

## @brief Description: Get the data from xml annotation (for xml to txt: part 1)
#
#  @param [in] xml_file     the annotation (xml) file path
#
#  @return info_dict
#  @date  20240122  danielwu
def extract_info_from_xml(xml_file):
    root = ET.parse(xml_file).getroot()
    
    # initialise the info dict 
    info_dict = {}
    info_dict['bboxes'] = []
    
    # get the filename 
    info_dict['filename'] = os.path.basename(xml_file)

    # parse the xml tree
    for elem in root:      
        # get the image size
        if elem.tag == 'size':
            image_size = []
            for subelem in elem:
                image_size.append(int(subelem.text))
            
            info_dict['image_size'] = tuple(image_size)
        
        # get details of the bounding box 
        elif elem.tag == 'object':
            bbox = {}
            for subelem in elem:
                if subelem.tag == 'name':
                    bbox['class'] = subelem.text
                    
                elif subelem.tag == 'bndbox':
                    for subsubelem in subelem:
                        bbox[subsubelem.tag] = int(subsubelem.text)            
            info_dict['bboxes'].append(bbox)
    
    return info_dict

## @brief Description: Convert the info dict to the required yolo format and write it to disk (for xml to txt: part 2)
#
#  @date  20240122  danielwu
def voc2yolo_format(info_dict, class_mapping, txt_paths):
    print_buffer = []
    reverse_class_mapping = {}
    
    for item in class_mapping.items():
        reverse_class_mapping[item[1]] = int(item[0])
    
    # for each bounding box
    for b in info_dict['bboxes']:
        try:
            class_id = reverse_class_mapping[b['class']]
        except KeyError:
            print(f'[ERROR] Invalid class. Must be one from {reverse_class_mapping.keys()}')
        
        # transform the bbox co-ordinates as per the format required by YOLOv5
        b_center_x = (b['xmin'] + b['xmax']) / 2 
        b_center_y = (b['ymin'] + b['ymax']) / 2
        b_width    = (b['xmax'] - b['xmin'])
        b_height   = (b['ymax'] - b['ymin'])
        
        # normalise the co-ordinates by the dimensions of the image
        image_w, image_h, _ = info_dict['image_size']  
        b_center_x /= image_w 
        b_center_y /= image_h 
        b_width    /= image_w 
        b_height   /= image_h 
        
        # write the bbox details to the file 
        print_buffer.append(f'{class_id} {b_center_x:.3f} {b_center_y:.3f} {b_width:.3f} {b_height:.3f}')
            
    # save the annotation to disk
    [print('\n'.join(print_buffer), end='', file=open(txt_path, 'w')) for txt_path in txt_paths]

## @brief Description: Convert voc format to yolo format and save into 'images' folder and 'labels' folder
#
#  @param [in] root             the parent folder path
#  @param [in] videos_folder    which folder want to convert
#  @param [in] class_mapping    class {number}: {name}
#
#  @return None
#  @date  20240122  danielwu
def run_voc2yolo_format(ROOT, videos_folder, class_mapping):
    if IS_LOG:
        print('='*col)
        print('[INFO] Start converting voc format to yolo format...')

    # initialise the path
    video2image_path = os.path.join(ROOT, f'{videos_folder}_video2image')
    
    # get xml file paths from video2image folder
    xml_paths = get_paths(video2image_path, ['xml'])
    
    # processing: voc format to yolo format
    for xml_path in tqdm(xml_paths):
        # get the information from xml file
        info_dict = extract_info_from_xml(xml_path)
        
        # convert xml path to save txt path
        """
        xml_path = ~/videoXX/voc_labels/xxxxxx.xml
        dir_xml_path = ~/videoXX/voc_labels
        save_basename = xxxxxx.txt
        save_path_fimages = ~/videoXX/images/xxxxxx.txt
        save_path_flabels = ~/videoXX/labels/xxxxxx.txt
        """
        dir_xml_path = os.path.dirname(xml_path)
        save_basename = os.path.basename(xml_path).replace('xml', 'txt')
        
        # update saving txt file folder path and create the folder
        save_file_to_images = os.path.join(dir_xml_path.replace('voc_labels', 'images'), save_basename)
        save_file_to_labels = os.path.join(dir_xml_path.replace('voc_labels', 'labels'), save_basename)
        
        make_dirs(os.path.dirname(save_file_to_labels))
        
        # save annotation
        save_paths = [save_file_to_images, save_file_to_labels]
        voc2yolo_format(info_dict, class_mapping, save_paths)
        
    if IS_LOG:
        print('[INFO] Converting voc format to yolo format is done!')
        print('='*col)

## @brief Description: Create an empty label file if the image dose not have a label file
#
#  @param [in] root             the parent folder path
#  @param [in] videos_folder    which folder want to run
#
#  @date  20240122  danielwu
def run_create_null_label_file(root, videos_folder):
    if IS_LOG:
        print('='*col)
        print('[INFO] Start creating null label file...')

    # initialise the path
    all_image_paths = []
    
    # get all image paths from the video2image_image_paths.txt file
    ref_info_file_path = os.path.join(root, f'{videos_folder}_video2image_image_paths.txt')
    if os.path.isfile(ref_info_file_path):
        with open(ref_info_file_path, 'r') as f:
            line = f.readline()
            while line:
                line = line.split('\n')[0]
                all_image_paths.append(line)
                line = f.readline()
        if IS_LOG and all_image_paths:
            print(f'[INFO] Get image paths from {ref_info_file_path}')

    # get all image paths from the video2image folder using func. get_paths():
    if not os.path.isfile(ref_info_file_path) or not all_image_paths:
        video2image_path = os.path.join(root, f'{videos_folder}_video2image')
        all_image_paths = get_paths(video2image_path, ['jpg'])
        if IS_LOG and all_image_paths:
            print('[INFO] Get image paths from video2image folder using func. get_paths()')

    assert all_image_paths, f'[ERROR] There is empty in {ref_info_file_path}\n        There is not any jpg file in {video2image_path}'

    # remove images from the 'all_in_one' or 'whole' folder
    all_image_paths = [path for path in all_image_paths if not any(key in path for key in ['all_in_one', 'whole'])]
    
    # # processing: create null lable file
    for image_path in tqdm(all_image_paths):
        """
        convert image path to yolo label path
        image_path = ~/videoXX/images/xxxxxx.jpg
        save_file_to_images = ~/videoXX/images/xxxxxx.txt
        """
        save_file_to_images = image_path.replace('jpg', 'txt')
        
        # save_file_to_labels = ~/videoXX/labels/xxxxxx.txt
        save_file_to_labels = save_file_to_images.replace('images', 'labels')
        make_dirs(os.path.dirname(save_file_to_labels))
        
        # create null txt file
        save_paths = [save_file_to_images, save_file_to_labels]
        [print('', end='', file=open(txt_path, 'w')) for txt_path in save_paths if not os.path.isfile(txt_path)]

    if IS_LOG:
        print('[INFO] Creating null label file is done!')
        print('='*col)

###############################################
#             D A T A   T Y P E S
###############################################
case_list = {
    0: 'video2image_and_all',
    1: 'yolo2voc_and_allocate',
    2: 'update_and_transform_and_null',
}

cut_method_list = {
    0: None,
    1: ['top', 'bottom', 'whole'],
    2: ['left', 'right', 'whole'],
    3: ['left_top', 'right_top', 'left_bottom', 'right_bottom', 'whole'],
}

###############################################
#              C O N S T A N T S
###############################################

###############################################
#        G L O B A L   V A R I A B L E
###############################################
IS_LOG = True # print log or not
case = case_list[1] # please refer case_list
ROOT = 'E:\\all_videos\\'
videos_folder = '240123'

## CASE: 'video2image_and_all'
if case == 'video2image_and_all':    
    INTERVAL = 29 # Save an image every <interval> frames
    CUT_METHOD = cut_method_list[2] # please refer cut_method_list
    FILE_EXT = ['mp4', 'MP4', 'MOV'] # video extension # mp4 # MP4 # MOV
    SIMILARITY_THRESHOLD = 0.7 # threshold about the similarity between the current frame and the next frame
    IS_RESIZE = True
    IS_KEEP_RATIO = True # father factor is IS_RESIZE, it will keep original aspect ratio
    IS_BORDER = False # father factor is IS_RESIZE + IS_KEEP_RATIO, it will fill black border if input image is not a square
    IMAGE_SIZE = 1080 if IS_KEEP_RATIO else (640, 360) # father factor is IS_RESIZE, if IS_BORDER == True: HxH, else: WxH, if IS_KEEP_RATIO == False: MxN
    IS_SOUND = False # video with sound or not. True: output video equal original video, False: output video without sound
    # zoom out image usually set to cv2.INTER_AREA, zoom in image usually set to cv2.INTER_CUBIC

## For CASE: 'yolo2voc_and_allocate', 'update_and_transform_and_null'
# dictionary that maps IDs to class names
if case == 'yolo2voc_and_allocate' or case == 'update_and_transform_and_null':
    MEMBERS = 1000 # {MEMBERS} datas in per folder

    # prj: COCO ADAS
    CLASS_MAPPING = {
        0: 'person',
        1: 'bicycle',
        2: 'car',
        3: 'motorcycle',
        4: 'aeroplane',
        5: 'bus',
        6: 'train',
        7: 'truck'
    }

###############################################
#                   M A I N
###############################################
if __name__ == '__main__':
    if IS_LOG:
        col = get_cmd_size()
    
    # case: video2image_and_all
    if case == 'video2image_and_all':
        if not IS_SOUND:
            from moviepy.editor import VideoFileClip
        
        run_video2image(ROOT, videos_folder, FILE_EXT)
        run_image_in_one_folder(ROOT, videos_folder)
    
    # case: yolo2voc_and_allocate
    if case == 'yolo2voc_and_allocate':
        from PIL import Image
        from math import floor
        import xml.etree.ElementTree as ET
        
        run_yolo2voc_format(ROOT, videos_folder, CLASS_MAPPING)
        run_allocate_data(ROOT, videos_folder)
        
        # # save labels name
        # labels_name = os.path.join(ROOT, 'labels.name')
        # with open(labels_name, 'w') as f:
        #     for name in CLASS_MAPPING.values():
        #         f.write(name + '\n')
    
    # case: update_and_transform_and_null
    if case == 'update_and_transform_and_null':
        import xml.etree.ElementTree as ET
        
        run_update_labels(ROOT, videos_folder)
        run_voc2yolo_format(ROOT, videos_folder, CLASS_MAPPING)
        run_create_null_label_file(ROOT, videos_folder)