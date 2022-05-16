# 影片轉圖片

### args:

1. `isLog`         : 是否顯示log

2. `case`          : 功能選擇 ( 參考 case_list )

3. `ROOT`          : 根目錄 (包含原始影片資料夾、創建影像資料夾等)

4. `videos_folder` : 影片母資料夾路徑

5. `interval`      : 幀數間格 (每幾幀擷取一張影像)
   
   ```python
   case_list = {'Video2ImageAndAll'    : 0,
                'Yolo2VocAllocateData' : 1,
                'UpdateTransformCreate': 2,
                }
   ```

### 流程

1. 執行CASE 'Video2ImageAndAll'  
   (1) 將`videos_folder`資料夾內所有影片切成影像，輸出至`video2image`資料夾  
   (2) 將切片的影像複製一份至`all_images`資料夾內，待自動標籤用  

2. 另外執行YOLO v5  
   `!python detect.py --weights best.pt --source path/*.jpg --save-txt path/*.txt`  
   (1) 將`yolov5/runs/detect/expXX/labels`手動複製至`ROOT/videos_folder_all_yolo_labels`  
   (2) 將`yolov5/runs/detect/expXX`內之影像手動複製至`ROOT/videos_folder_check_images`  

3. 執行CASE 'Yolo2VocAllocateData':  
   (1) 將`all_yolo_labels`資料夾內`.txt`檔轉成`.xml`檔至`all_voc_labels`資料夾內  
   (2) 將`check_images`(對應`all_voc_labels`)每2000筆分配在一個資料夾，母資料夾為`help_check_labels`，接著就可以請同仁幫忙檢查自動標籤是否有誤，並手動修正`.xml`檔內類別座標資訊  
   (3) 將刪除`all_images`、`check_images`資料夾與`all_voc_labels`資料夾  

4. 執行CASE 'UpdateTransformCreate':  
   (1) 將檢查完的`.xml`檔(母資料夾為`help_check_labels`)更新回`video2image/videoXX/voc_label`資料夾內  
   (2) 將`voc_label`資料夾內`.xml`檔轉成`.txt`檔至`videoXX_img`資料夾內  
   (3) 建立影像空標籤的`.txt`檔  

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

### CASE 'Video2ImageAndAll'

說明:

1. 依序執行CASE:Video2Image與CASE:ImageAllInOne

---

### CASE 'Yolo2VocAllocateData'

說明:

1. 前置作業請參考CASE:'Yolo2Voc'第1、2點說明
2. 依序執行CASE:Yolo2Voc與CASE:AllocateData
3. 額外刪除`all_images`資料夾

---

### CASE 'UpdateTransformCreate'

說明:

1. 依序執行CASE:UpdateLabels、CASE:Voc2Yolo與CASE:CreateNullTxt

---

### 各CASE說明:

---

### CASE: 'Video2Image'

說明:

1. 影片切成影像
2. 輸出影像資料夾樹狀圖 ( 階層會與來源相同 ):

```
ROOT  
├─ videos_folder              # 原始影片  
│                             # 執行此CASE後，刪除此資料夾!  
├─ videos_folder_video2image  # 執行此CASE後，輸出  
│  ├─ folder1  
│  │  ├─ video01  
│  │  │  ├─ video01_img       # 影片 > 影像儲存資料夾  
│  │  │  │  ├─ 000000.jpg  
│  │  │  │  ├─ ..  
│  │  │  │  └─ 000010.jpg  
│  │  │  ├─ video01.MOV        # 「搬移」原始影片
│  │  │  └ video01_path.txt    # 影像絕對路徑
│  │  ├─ ..  
│  │  └─ videoXX  
│  │     ├─ videoXX_img  
│  │     │  ├─ 000000.jpg  
│  │     │  ├─ ..  
│  │     │  └─ 000020.jpg  
│  │     ├─ videoXX.MOV  
│  │     └ videoXX_path.txt  
│  ├─ folder2  
│  │  ├─ video01  
│  │  ├─ ..  
│  │  └─ videoXX  
│  └─ ..  
└ video2image_image_paths.txt  # 執行此CASE後，輸出  
```

3. video2image_image_paths.txt為儲存切片後各影像的路徑

---

### CASE 'ImageAllInOne'

說明:

1. 將在各個資料夾內的影像複製出來放在`all_images`資料夾內 ( YOLO自動標籤用 )
2. 輸出影像資料夾樹狀圖 ( 輸出的影像序號會接續下去 ):

