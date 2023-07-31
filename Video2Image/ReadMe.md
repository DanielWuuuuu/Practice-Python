# 影片轉圖片

### args:
1. `isLog`         : 是否顯示log
2. `case`          : 功能選擇 ( 參考 case_list )
3. `ROOT`          : 根目錄 (包含原始影片資料夾、創建影像資料夾等)
4. `videos_folder` : 影片母資料夾路徑
5. `interval`      : 幀數間格 (每幾幀擷取一張影像)
6. `cut_method`    : 切割方法 (畫面只有一個主畫面:normal; 畫面有4個子畫面:four_in_one)
7. `class_mapping` : 標籤轉換 (索引:標籤)

> **Note**  
> `ROOT`不可以含有此關鍵字:`images`!

---

<a id="FlowChart"></a>
### 流程

1. 執行CASE:<a href="#Video2ImageAndAll">Video2ImageAndAll</a>:  
   (1) 將`videos_folder`資料夾內所有影片切成影像，輸出至`video2image`資料夾  
   (2) 將切片的影像複製一份至`all_images`資料夾內，待自動標籤用  <br><br>

2. 另外執行YOLOv5  
   `!python detect.py --weights best.pt --source path/ --conf-thres 0.5 --save-txt --name xxx --line-thickness 2 --hide-labels`  
   (1) 將`yolov5/runs/detect/xxx/labels`手動複製至`ROOT/videos_folder_all_yolo_labels`  
   (2) 將`yolov5/runs/detect/xxx`內之影像手動複製至`ROOT/videos_folder_check_images`  

3. 執行CASE:<a href="#Yolo2VocAllocateData">Yolo2VocAllocateData</a>:  
   (1) 將`all_yolo_labels`資料夾內`.txt`檔轉成`.xml`檔至`all_voc_labels`資料夾內  
   (2) 將`check_images`(對應`all_voc_labels`)每2000筆分配在一個資料夾，母資料夾為`help_check_labels`，接著就可以請同仁幫忙檢查自動標籤是否有誤，使用Labelimg等開源軟體修正`.xml`檔內類別座標資訊  
   (3) 將建立`help_check_labels`資料夾，並刪除`all_images`資料夾、`check_images`資料夾、`all_yolo_labels`資料夾與`all_voc_labels`資料夾  <br><br>

4. 執行CASE:<a href="#UpdateTransformCreate">UpdateTransformCreate</a>:  
   (1) 手動將檢查完的`.xml`檔(母資料夾為`help_check_labels`)覆蓋原始的`help_check_labels`資料夾  
   (2) 將更新後的`.xml`檔移至`video2image/videoXX/voc_labels`資料夾內  
   (3) 將`voc_labels`資料夾內`.xml`檔轉成`.txt`檔並分別儲存至`images`資料夾內及`labels`資料夾內  
   (4) 建立影像空標籤的`.txt`檔  

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

<a id="Video2ImageAndAll"></a>
### CASE:'Video2ImageAndAll'

說明:

1. 依序執行CASE:<a href=#Video2Image>Video2Image</a>與CASE:<a href=#ImageAllInOne>ImageAllInOne</a>  

<a href="#FlowChart">(回流程)</a>

---

<a id="Yolo2VocAllocateData"></a>
### CASE:'Yolo2VocAllocateData'

說明:

1. 前置作業請參考CASE:<a href=#Yolo2Voc>Yolo2Voc</a>第1、2點說明
2. 依序執行CASE:<a href=#Yolo2Voc>Yolo2Voc</a>與CASE:<a href=#AllocateData>AllocateData</a>
3. 額外刪除`all_images`資料夾

<a href="#FlowChart">(回流程)</a>

---

<a id="UpdateTransformCreate"></a>
### CASE:'UpdateTransformCreate'

說明:

1. 依序執行CASE:<a href=#UpdateLabels>UpdateLabels</a>、CASE:<a href=#Voc2Yolo>Voc2Yolo</a>與CASE:<a href=#CreateNullTxt>CreateNullTxt</a>

<a href="#FlowChart">(回流程)</a>

---

<a id="Video2Image"></a>
### CASE:'Video2Image'

說明:

