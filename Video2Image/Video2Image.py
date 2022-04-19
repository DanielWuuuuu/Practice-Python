#!/usr/bin/env python
# coding: utf-8

# # 影片轉圖片
# 
# ### args:
# 1. `isLog`         : 是否顯示log
# 2. `case`          : 功能選擇 ( 參考 case_list )
# 3. `ROOT`          : 根目錄 (包含原始影片資料夾、創建影像資料夾等)
# 4. `videos_folder` : 影片母資料夾路徑
# 5. `interval`      : 幀數間格 (每幾幀擷取一張影像)
# 
# ### 流程
# 
# 1. 執行CASE 'Video2ImageAndAll'  
#    (1) 將`videos_folder`資料夾內所有影片切成影像，輸出至`video2image`資料夾  
#    (2) 將切片的影像複製一份至`all_images`資料夾內，待自動標籤用  
#    
# 2. 另外執行YOLO v5  
#    `!python detect.py --weights best.pt --source path/*.jpg --save-txt path/*.txt`  
#    (1) 將`yolov5/runs/detect/expXX/labels`手動複製至`ROOT/videos_folder_all_yolo_labels`  
#    (2) 將`yolov5/runs/detect/expXX`內之影像手動複製至`ROOT/videos_folder_check_images`  
#    
# 3. 執行CASE 'Yolo2VocAllocateData':  
#    (1) 將`all_yolo_labels`資料夾內`.txt`檔轉成`.xml`檔至`all_voc_labels`資料夾內  
#    (2) 將`check_images`(對應`all_voc_labels`)每2000筆分配在一個資料夾，母資料夾為`help_check_labels`，接著就可以請同仁幫忙檢查自動標籤是否有誤，並手動修正`.xml`檔內類別座標資訊  
#    (3) 將刪除`all_images`、`check_images`資料夾與`all_voc_labels`資料夾  
#    
# 4. 執行CASE 'UpdateTransformCreate':  
#    a. 將檢查完的`.xml`檔(母資料夾為`help_check_labels`)更新回`video2image/videoXX/voc_label`資料夾內  
#    b. 將`voc_label`資料夾內`.xml`檔轉成`.txt`檔至`videoXX_img`資料夾內  
#    c. 建立影像空標籤的`.txt`檔  
# 
# ### 影片資料夾樹狀圖:
# 
# 說明:
# 1. 資料夾可為多階層 ( 以下為範例 ):
# 
# ```
# ROOT  
# └─ videos_folder  
#    ├─ folder1  
#    │  ├─ video01.MOV  
#    │  ├─ video02.MOV  
#    │  └─ ..  
#    ├─ folder2  
#    │  ├─ video01.MOV  
#    │  ├─ video02.MOV  
#    │  └─ ..  
#    └─ ..  
# ```
# ---
# 
# ### CASE 'Video2ImageAndAll'
# 
# 說明:
# 1. 依序執行CASE:Video2Image與CASE:ImageAllInOne
# 
# ---
# 
# ### CASE 'Yolo2VocAllocateData'
# 
# 說明:
# 1. 前置作業請參考CASE:'Yolo2Voc'第1、2點說明
# 2. 依序執行CASE:Yolo2Voc與CASE:AllocateData
# 3. 額外刪除`all_images`資料夾
# 
# ---
# 
# ### CASE 'UpdateTransformCreate'
# 
# 說明:
# 1. 依序執行CASE:UpdateLabels、CASE:Voc2Yolo與CASE:CreateNullTxt
# 
# ---
# 
# ### CASE: 'Video2Image'
# 
# 說明:
# 1. 影片切成影像
# 2. 輸出影像資料夾樹狀圖 ( 階層會與來源相同 ):
# 
# ```
# ROOT  
# ├─ videos_folder              # 原始影片  
# │                             # 執行此CASE後，刪除此資料夾!  
# ├─ videos_folder_video2image  # 執行此CASE後，輸出  
# │  ├─ folder1  
# │  │  ├─ video01  
# │  │  │  ├─ video01_img       # 影片 > 影像儲存資料夾  
# │  │  │  │  ├─ 000000.jpg  
# │  │  │  │  ├─ ..  
# │  │  │  │  └─ 000010.jpg  
# │  │  │  ├─ video01.MOV        # 「搬移」原始影片
# │  │  │  └ video01_path.txt    # 影像絕對路徑
# │  │  ├─ ..  
# │  │  └─ videoXX  
# │  │     ├─ videoXX_img  
# │  │     │  ├─ 000000.jpg  
# │  │     │  ├─ ..  
# │  │     │  └─ 000020.jpg  
# │  │     ├─ videoXX.MOV  
# │  │     └ videoXX_path.txt  
# │  ├─ folder2  
# │  │  ├─ video01  
# │  │  ├─ ..  
# │  │  └─ videoXX  
# │  └─ ..  
# └ video2image_image_paths.txt  # 執行此CASE後，輸出  
# ```
# 3. video2image_image_paths.txt為儲存切片後各影像的路徑
# 
# ---
# 
# ### CASE 'ImageAllInOne'
# 
# 說明:
# 1. 將在各個資料夾內的影像複製出來放在`all_images`資料夾內 ( YOLO自動標籤用 )
# 2. 輸出影像資料夾樹狀圖 ( 輸出的影像序號會接續下去 ):
# 
# ```
# ROOT  
# ├─ videos_folder_all_images     # 執行此CASE後，輸出  
# │  ├─ 000000.jpg  
# │  ├─ ..  
# │  └─ xxxxxx.jpg  
# ├─ videos_folder_video2image    # 執行CASE:'Video2Image'後輸出  
# ├─ allinone_image_paths.txt     # 執行此CASE後，輸出 ( 如第4點範例 )  
# └─ video2image_image_paths.txt  # 執行CASE:'Video2Image'後輸出  
# ```
# 3. allinone_image_paths.txt資訊如下:
# 
# ```
# ## # <video2image Relative Path>\n')
# ## image basename of all_images: image relative paht of video2image
# 
# # folder1/video01/video01_img
# 000000.jpg : folder1/video01/video01_img/000000.jpg
# ..
# 000010.jpg : folder1/video01/video01_img/000010.jpg
# 
# # folder1/videoXX/videoXX_img
# 000011.jpg : folder1/videoXX/videoXX_img/000000.jpg
# ..
# 000031.jpg : folder1/videoXX/videoXX_img/000020.jpg
# ..
# ```
# ---
# 
# ### CASE 'Yolo2Voc'
# 
# 說明:
# 1. 將`all_yolo_labels`資料夾內`.txt`檔轉成`.xml`檔至`all_voc_labels`資料夾內
# 2. 先執行YOLO v5 detect.py:
#    `python detect.py --weights best.pt --source path/*.jpg --save-txt`
#    (1) 將`yolov5/runs/detect/expXX/labels`手動複製至`ROOT/videos_folder_all_yolo_labels`
#    (2) 將`yolov5/runs/detect/expXX`內之影像手動複製至`ROOT/videos_folder_check_images`
# 3. 執行完YOLO v5 detect.py後，在執行此CASE
# 4. 輸出標籤資料夾樹狀圖:
# 
# ```
# ROOT  
# ├─ videos_folder_all_voc_labels   # 執行此CASE後，輸出  
# │  ├─ 000000.xml  
# │  ├─ ..  
# │  └─ xxxxxx.xml  
# ├─ videos_folder_all_yolo_labels  # 手動將YOLO偵測物件輸出的.txt檔放入此資料夾  
# │  ├─ 000000.txt  
# │  ├─ ..  
# │  └─ xxxxxx.txt  
# ├─ videos_folder_check_images     # 手動將YOLO偵測物件輸出的.jpg檔放入此資料夾  
# │  ├─ 000000.jpg  
# │  ├─ ..  
# │  └─ xxxxxx.jpg  
# ├─ videos_folder_video2image      # 執行CASE:'Video2Image'後輸出  
# ├─ allinone_image_paths.txt       # 執行CASE:'ImageAllInOne'後輸出  
# └─ video2image_image_paths.txt    # 執行CASE:'Video2Image'後輸出  
# ```
# ---
# 
# ### CASE 'AllocateData'
# 
# 說明:
# 1. 將`check_images`資料夾內影像及`all_voc_labels`資料夾內標籤檔按比例重新分配，
#    每2000個檔案放在一個資料夾，接著就可以請同仁們幫忙檢查自動標籤是否有誤，並手動修正
# 2. 執行後將刪除`all_voc_labels`資料夾與`check_images`資料夾
# 3. 分配資料夾樹狀圖:
# 
# ```
# ROOT  
# ├─ videos_folder_all_yolo_labels    # 執行此CASE後，刪除此資料夾!  
# ├─ videos_folder_help_check_labels  # 執行此CASE後，輸出  
# │  ├─ 0  
# │  │  ├─ images  
# │  │  │  ├─ 000000.jpg  
# │  │  │  ├─ ..  
# │  │  │  └─ 001999.jpg  
# │  │  └─ labels  
# │  │  │  ├─ 000000.xml  
# │  │  │  ├─ ..  
# │  │  │  └─ 001999.xml  
# │  ├─ 1  
# │  │  ├─ images  
# │  │  │  ├─ 002000.jpg  
# │  │  │  ├─ ..  
# │  │  │  └─ 003999.jpg  
# │  │  └─ labels  
# │  │     ├─ 002000.jpg  
# │  │     ├─ ..  
# │  │     └─ 003999.jpg  
# │  └─ ..  
# ├─ videos_folder_video2image        # 執行CASE:'Video2Image'後輸出  
# ├─ allinone_image_paths.txt         # 執行CASE:'Video2Image'後輸出  
# └─ video2image_image_paths.txt      # 執行CASE:'ImageAllInOne'後輸出  
# ```
# ---
# 
# ### CASE 'UpdateLabels'
# 
# 說明:
# 1. 更新自動標籤檔: 將各個資料夾內檢查好的`.xml`檔放回`video2image`資料夾
# 2. 同仁們檢查好標籤後，請同仁們回傳整個`help_check_labels`資料夾(子資料夾`images`可不用回傳)
# 3. 將回傳的`help_check_labels`資料夾覆蓋回自己原本的`help_check_labels`資料夾 
#    ( 更新標籤檔: 檔案已存在 => 勾選 全部取代 )
# 4. 執行前資料夾樹狀圖:
# 
# ```
# ROOT  
# ├─ videos_folder_all_images         # 執行CASE:'ImageAllInOne'後輸出  
# ├─ videos_folder_help_check_labels  # 手動將檢查好的help_check_labels資料夾覆蓋回來  
# ├─ videos_folder_video2image        # 執行CASE:'Video2Image'後輸出  
# ├─ allinone_image_paths.txt         # 執行CASE:'Video2Image'後輸出  
# └─ video2image_image_paths.txt      # 執行CASE:'ImageAllInOne'後輸出  
# ```
# 5. 執行後資料夾樹狀圖(刪除`help_check_labels`資料夾):
# 
# ```
# ROOT  
# ├─ videos_folder_video2image        # 執行此CASE後，輸出  
# │  ├─ folder1  
# │  │  ├─ video01  
# │  │  │  ├─ video01_img  
# │  │  │  ├─ voc_label               # 執行此CASE後，輸出  
# │  │  │  │  ├─ 000000.xml    
# │  │  │  │  ├─ ..  
# │  │  │  │  └─ 000010.xml  
# │  │  │  ├─ video01.MOV  
# │  │  │  └ video01_path.txt  
# │  │  ├─ ..  
# │  │  └─ videoXX  
# │  │     ├─ videoXX_img  
# │  │     ├─ voc_label               # 執行此CASE後，輸出  
# │  │     │  ├─ 000000.xml  
# │  │     │  ├─ ..  
# │  │     │  └─ 000020.xml  
# │  │     ├─ videoXX.MOV  
# │  │     └ videoXX_path.txt  
# │  ├─ folder2  
# │  │  ├─ video01  
# │  │  ├─ ..  
# │  │  └─ videoXX  
# │  └─ ..  
# ├─ allinone_image_paths.txt         # 執行CASE:'Video2Image'後輸出  
# └─ video2image_image_paths.txt      # 執行CASE:'ImageAllInOne'後輸出  
# ```
# ---
# 
# ### CASE 'Voc2Yolo'
# 
# 說明:
# 1. 將標籤檔VOC格式(`.xml`)轉成YOLO格式(`.txt`)
# 2. 對`video2image`資料夾內每個`voc_label`資料夾的`.xml`檔進行格式轉換，並儲存在`videoXX_img`資料夾內
# 
# ```
# ROOT  
# ├─ videos_folder_video2image  
# │  ├─ folder1  
# │  │  ├─ video01  
# │  │  │  ├─ video01_img  
# │  │  │  │  ├─ 000000.jpg  
# │  │  │  │  ├─ 000000.txt           # 執行此CASE後，輸出  
# │  │  │  │  ├─ 000001.jpg  
# │  │  │  │  ├─ 000002.jpg  
# │  │  │  │  ├─ 000002.txt           # 執行此CASE後，輸出   
# │  │  │  │  ├─ 000003.jpg  
# │  │  │  │  └─ ..  
# │  │  │  ├─ voc_label  
# │  │  │  │  ├─ 000000.xml  
# │  │  │  │  └─ 000002.xml  
# │  │  │  ├─ video01.MOV  
# │  │  │  └ video01_path.txt  
# │  │  └─ ..   
# │  └─ ..  
# ├─ allinone_image_paths.txt         # 執行CASE:'Video2Image'後輸出  
# └─ video2image_image_paths.txt      # 執行CASE:'ImageAllInOne'後輸出  
# ```
# ---
# 
# ### CASE 'CreateNullTxt'
# 
# 說明:
# 1. 建立影像空標籤的`.txt`檔
# 
# ```
# ROOT  
# ├─ videos_folder_video2image  
# │  ├─ folder1  
# │  │  ├─ video01  
# │  │  │  ├─ video01_img  
# │  │  │  │  ├─ 000000.jpg  
# │  │  │  │  ├─ 000000.txt  
# │  │  │  │  ├─ 000001.jpg  
# │  │  │  │  ├─ 000002.jpg  
# │  │  │  │  ├─ 000002.txt           # 執行此CASE後，輸出   
# │  │  │  │  ├─ 000002.txt
# │  │  │  │  ├─ 000003.jpg  
# │  │  │  │  └─ ..  
# │  │  │  ├─ voc_label  
# │  │  │  │  ├─ 000000.xml  
# │  │  │  │  └─ 000002.xml  
# │  │  │  ├─ video01.MOV  
# │  │  │  └ video01_path.txt  
# │  │  └─ ..   
# │  └─ ..  
# ├─ allinone_image_paths.txt         # 執行CASE:'Video2Image'後輸出  
# └─ video2image_image_paths.txt      # 執行CASE:'ImageAllInOne'後輸出  
# ```
# ---
# 