```
ROOT  
├─ videos_folder_all_images     # 執行此CASE後，輸出  
│  ├─ 000000.jpg  
│  ├─ ..  
│  └─ xxxxxx.jpg  
├─ videos_folder_video2image    # 執行CASE:'Video2Image'後輸出  
├─ allinone_image_paths.txt     # 執行此CASE後，輸出 ( 如第4點範例 )  
└─ video2image_image_paths.txt  # 執行CASE:'Video2Image'後輸出  
```

3. allinone_image_paths.txt資訊如下:

```
## # <video2image Relative Path>\n')
## image basename of all_images: image relative paht of video2image

# folder1/video01/video01_img
000000.jpg : folder1/video01/video01_img/000000.jpg
..
000010.jpg : folder1/video01/video01_img/000010.jpg

# folder1/videoXX/videoXX_img
000011.jpg : folder1/videoXX/videoXX_img/000000.jpg
..
000031.jpg : folder1/videoXX/videoXX_img/000020.jpg
..
```

---

### CASE 'Yolo2Voc'

說明:

1. 將`all_yolo_labels`資料夾內`.txt`檔轉成`.xml`檔至`all_voc_labels`資料夾內
2. 先執行YOLO v5 detect.py:
   `python detect.py --weights best.pt --source path/*.jpg --save-txt`
   (1) 將`yolov5/runs/detect/expXX/labels`手動複製至`ROOT/videos_folder_all_yolo_labels`
   (2) 將`yolov5/runs/detect/expXX`內之影像手動複製至`ROOT/videos_folder_check_images`
3. 執行完YOLO v5 detect.py後，在執行此CASE
4. 輸出標籤資料夾樹狀圖:

```
ROOT  
├─ videos_folder_all_voc_labels   # 執行此CASE後，輸出  
│  ├─ 000000.xml  
│  ├─ ..  
│  └─ xxxxxx.xml  
├─ videos_folder_all_yolo_labels  # 手動將YOLO偵測物件輸出的.txt檔放入此資料夾  
│  ├─ 000000.txt  
│  ├─ ..  
│  └─ xxxxxx.txt  
├─ videos_folder_check_images     # 手動將YOLO偵測物件輸出的.jpg檔放入此資料夾  
│  ├─ 000000.jpg  
│  ├─ ..  
│  └─ xxxxxx.jpg  
├─ videos_folder_video2image      # 執行CASE:'Video2Image'後輸出  
├─ allinone_image_paths.txt       # 執行CASE:'ImageAllInOne'後輸出  
└─ video2image_image_paths.txt    # 執行CASE:'Video2Image'後輸出  
```

---

### CASE 'AllocateData'

說明:

1. 將`check_images`資料夾內影像及`all_voc_labels`資料夾內標籤檔按比例重新分配，
   每2000個檔案放在一個資料夾，接著就可以請同仁們幫忙檢查自動標籤是否有誤，並手動修正
2. 執行後將刪除`all_voc_labels`資料夾與`check_images`資料夾
3. 分配資料夾樹狀圖:

```
ROOT  
├─ videos_folder_all_yolo_labels    # 執行此CASE後，刪除此資料夾!  
├─ videos_folder_help_check_labels  # 執行此CASE後，輸出  
│  ├─ 0  
│  │  ├─ images  
│  │  │  ├─ 000000.jpg  
│  │  │  ├─ ..  
│  │  │  └─ 001999.jpg  
│  │  └─ labels  
│  │  │  ├─ 000000.xml  
│  │  │  ├─ ..  
│  │  │  └─ 001999.xml  
│  ├─ 1  
│  │  ├─ images  
│  │  │  ├─ 002000.jpg  
│  │  │  ├─ ..  
│  │  │  └─ 003999.jpg  
│  │  └─ labels  
│  │     ├─ 002000.jpg  
│  │     ├─ ..  
│  │     └─ 003999.jpg  
│  └─ ..  
├─ videos_folder_video2image        # 執行CASE:'Video2Image'後輸出  
├─ allinone_image_paths.txt         # 執行CASE:'Video2Image'後輸出  
└─ video2image_image_paths.txt      # 執行CASE:'ImageAllInOne'後輸出  
```

---

### CASE 'UpdateLabels'

說明:

1. 更新自動標籤檔: 將各個資料夾內檢查好的`.xml`檔放回`video2image`資料夾
2. 同仁們檢查好標籤後，請同仁們回傳整個`help_check_labels`資料夾(子資料夾`images`可不用回傳)
3. 將回傳的`help_check_labels`資料夾覆蓋回自己原本的`help_check_labels`資料夾 
   ( 更新標籤檔: 檔案已存在 => 勾選 全部取代 )
