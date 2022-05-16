# 座標文件檔輸出至影像

說明:  
YOLOv4偵測影片輸出座標文件檔(如附件1)，將座標文件檔結合在原始影片輸出有畫框的影片。

參數:

1. `ROOT`              : 原始影片/座標文件檔路徑
2. `video_save_folder` : 儲存影片路徑
3. `color_file`        : 標籤/顏色清單文件檔 (可有可無)
4. `isAll`             : `isAll=True`:所有標籤畫出來, `isAll=False`:僅將`onlyLabels`內的標籤畫出來
5. `onlyLabels`        : 只要畫特定的標籤 (僅`isAll=False`時定義)

資料夾樹狀圖:

```
ROOT  
├─ video_save_folder  # 程式建立  
│  ├─ 000001_out.avi  # 程式輸出  
│  ├─ 000002_out.avi  # 程式輸出  
│  └─ ..  
├─ 000001.MOV  
├─ 000001.txt  
├─ 000002.MOV  
├─ 000002.txt  
├─ ...  
└─ class_colors.txt  # 標籤顏色清單 (可有可無)  
```

---

備註:
YOLOv4偵測影片輸出座標文件檔指令(in Linux)如:

```
./darknet detector demo ./train.data ./yolov4-tiny.cfg ./best.weights -dont_show -ext_output ./dataset/test/video0001.MOV > ./dataset/result_test/video0001.txt
```

---

附件1:

```
Demo
net.optimized_memory = 0 
mini_batch = 1, batch = 1, time_steps = 1, train = 0 
Create CUDA-stream - 0 
 Create cudnn-handle 0 
nms_kind: greedynms (1), beta = 0.600000 
nms_kind: greedynms (1), beta = 0.600000 

 seen 64, trained: 384 K-images (6 Kilo-batches_64) 
video file: ../tmp/test_video/220208150059.MOV
Video stream: 1280 x 720 
Objects:


FPS:0.0      AVG_FPS:0.0
Objects:

cone: 98%     (left_x:  629   top_y:  345   width:   71   height:  104)
cone: 92%     (left_x:  596   top_y:  264   width:   52   height:  103)
person: 95%     (left_x:  727   top_y:  175   width:  112   height:  238)

FPS:23.3      AVG_FPS:0.0
Objects:

cone: 97%     (left_x:  629   top_y:  345   width:   70   height:  102)
cone: 92%     (left_x:  596   top_y:  264   width:   52   height:  102)
person: 96%     (left_x:  728   top_y:  174   width:  108   height:  240)

FPS:43.5      AVG_FPS:0.0
...
```