# In[ ]:


import os
import shutil


# In[ ]:


case_list = {'Video2ImageAndAll'    : 0,
             'Yolo2VocAllocateData' : 1,
             'UpdateTransformCreate': 2,
             }

# VARIABLE
isLog = 1
case = case_list['Video2ImageAndAll']
ROOT = 'C:\\Users\\danielwu\\Desktop\\new'
videos_folder = '220407'

## CASE: 'Video2Image'
# Save an image every <interval> frames
interval = 10

## For CASE 'YOLO2VOC', 'Voc2Yolo'
# Dictionary that maps IDs to class names
class_mapping = {'0': 'person',
                 '1': 'cone'}


# In[ ]:


## @brief Description: 取得CMD大小
#  @param None
#  
#  @return col
#  @date 20220318  danielwu
def GetCmdSize():
    import shutil
    col, _ = shutil.get_terminal_size()
    col = col - 21
    return col


# In[ ]:


## @brief Description: 建立資料夾
#  @param folder
#  
#  @return None
#  @date 20220321  danielwu
def MakeDirs(folder):
    if not os.path.isdir(folder):
        os.makedirs(folder)


# In[ ]:


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


# In[ ]:


## @brief Description: 影片轉成影像
#
#  @param [in] video_path  影片路徑
#  @param [in] save_dir    儲存影像之路徑
#  @param [in] interval    幀數間格
#
#  @return None
#  @date  20220318  danielwu 
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
        if ret == True and frame_index % interval == 0:
            cv2.imwrite(os.path.join(save_dir, '{}.jpg'.format(frame_count).zfill(10)), frame)
            frame_count += 1
        frame_index += 1
        
    cap.release()