1. 影片切成影像
2. 輸出影像資料夾樹狀圖 ( 階層會與來源相同 ):

   ```
   ROOT  
   ├─ {videos_folder}             # 原始影片，執行此CASE後，刪除此資料夾!  
   ├─ {videos_folder}_video2image # 執行此CASE後，輸出  
   │  ├─ folder1  
   │  │  ├─ video01  
   │  │  │  ├─ images             # 影片 > 影像儲存資料夾  
   │  │  │  │  ├─ 000000.jpg  
   │  │  │  │  ├─ ..  
   │  │  │  │  └─ 000010.jpg  
   │  │  │  ├─ video01.{file_exe}  # 「搬移」原始影片  
   │  │  │  └ video01_path.txt     # 影像絕對路徑  
   │  │  ├─ ..  
   │  │  └─ videoXX  
   │  │     ├─ images  
   │  │     │  ├─ 000000.jpg  
   │  │     │  ├─ ..  
   │  │     │  └─ 000020.jpg  
   │  │     ├─ videoXX.{file_exe}  
   │  │     └ videoXX_path.txt  
   │  ├─ folder2  
   │  │  ├─ video01  
   │  │  ├─ ..  
   │  │  └─ videoXX  
   │  └─ ..  
   └ {videos_folder}_video2image_image_paths.txt  # 執行此CASE後，輸出  
   ```

3. video2image_image_paths.txt為儲存切片後各影像的路徑

<a href=#Video2ImageAndAll>回CASE: Video2ImageAndAll</a>

---

<a id="ImageAllInOne"></a>
### CASE:'ImageAllInOne'

說明:

1. 將在各個資料夾內的影像複製出來放在`all_images`資料夾內 ( YOLO自動標籤用 )
2. 輸出影像資料夾樹狀圖 ( 輸出的影像序號會接續下去 ):

   ```
   ROOT  
   ├─ {videos_folder}_all_images   # 執行此CASE後，輸出  
   │  ├─ 000000.jpg  
   │  ├─ ..  
   │  └─ xxxxxx.jpg  
   ├─ {videos_folder}_video2image  # 執行CASE:'Video2Image'後輸出  
   ├─ {videos_folder}_allinone_image_paths.txt     # 執行此CASE後，輸出 ( 如第4點範例 )  
   └─ {videos_folder}_video2image_image_paths.txt  # 執行CASE:'Video2Image'後輸出  
   ```

