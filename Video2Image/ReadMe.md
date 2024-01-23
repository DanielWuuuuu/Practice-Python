# 影片轉圖片

### args:
1. `IS_LOG`        : Show log or not
2. `case`          : Please refer case_list
3. `ROOT`          : root
4. `videos_folder` : Parent video folder name
5. `INTERVAL`      : How many frame intervals will save an image
6. `CUT_METHOD`    : Please refer cut_method_list
7. `FILE_EXT`      : File extension
8. `SIMILARITY_THRESHOLD` : Threshold about the similarity between the current frame and the next frame
9. `IS_RESIZE`      : Whether to resize the image to a custom size
10. `IS_KEEP_RATIO` : Whether to keep the original aspect ratio when resizing the image
11. `IS_BORDER`     : Whether to fill black border if the image is not square
12. `IMAGE_SIZE`    : New image size (if IS_BORDER == True: HxH, else: WxH, if IS_KEEP_RATIO == False: MxN)
13. `IS_SOUND`      : Video with sound or not
14. `MEMBERS`       : How many datas in per folder
15. `CLASS_MAPPING` : Index corresponds to the label name

*NOTE*  `ROOT`不可以含有此關鍵字:`images`!

---
<a name='FlowChart'></a>
### 流程

1. 執行CASE:['video2image_and_all'](#video2image_and_all) :  
   (1) 將`videos_folder`資料夾內所有影片切成影像，輸出至`video2image`資料夾  
   (2) 將切片的影像複製一份至`all_images`資料夾內，待自動標籤用  <br><br>

2. 另外執行YOLOv5  
   `!python detect.py --weights best.pt --source path/ --conf-thres 0.5 --save-txt --project save/to/path/ --name xxx --line-thickness 1 --hide-labels`  
   (1) 將`save/to/path/xxx/labels`手動複製至`ROOT/{videos_folder}_auto_labeled_labels`  
   (2) 將`save/to/path/xxx`內之影像手動複製至`ROOT/{videos_folder}_auto_labeled_images`  <br><br>

3. 執行CASE:['yolo2voc_and_allocate'](#yolo2voc_and_allocate) :  
   (1) 將`auto_labeled_labels`資料夾內`txt`檔轉成`xml`檔至`all_voc_labels`資料夾內  
   (2) 將`auto_labeled_images`(對應`all_voc_labels`)每`{MEMBERS}`筆分配在一個資料夾，母資料夾為`help_check_labels`，接著就可以請同仁幫忙檢查自動標籤是否有誤，使用Labelimg等開源軟體修正`xml`檔內類別座標資訊  
   (3) 將建立`help_check_labels`資料夾，並刪除`all_images`資料夾、`auto_labeled_images`資料夾、`auto_labeled_labels`資料夾與`all_voc_labels`資料夾  <br><br>

4. 另外手動將檢查完的`xml`檔(母資料夾為`help_check_labels`)覆蓋至原始的`help_check_labels`資料夾  

5. 執行CASE:['update_and_transform_and_null'](#update_and_transform_and_null) :  
   (1) 將更新後的`xml`檔移至`video2image/videoXX/voc_labels`資料夾內  
   (2) 將`voc_labels`資料夾內`xml`檔轉成`txt`檔並分別儲存至`images`資料夾內及`labels`資料夾內  
   (3) 建立影像空標籤的`txt`檔  

---
### 影片資料夾樹狀圖:

說明:
1. 資料夾可為多階層 ( 以下為範例 ):

```
ROOT  
└─ videos_folder  
   ├─ folder1  
   │  ├─ video01.MOV  
   │  ├─ video02.MOV  
   │  └─ ..  
   ├─ folder2  
   │  ├─ video01.MOV  
   │  ├─ video02.MOV  
   │  └─ ..  
   └─ ..  
```
---
<a name='video2image_and_all'></a>
### CASE:'video2image_and_all'

說明:
1. 依序執行CASE:['run_video2image'](#run_video2image)與CASE:['run_image_in_one_folder'](#run_image_in_one_folder)  

[(回流程)](#FlowChart)

---
<a name='yolo2voc_and_allocate'></a>
### CASE:'yolo2voc_and_allocate'

說明:
1. 前置作業請參考CASE:['run_yolo2voc_format'](#run_yolo2voc_format)第1、2點說明
2. 依序執行CASE:['run_yolo2voc_format'](#run_yolo2voc_format)與CASE:['run_allocate_data'](#run_allocate_data)
3. 將刪除`all_images`資料夾

[(回流程)](#FlowChart)

---
<a name='update_and_transform_and_null'></a>
### CASE:'update_and_transform_and_null'

說明:
1. 依序執行CASE:['run_update_labels'](#run_update_labels)、CASE:['run_voc2yolo_format'](#run_voc2yolo_format)與CASE:['run_create_null_label_file'](#run_create_null_label_file)

[(回流程)](#FlowChart)

---
<a name='run_video2image'></a>
### CASE:'run_video2image'

說明:
1. 影片切成影像
2. 輸出影像資料夾樹狀圖 ( 階層會與來源相同 ):

```
ROOT  
├─ {videos_folder}                # 原始影片，執行此CASE後，刪除此資料夾!  
├─ {videos_folder}_video2image    # 執行此CASE後，輸出  
│  ├─ folder1  
│  │  ├─ video01  
│  │  │  ├─ images                # 影片 > 影像儲存資料夾  
│  │  │  │  ├─ 000000.jpg  
│  │  │  │  ├─ ..  
│  │  │  │  └─ 000010.jpg  
│  │  │  ├─ video01.{original_ext} # 「搬移」原始影片，或移除聲音的影片  
│  │  │  └ video01_path.txt        # 當下影像絕對路徑  
│  │  ├─ ..  
│  │  └─ videoXX  
│  │     ├─ images  
│  │     │  ├─ 000000.jpg  
│  │     │  ├─ ..  
│  │     │  └─ 000020.jpg  
│  │     ├─ videoXX.{original_ext}  
│  │     └ videoXX_path.txt  
│  ├─ folder2  
│  │  ├─ video01  
│  │  ├─ ..  
│  │  └─ videoXX  
│  └─ ..  
└ {videos_folder}_video2image_image_paths.txt  # 執行此CASE後，輸出  
```
3. `video2image_image_paths.txt`為儲存切片後各影像的路徑

[(回CASE:'video2image_and_all')](#video2image_and_all)

---
<a name='run_image_in_one_folder'></a>
### CASE:'run_image_in_one_folder'

說明:
1. 將在各個資料夾內的影像複製出來放在`all_images`資料夾內 ( YOLO自動標籤用 )
2. 輸出影像資料夾樹狀圖 ( 輸出的影像序號會接續下去 ):

```
ROOT  
├─ {videos_folder}_all_images   # 執行此CASE後，輸出  
│  ├─ 000000.jpg  
│  ├─ ..  
│  └─ xxxxxx.jpg  
├─ {videos_folder}_video2image  # 執行CASE:'run_video2image'後輸出  
├─ {videos_folder}_allinone_image_paths.txt     # 執行此CASE後，輸出 ( 如第3點範例 )  
└─ {videos_folder}_video2image_image_paths.txt  # 執行CASE:'run_video2image'後輸出  
```
3. `allinone_image_paths.txt`資訊如下:

```
## # <video2image Relative Path>
## image basename of all_images: image relative paht of video2image

# folder1/video01/images
000000.jpg : folder1/video01/images/000000.jpg
..
000010.jpg : folder1/video01/images/000010.jpg

# folder1/videoXX/images
000011.jpg : folder1/videoXX/images/000000.jpg
..
000031.jpg : folder1/videoXX/images/000020.jpg
..
```

[(回CASE:'video2image_and_all')](#video2image_and_all)

---
<a name='run_yolo2voc_format'></a>
### CASE:'run_yolo2voc_format'

說明:
1. 將`auto_labeled_labels`資料夾內`txt`檔轉成`xml`檔至`all_voc_labels`資料夾內
2. 先執行YOLO v5 detect.py:
   `!python detect.py --weights best.pt --source path/ --conf-thres 0.5 --save-txt --project save/to/path/ --name xxx --line-thickness 1 --hide-labels`  
   (1) 將`save/to/path/xxx/labels`手動複製至`ROOT/{videos_folder}_auto_labeled_labels`  
   (2) 將`save/to/path/xxx`內之影像手動複製至`ROOT/{videos_folder}_auto_labeled_images`  
3. 執行完YOLOv5 detect.py後，再執行此CASE  
   = ============================ **注 意** ============================ =  
   (1) 若未執行「自動標籤」，即`auto_labeled_images`與`auto_labeled_labels`資料夾都沒有的情況下，則不會執行此CASE  
   (2) 若只有`auto_labeled_images`資料夾，沒有`auto_labeled_labels`資料夾，則不會執行此CASE  
   (3) 若只有`auto_labeled_labels`資料夾，但是裡面沒有任何`txt`檔案，則不會執行此CASE  
   = =============================================================== =  
4. 輸出標籤資料夾樹狀圖:

```
ROOT  
├─ {videos_folder}_auto_labeled_voc_labels # 執行此CASE後，輸出  
│  ├─ 000000.xml  
│  ├─ ..  
│  └─ xxxxxx.xml  
├─ {videos_folder}_auto_labeled_labels     # 手動將YOLO偵測物件輸出的txt檔放入此資料夾  
│  ├─ 000000.txt  
│  ├─ ..  
│  └─ xxxxxx.txt  
├─ {videos_folder}_auto_labeled_images     # 手動將YOLO偵測物件輸出的pg檔放入此資料夾  
│  ├─ 000000.jpg  
│  ├─ ..  
│  └─ xxxxxx.jpg  
├─ {videos_folder}_all_images       # 執行CASE:'run_image_in_one_folder'後輸出  
├─ {videos_folder}_video2image      # 執行CASE:'run_video2image'後輸出  
├─ {videos_folder}_allinone_image_paths.txt    # 執行CASE:'run_image_in_one_folder'後輸出  
└─ {videos_folder}_video2image_image_paths.txt # 執行CASE:'run_video2image'後輸出  
```

[(回CASE:'yolo2voc_and_allocate')](#yolo2voc_and_allocate)

---
<a name='run_allocate_data'></a>
### CASE:'run_allocate_data'

說明:
1. 將`auto_labeled_images`資料夾內影像及`all_voc_labels`資料夾內標籤檔按比例重新分配  
   每`{MEMBERS}`個檔案放在一個資料夾，接著就可以請同仁們幫忙檢查自動標籤是否有誤，並手動修正  
   = ============================ **注 意** ============================ =  
   若沒有`auto_labeled_images`資料夾，則將使用`all_images`資料夾 
   = =============================================================== =  
2. 執行後將刪除`all_images`資料夾、`all_voc_labels`資料夾、`auto_labeled_labels`資料夾及`auto_labeled_images`資料夾
3. 分配資料夾樹狀圖:

```
ROOT  
├─ {videos_folder}_all_images              # 執行此CASE後，刪除此資料夾!  
├─ {videos_folder}_auto_labeled_voc_labels # 執行此CASE後，刪除此資料夾!  
├─ {videos_folder}_auto_labeled_labels     # 執行此CASE後，刪除此資料夾!  
├─ {videos_folder}_auto_labeled_images     # 執行此CASE後，刪除此資料夾!  
├─ {videos_folder}_help_check_labels  # 執行此CASE後，輸出  
│  ├─ 0  
│  │  ├─ images  
│  │  │  ├─ 000000.jpg  
│  │  │  ├─ ..  
│  │  │  └─ 001999.jpg  
│  │  └─ labels  
│  │     ├─ 000000.xml  
│  │     ├─ ..  
│  │     └─ 001999.xml  
│  ├─ 1  
│  │  ├─ images  
│  │  │  ├─ 002000.jpg  
│  │  │  ├─ ..  
│  │  │  └─ 003999.jpg  
│  │  └─ labels  
│  │     ├─ 002000.xml  
│  │     ├─ ..  
│  │     └─ 003999.xml  
│  └─ ..  
├─ {videos_folder}_video2image                 # 執行CASE:'run_video2image'後輸出  
├─ {videos_folder}_allinone_image_paths.txt    # 執行CASE:'run_image_in_one_folder'後輸出  
└─ {videos_folder}_video2image_image_paths.txt # 執行CASE:'run_video2image'後輸出  
```

[(回CASE:'yolo2voc_and_allocate')](#yolo2voc_and_allocate)

---
<a name='run_update_labels'></a>
### CASE:'run_update_labels'

說明:
1. 更新自動標籤檔: 將各個資料夾內檢查好的`xml`檔放回`video2image`資料夾
2. 同仁們檢查好標籤後，請同仁們回傳整個`help_check_labels`資料夾(子資料夾`images`可不用回傳)
3. 將回傳的`help_check_labels`資料夾覆蓋至自己原本的`help_check_labels`資料夾 
   ( 更新標籤檔: 檔案已存在 => 勾選 全部取代 或 將原本的標籤檔全部刪除再貼上檢查後的標籤檔 )
4. 執行前資料夾樹狀圖:

```
ROOT  
├─ {videos_folder}_help_check_labels  # 手動將檢查好的labels資料夾覆蓋回來  
├─ {videos_folder}_video2image        # 執行CASE:'run_video2image'後輸出  
├─ {videos_folder}_allinone_image_paths.txt    # 執行CASE:'run_image_in_one_folder'後輸出  
└─ {videos_folder}_video2image_image_paths.txt # 執行CASE:'run_video2image'後輸出  
```
5. 執行後資料夾樹狀圖(刪除`help_check_labels`資料夾):

```
ROOT  
├─ {videos_folder}_video2image  
│  ├─ folder1  
│  │  ├─ video01  
│  │  │  ├─ images  
│  │  │  ├─ voc_labels              # 執行此CASE後，輸出  
│  │  │  │  ├─ 000000.xml    
│  │  │  │  ├─ ..  
│  │  │  │  └─ 000010.xml  
│  │  │  ├─ video01.{original_ext}  
│  │  │  └ video01_path.txt  
│  │  ├─ ..  
│  │  └─ videoXX  
│  │     ├─ images  
│  │     ├─ voc_labels              # 執行此CASE後，輸出  
│  │     │  ├─ 000000.xml  
│  │     │  ├─ ..  
│  │     │  └─ 000020.xml  
│  │     ├─ videoXX.{original_ext}  
│  │     └ videoXX_path.txt  
│  ├─ folder2  
│  │  ├─ video01  
│  │  ├─ ..  
│  │  └─ videoXX  
│  └─ ..  
├─ {videos_folder}_allinone_image_paths.txt    # 執行CASE:'run_image_in_one_folder'後輸出  
└─ {videos_folder}_video2image_image_paths.txt # 執行CASE:'run_video2image'後輸出  
```

[(回CASE:'update_and_transform_and_null')](#update_and_transform_and_null)

---
<a name='run_voc2yolo_format'></a>
### CASE:'run_voc2yolo_format'

說明:
1. 將標籤檔VOC格式(`xml`)轉成YOLO格式(`txt`)
2. 對`video2image`資料夾內每個`voc_labels`資料夾的`xml`檔進行格式轉換，並儲存在`images`資料夾內及`labels`資料夾內

```
ROOT  
├─ {videos_folder}_video2image  
│  ├─ folder1  
│  │  ├─ video01  
│  │  │  ├─ images  
│  │  │  │  ├─ 000000.jpg  
│  │  │  │  ├─ 000000.txt           # 執行此CASE後，輸出  
│  │  │  │  ├─ 000001.jpg  
│  │  │  │  ├─ 000002.jpg  
│  │  │  │  ├─ 000002.txt           # 執行此CASE後，輸出  
│  │  │  │  ├─ 000003.jpg  
│  │  │  │  └─ ..  
│  │  │  ├─ labels  
│  │  │  │  ├─ 000000.txt           # 執行此CASE後，輸出  
│  │  │  │  ├─ 000002.txt           # 執行此CASE後，輸出  
│  │  │  │  └─ ..  
│  │  │  ├─ voc_labels  
│  │  │  │  ├─ 000000.xml  
│  │  │  │  └─ 000002.xml  
│  │  │  ├─ video01.{original_ext}  
│  │  │  └ video01_path.txt  
│  │  └─ ..   
│  └─ ..  
├─ {videos_folder}_allinone_image_paths.txt         # 執行CASE:'run_image_in_one_folder'後輸出  
└─ {videos_folder}_video2image_image_paths.txt      # 執行CASE:'run_video2image'後輸出  
```

[(回CASE:'update_and_transform_and_null')](#update_and_transform_and_null)

---
<a name='run_create_null_label_file'></a>
### CASE:'run_create_null_label_file'

說明:
1. 建立影像空標籤的`txt`檔

```
ROOT  
├─ {videos_folder}_video2image  
│  ├─ folder1  
│  │  ├─ video01  
│  │  │  ├─ images  
│  │  │  │  ├─ 000000.jpg  
│  │  │  │  ├─ 000000.txt  
│  │  │  │  ├─ 000001.jpg  
│  │  │  │  ├─ 000001.txt           # 執行此CASE後，輸出  
│  │  │  │  ├─ 000002.jpg  
│  │  │  │  ├─ 000002.txt  
│  │  │  │  ├─ 000003.jpg  
│  │  │  │  └─ ..  
│  │  │  ├─ labels  
│  │  │  │  ├─ 000000.txt  
│  │  │  │  ├─ 000001.txt           # 執行此CASE後，輸出  
│  │  │  │  ├─ 000002.txt  
│  │  │  │  └─ ..  
│  │  │  ├─ voc_labels  
│  │  │  │  ├─ 000000.xml  
│  │  │  │  └─ 000002.xml  
│  │  │  ├─ video01.{original_ext}  
│  │  │  └ video01_path.txt  
│  │  └─ ..   
│  └─ ..  
├─ {videos_folder}_allinone_image_paths.txt         # 執行CASE:'run_image_in_one_folder'後輸出  
└─ {videos_folder}_video2image_image_paths.txt      # 執行CASE:'run_video2image'後輸出  
```

[(回CASE:'update_and_transform_and_null')](#update_and_transform_and_null)

---