def StartVideo2Image(ROOT, videos_folder):
    # Get Video Paths from ROOT (Video is .MOV file)
    videos_folder_path = os.path.join(ROOT, videos_folder)
    video_paths = GetPaths(videos_folder_path, extension='.MOV')
    
    if video_paths == []:
        print('There is not any .MOV file in the {}'.format(videos_folder_path))
        print('Please put the video you want to cut into this folder!')
        return

    if isLog:
        print('== Info ' + '='*(col-8))
        print('There are {} videos in dir: {}'.format(len(video_paths), videos_folder_path))
        print('='*col)

    all_image_paths = []
    for video_path in video_paths:
        basename = os.path.basename(video_path)        # videoXX.MOV
        name = os.path.splitext(basename)[0]           # videoXX
        save_path = video_path.replace(videos_folder, '{}_video2image'.format(videos_folder))
        save_path = save_path.replace(basename, name)  # ~\videos_folder_video2image\~\videoXX
        save_images_path = os.path.join(save_path, '{}_img'.format(name))
        MakeDirs(save_images_path)         # ~\videos_folder_video2image\~\videoXX\videoXX_img

        # Cut video, save images and move the original video to the created image folder
        CutVideo(video_path, save_images_path, interval)
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
    txt_file = 'video2image_image_paths.txt'
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