3. allinone_image_paths.txt資訊如下:

   ```
   ## # <video2image Relative Path>\n'
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

<a href=#Video2ImageAndAll>回CASE: Video2ImageAndAll</a>

---

<a id="Yolo2Voc"></a>
### CASE:'Yolo2Voc'

說明:
1. 將`all_yolo_labels`資料夾內`.txt`檔轉成`.xml`檔至`all_voc_labels`資料夾內
2. 先執行YOLO v5 detect.py:
   `!python detect.py --weights best.pt --source path/ --conf-thres 0.5 --save-txt --name xxx --line-thickness 2 --hide-labels`  
   (1) 將`yolov5/runs/detect/expXX/labels`手動複製至`ROOT/{videos_folder}_all_yolo_labels`  
   (2) 將`yolov5/runs/detect/expXX`內之影像手動複製至`ROOT/{videos_folder}_check_images`  
3. 執行完YOLO v5 detect.py後，再執行此CASE  
   **注意**  
   (1) 若未執行「自動標籤」，即`check_images`與`all_yolo_labels`資料夾都沒有的情況下，則不會執行此CASE  
   (2) 若只有`check_images`資料夾，沒有`all_yolo_labels`資料夾，則不會執行此CASE  
   (3) 若只有`all_yolo_labels`資料夾，沒有`check_images`資料夾，則`check_images`將使用`all_images`資料夾  
     
   
4. 輸出標籤資料夾樹狀圖:

   ```
   ROOT  
   ├─ {videos_folder}_all_voc_labels   # 執行此CASE後，輸出  
   │  ├─ 000000.xml  
   │  ├─ ..  
   │  └─ xxxxxx.xml  
   ├─ {videos_folder}_all_yolo_labels  # 手動將YOLO偵測物件輸出的.txt檔放入此資料夾  
   │  ├─ 000000.txt  
   │  ├─ ..  
   │  └─ xxxxxx.txt  
   ├─ {videos_folder}_check_images     # 手動將YOLO偵測物件輸出的.jpg檔放入此資料夾  
   │  ├─ 000000.jpg  
   │  ├─ ..  
   │  └─ xxxxxx.jpg  
   ├─ {videos_folder}_all_images       # 執行CASE:'ImageAllInOne'後輸出  
   ├─ {videos_folder}_video2image      # 執行CASE:'Video2Image'後輸出  
   ├─ {videos_folder}_allinone_image_paths.txt       # 執行CASE:'ImageAllInOne'後輸出  
   └─ {videos_folder}_video2image_image_paths.txt    # 執行CASE:'Video2Image'後輸出  
   ```

<a href=#Yolo2VocAllocateData>回CASE: Yolo2VocAllocateData</a>

---

<a id="AllocateData"></a>
### CASE:'AllocateData'

說明:

1. 將`check_images`資料夾內影像及`all_voc_labels`資料夾內標籤檔按比例重新分配，每2000個檔案放在一個資料夾，接著就可以請同仁們幫忙檢查自動標籤是否有誤，並手動修正
2. 執行後將刪除`all_images`資料夾、`all_voc_labels`資料夾、`all_yolo_labels`資料夾與`check_images`資料夾
3. 分配資料夾樹狀圖:

   ```
   ROOT  
   ├─ {videos_folder}_all_images         # 執行此CASE後，刪除此資料夾!  
   ├─ {videos_folder}_all_voc_labels     # 執行此CASE後，刪除此資料夾!  
   ├─ {videos_folder}_all_yolo_labels    # 執行此CASE後，刪除此資料夾!  
   ├─ {videos_folder}_check_images       # 執行此CASE後，刪除此資料夾!  
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
   ├─ {videos_folder}_video2image        # 執行CASE:'Video2Image'後輸出  
   ├─ {videos_folder}_allinone_image_paths.txt         # 執行CASE:'Video2Image'後輸出  
   └─ {videos_folder}_video2image_image_paths.txt      # 執行CASE:'ImageAllInOne'後輸出  
   ```

<a href=#Yolo2VocAllocateData>回CASE: Yolo2VocAllocateData</a>

---

<a id="UpdateLabels"></a>
### CASE:'UpdateLabels'

說明:

1. 更新自動標籤檔: 將各個資料夾內檢查好的`.xml`檔放回`video2image`資料夾
2. 同仁們檢查好標籤後，請同仁們回傳整個`help_check_labels`資料夾(子資料夾`images`可不用回傳)
3. 將回傳的`help_check_labels`資料夾覆蓋回自己原本的`help_check_labels`資料夾 
   ( 更新標籤檔: 檔案已存在 => 勾選 全部取代 )
4. 執行前資料夾樹狀圖:

   ```
   ROOT  
   ├─ {videos_folder}_help_check_labels  # 手動將檢查好的help_check_labels資料夾覆蓋回來  
   ├─ {videos_folder}_video2image        # 執行CASE:'Video2Image'後輸出  
   ├─ {videos_folder}_allinone_image_paths.txt         # 執行CASE:'Video2Image'後輸出  
   └─ {videos_folder}_video2image_image_paths.txt      # 執行CASE:'ImageAllInOne'後輸出  
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
   │  │  │  ├─ video01.{file_exe}  
   │  │  │  └ video01_path.txt  
   │  │  ├─ ..  
   │  │  └─ videoXX  
   │  │     ├─ images  
   │  │     ├─ voc_labels              # 執行此CASE後，輸出  
   │  │     │  ├─ 000000.xml  
   │  │     │  ├─ ..  
   │  │     │  └─ 000020.xml  
   │  │     ├─ videoXX.{file_exe}  
   │  │     └ videoXX_path.txt  
   │  ├─ folder2  
   │  │  ├─ video01  
   │  │  ├─ ..  
   │  │  └─ videoXX  
   │  └─ ..  
   ├─ {videos_folder}_allinone_image_paths.txt         # 執行CASE:'Video2Image'後輸出  
   └─ {videos_folder}_video2image_image_paths.txt      # 執行CASE:'ImageAllInOne'後輸出  
   ```

<a href=#UpdateTransformCreate>回CASE: UpdateTransformCreate</a>

---

<a id="Voc2Yolo"></a>
### CASE:'Voc2Yolo'

說明:

1. 將標籤檔VOC格式(`.xml`)轉成YOLO格式(`.txt`)
2. 對`video2image`資料夾內每個`voc_labels`資料夾的`.xml`檔進行格式轉換，並儲存在`images`資料夾內及`labels`資料夾內

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
   │  │  │  ├─ video01.{file_exe}  
   │  │  │  └ video01_path.txt  
   │  │  └─ ..   
   │  └─ ..  
   ├─ {videos_folder}_allinone_image_paths.txt         # 執行CASE:'Video2Image'後輸出  
   └─ {videos_folder}_video2image_image_paths.txt      # 執行CASE:'ImageAllInOne'後輸出  
   ```

<a href=#UpdateTransformCreate>回CASE: UpdateTransformCreate</a>

---

<a id="CreateNullTxt"></a>
### CASE:'CreateNullTxt'

說明:

1. 建立影像空標籤的`.txt`檔

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
   │  │  │  ├─ video01.{file_exe}  
   │  │  │  └ video01_path.txt  
   │  │  └─ ..   
   │  └─ ..  
   ├─ {videos_folder}_allinone_image_paths.txt         # 執行CASE:'Video2Image'後輸出  
   └─ {videos_folder}_video2image_image_paths.txt      # 執行CASE:'ImageAllInOne'後輸出  
   ```

<a href=#UpdateTransformCreate>回CASE: UpdateTransformCreate</a>

---