4. 執行前資料夾樹狀圖:

```
ROOT  
├─ videos_folder_all_images         # 執行CASE:'ImageAllInOne'後輸出  
├─ videos_folder_help_check_labels  # 手動將檢查好的help_check_labels資料夾覆蓋回來  
├─ videos_folder_video2image        # 執行CASE:'Video2Image'後輸出  
├─ allinone_image_paths.txt         # 執行CASE:'Video2Image'後輸出  
└─ video2image_image_paths.txt      # 執行CASE:'ImageAllInOne'後輸出  
```

5. 執行後資料夾樹狀圖(刪除`help_check_labels`資料夾):

```
ROOT  
├─ videos_folder_video2image        # 執行此CASE後，輸出  
│  ├─ folder1  
│  │  ├─ video01  
│  │  │  ├─ video01_img  
│  │  │  ├─ voc_label               # 執行此CASE後，輸出  
│  │  │  │  ├─ 000000.xml    
│  │  │  │  ├─ ..  
│  │  │  │  └─ 000010.xml  
│  │  │  ├─ video01.MOV  
│  │  │  └ video01_path.txt  
│  │  ├─ ..  
│  │  └─ videoXX  
│  │     ├─ videoXX_img  
│  │     ├─ voc_label               # 執行此CASE後，輸出  
│  │     │  ├─ 000000.xml  
│  │     │  ├─ ..  
│  │     │  └─ 000020.xml  
│  │     ├─ videoXX.MOV  
│  │     └ videoXX_path.txt  
│  ├─ folder2  
│  │  ├─ video01  
│  │  ├─ ..  
│  │  └─ videoXX  
│  └─ ..  
├─ allinone_image_paths.txt         # 執行CASE:'Video2Image'後輸出  
└─ video2image_image_paths.txt      # 執行CASE:'ImageAllInOne'後輸出  
```

---

### CASE 'Voc2Yolo'

說明:

1. 將標籤檔VOC格式(`.xml`)轉成YOLO格式(`.txt`)
2. 對`video2image`資料夾內每個`voc_label`資料夾的`.xml`檔進行格式轉換，並儲存在`videoXX_img`資料夾內

```
ROOT  
├─ videos_folder_video2image  
│  ├─ folder1  
│  │  ├─ video01  
│  │  │  ├─ video01_img  
│  │  │  │  ├─ 000000.jpg  
│  │  │  │  ├─ 000000.txt           # 執行此CASE後，輸出  
│  │  │  │  ├─ 000001.jpg  
│  │  │  │  ├─ 000002.jpg  
│  │  │  │  ├─ 000002.txt           # 執行此CASE後，輸出   
│  │  │  │  ├─ 000003.jpg  
│  │  │  │  └─ ..  
│  │  │  ├─ voc_label  
│  │  │  │  ├─ 000000.xml  
│  │  │  │  └─ 000002.xml  
│  │  │  ├─ video01.MOV  
│  │  │  └ video01_path.txt  
│  │  └─ ..   
│  └─ ..  
├─ allinone_image_paths.txt         # 執行CASE:'Video2Image'後輸出  
└─ video2image_image_paths.txt      # 執行CASE:'ImageAllInOne'後輸出  
```

---

### CASE 'CreateNullTxt'

說明:

1. 建立影像空標籤的`.txt`檔

```
ROOT  
├─ videos_folder_video2image  
│  ├─ folder1  
│  │  ├─ video01  
│  │  │  ├─ video01_img  
│  │  │  │  ├─ 000000.jpg  
│  │  │  │  ├─ 000000.txt  
│  │  │  │  ├─ 000001.jpg  
│  │  │  │  ├─ 000002.jpg  
│  │  │  │  ├─ 000002.txt           # 執行此CASE後，輸出   
│  │  │  │  ├─ 000002.txt
│  │  │  │  ├─ 000003.jpg  
│  │  │  │  └─ ..  
│  │  │  ├─ voc_label  
│  │  │  │  ├─ 000000.xml  
│  │  │  │  └─ 000002.xml  
│  │  │  ├─ video01.MOV  
│  │  │  └ video01_path.txt  
│  │  └─ ..   
│  └─ ..  
├─ allinone_image_paths.txt         # 執行CASE:'Video2Image'後輸出  
└─ video2image_image_paths.txt      # 執行CASE:'ImageAllInOne'後輸出  
```

---