# In[ ]:


def StartImageAllInOne(ROOT, videos_folder):
    info_txt_path = os.path.join(ROOT, 'video2image_image_paths.txt')
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

    # Copy images from video2image folder to all_images folder
    for count, image_path in enumerate(all_image_paths):
        basename = os.path.basename(image_path)
        save_image_path = os.path.join(save_path, '{}.jpg'.format(str(count).zfill(6)))
        shutil.copy(image_path, save_image_path)

    # Create the .txt file and write (new image name: image original path)
    txt_file = 'allinone_image_paths.txt'
    txt_path = os.path.join(ROOT, txt_file)
    with open(txt_path, 'w') as f:
        flag = ''
        f.write('## # <video2image Relative Path>\n')
        f.write('## image basename of all_images: image relative paht of video2image')
        for count, image_path in enumerate(all_image_paths):
            relative_path = image_path.split(ROOT+'\\')[1]
            dirname = os.path.dirname(relative_path)
            if dirname != flag:
                f.write('\n\n# {}'.format(dirname))
                flag = dirname
            f.write('\n{}.jpg : {}'.format(str(count).zfill(6), relative_path))
            count += 1
    
    if isLog:
        print('case: ImageAllInOne done!')


# In[ ]:


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
        CreateFile(image_path, save_folder, file_prefix, w, h, voc_labels)

#     print('Processing complete for file: {}'.format(basename))



def StartYolo2Voc(ROOT, videos_folder):
    check_images_path = os.path.join(ROOT, '{}_check_images'.format(videos_folder))
    yolo_labels_path = os.path.join(ROOT, '{}_all_yolo_labels'.format(videos_folder))
    image_paths = GetPaths(check_images_path, extension='.jpg')
    txt_paths = GetPaths(yolo_labels_path, extension='.txt')
    
    if txt_paths == []:
        print('There is not any .txt file in the {}'.format(yolo_labels_path))
        print('Please manually copy .txt file from yolo detect to this folder!')
        return
    if image_paths == []:
        print('There is not any .jpg file in the {}'.format(check_images_path))
        print('Please manually copy .jpg file from yolo detect to this folder!')
        return

    voc_labels_path = os.path.join(ROOT, '{}_all_voc_labels'.format(videos_folder))
    MakeDirs(voc_labels_path)

    for txt_path in txt_paths:
        # txt_path = '~/video_folder_all_yolo_labels/xxxxxx.txt'
        # image_path = '~/video_folder_check_images/xxxxxx.jpg'
        image_path = txt_path.replace('all_yolo_labels', 'check_images')
        image_path = image_path.replace('.txt', '.jpg')

        Yolo2Voc(txt_path, image_path, voc_labels_path)
    
    if isLog:
        print('case: Yolo2Voc done!')


# In[ ]:


def StartAllocateData(ROOT, videos_folder):
    check_images_path = os.path.join(ROOT, '{}_check_images'.format(videos_folder))
    help_check_path = os.path.join(ROOT, '{}_help_check_labels'.format(videos_folder))
    voc_labels_path = os.path.join(ROOT, '{}_all_voc_labels'.format(videos_folder))
    yolo_labels_path = os.path.join(ROOT, '{}_all_yolo_labels'.format(videos_folder))
    image_paths = GetPaths(check_images_path, extension='.jpg')
    
    for count, image_path in enumerate(image_paths):
        folder_idx = count // 2000                          # 一個資料夾2000筆資料
        save_image = os.path.join(help_check_path, str(folder_idx), 'image')
        save_label = os.path.join(help_check_path, str(folder_idx), 'labels')
        for f in [save_image, save_label]:
            MakeDirs(f)
        
        label_path = image_path.replace('check_images', 'all_voc_labels')
        label_path = label_path.replace('.jpg', '.xml')
        
        # Move Original Image To New Folder
        shutil.move(image_path, save_image)
        # Move Original Label To New Folder
        if os.path.isfile(label_path):
            shutil.move(label_path, save_label)
    
    # Remove check_images and all_voc_labels folder (they are empty folders)
    shutil.rmtree(check_images_path)
    shutil.rmtree(voc_labels_path)
    # Remove old .txt files (using yolo to auto labeling)
    shutil.rmtree(yolo_labels_path)
    
    if isLog:
        print('Remove {} folder'.format(os.path.basename(check_images_path)))
        print('Remove {} folder'.format(os.path.basename(voc_labels_path)))
        print('Remove {} folder'.format(os.path.basename(yolo_labels_path)))
        print('='*col)
        print('case: AllocateData done!')


# In[ ]:


def StartUpdateLabels(ROOT, videos_folder):
    help_check_path = os.path.join(ROOT, '{}_help_check_labels'.format(videos_folder))
    info_txt_path = os.path.join(ROOT, 'allinone_image_paths.txt')
    
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
    
    for xml_path in xml_paths:
        basename = os.path.basename(xml_path)      # xxxxxx.xml
        prefix_basename = basename.split('.')[0]   # xxxxxx
        
        # Using path of .xml file to get original image relative path
        # relative_path = '~/videoXX/videoXX_img/xxxxxx.jpg'
        # split_relative_path = [~, videoXX, videoXX_img, xxxxxx.jpg]
        # save_basename = 'xxxxxx.xml'
        split_relative_path = relative_path[prefix_basename].split('\\')
        save_basename = split_relative_path[-1].split('.')[0] + '.xml'
        
        # Update saving .xml file folder path and create the folder
        save_path = ROOT
        for path in split_relative_path[:-2]:
            save_path = os.path.join(save_path, path)
        save_path = os.path.join(save_path, 'voc_label')
        MakeDirs(save_path)
        save_path = os.path.join(save_path, save_basename)
        
        # Cut .xml file from help_check_labels folder to video2image folder
        shutil.move(xml_path, save_path)

    # Remove help_check_labels folder (the folder is for staged mission)
    shutil.rmtree(help_check_path)
        
    if isLog:
        print('Remove {} folder'.format(os.path.basename(help_check_path)))
        print('='*col)
        print('case: UpdateLabels done!')


# In[ ]:


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
def Voc2Yolo(info_dict, txt_path):
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
    print("\n".join(print_buffer), end='', file= open(txt_path, "w"))



# Start voc to yolo (for .xml to .txt: final)
def StartVoc2Yolo(ROOT, videos_folder):
    video2image_path = os.path.join(ROOT, '{}_video2image'.format(videos_folder))
    
    # Get .xml file paths from video2image folder
    xml_paths = GetPaths(video2image_path, extension='.xml')
    
    for xml_path in xml_paths:
        # Read .xml information
        info_dict = ExtractInfoFromXml(xml_path)
        
        # Convert xml path to save txt path
        # xml_path = '~\videoXX\voc_label\xxxxxx.xml'
        # split_xml_path = [~, videoXX, voc_label, xxxxxx.xml]
        # save_basename = xxxxxx.txt
        # save_path = '~\videoXX\videoXX_img\xxxxxx.txt'
        split_xml_path = xml_path.split('\\')
        save_basename = split_xml_path[-1].replace('.xml', '.txt')
        
        # Update saving .txt file folder path and create the folder
        save_path = ''
        for path in split_xml_path[:-2]:
            save_path = os.path.join(save_path, path)
        save_path = os.path.join(save_path, split_xml_path[-3] + '_img', save_basename)
        
        # Save annotation
        Voc2Yolo(info_dict, save_path)
    
    if isLog:
        print('case: Voc2Yolo done!')


# In[ ]:


def StartCreateNullTxt(ROOT, videos_folder):
    info_txt_path = os.path.join(ROOT, 'video2image_image_paths.txt')
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
        if all_image_paths != []:
            if isLog:
                print('Get image paths from the {}'.format(info_txt_path))
    if not os.path.isfile(info_txt_path) or all_image_paths == []:
        # Get all image paths from the video2image folder using func. GetPaths():
        all_image_paths = GetPaths(video2image_path, extension='.jpg')
        if all_image_paths != []:
            if isLog:
                print('Get image paths from video2image folder using func. GetPaths()')
        else:
            print('There is empty in the {}'.format(info_txt_path))
            print('There is not any .jpg file in the {}'.format(video2image_path))
            print('Error: Can not do the case: "CreateNullTxt"!')
            return
        
    # Create null txt file
    for image_path in all_image_paths:        
        # Convert image path to yolo label path
        label_path = image_path.split('.')[0] + '.txt'
        
        # Create null txt file
        if not os.path.isfile(label_path):
            print('', end= '', file= open(label_path, 'w'))
    
    if isLog:
        print('case: StartCreateNullTxt done!')


# In[ ]:


if __name__ == '__main__':
    if isLog:
        col = GetCmdSize()
    
    # Case: Video2ImageAndAll
    if case == 0:
        import cv2
        
        StartVideo2Image(ROOT, videos_folder)
        StartImageAllInOne(ROOT, videos_folder)        
    
    # Case: Yolo2VocAllocateData
    if case == 1:
        from PIL import Image
        from math import floor
        import xml.etree.ElementTree as ET
        
        StartYolo2Voc(ROOT, videos_folder)
        StartAllocateData(ROOT, videos_folder)
        
        # Remove all_images folder if it exist
        all_images = os.path.join(ROOT, '{}_all_images'.format(videos_folder))
        if os.path.exists(all_images):
            shutil.rmtree(all_images)
            if isLog:
                print('Remove {} folder'.format(os.path.basename(all_images)))
        
        # Save labels name
        labels_name = os.path.join(ROOT, 'labels.name')
        with open(labels_name, 'w') as f:
            for name in class_mapping.values():
                f.write(name + '\n')
    
    # Case: UpdateTransformCreate
    if case == 2:
        import xml.etree.ElementTree as ET
        
        StartUpdateLabels(ROOT, videos_folder)
        StartVoc2Yolo(ROOT, videos_folder)
        StartCreateNullTxt(ROOT, videos_folder)

