# 驗證文件檔輸出至影像

說明:
利用YOLOv4驗證測試集輸出偵測文件檔(如附件1)，將偵測文件檔結合在原始影像輸出有畫框的影像。

參數:

1. `ROOT`              : 原始影片/座標文件檔路徑
2. `SPLIT_ROOT`        : 要分割的路徑(偵測文件檔的路徑為絕對路徑 -> 分割成相對路徑顯示在輸出的影像)
3. `image_save_folder` : 儲存影片路徑
4. `color_file`        : 標籤/顏色清單文件檔 (可有可無)
5. `isAll`             : `isAll=True`:所有標籤畫出來, `isAll=False`:僅將`onlyLabels`內的標籤畫出來
6. `onlyLabels`        : 只要畫特定的標籤 (僅`isAll=False`時定義)

資料夾樹狀圖:

```
ROOT  
├─ images_out     # 程式建立  
│  ├─ 000000.jpg  # 程式輸出  
│  ├─ 000001.jpg  # 程式輸出  
│  └─ ..  
├─ comp4_det_test_cone.txt    # 將darknet/result/comp4_det_test_cone.txt複製過來  
├─ comp4_det_test_person.txt  # 將darknet/result/comp4_det_test_person.txt複製過來  
└─ class_colors.txt           # 標籤顏色清單 (可有可無)  
```

---

流程:  

1. 修改`scr/detector.c`內function:`validate_detector`約第799行前後，並重新編譯生成`detector.exe`:
   
    修改前:
   
   ```
   else {
       print_detector_detections(fps, id, dets, nboxes, classes, w, h);
   }
   ```
   
    修改後:
   
   ```
   else {
       print_detector_detections(fps, path, dets, nboxes, classes, w, h);
   }
   ```

2. 修改`train.data`內`valid`指到測試集路徑文件檔

3. 執行YOLOv4驗證影像輸出偵測文件檔指令(in Linux)如:  
    `./darknet detector valid ./train.data ./yolov4-tiny.cfg ./best.weights`
    => 執行上述指令`darknet/result`會有文件檔開頭為`comp4_det_test_`的`.txt`檔

4. 複製`darknet/result/comp4_det_test_*.txt`至`ROOT`底下

5. 確保原始圖片存在，原始圖片的路徑為`comp4_det_test_*.txt`內第一欄的資訊

6. 執行此`Yolov4ValidTxt2DetectImage.py`

---

附件1:

comp4_det_test_cone.txt:

```
D:\Dataset(Test)\Sumitomo(CM088A)\220316\file_20220316083442\20220208_REFERENCE_DATA_01\220208142415\220208142415_img\000013.jpg 0.001128 857.669189 270.190430 1012.778687 510.487732
D:\Dataset(Test)\Sumitomo(CM088A)\220316\file_20220316083442\20220208_REFERENCE_DATA_01\220208142415\220208142415_img\000016.jpg 0.001183 696.023315 167.945938 797.465942 397.454895
D:\Dataset(Test)\Sumitomo(CM088A)\220316\file_20220316083442\20220208_REFERENCE_DATA_01\220208142415\220208142415_img\000017.jpg 0.001583 645.638672 151.927246 746.952881 357.833893
D:\Dataset(Test)\Sumitomo(CM088A)\220316\file_20220316083442\20220208_REFERENCE_DATA_01\220208142415\220208142415_img\000022.jpg 0.001301 607.242493 104.822128 673.907166 247.199509
```

comp4_det_test_person.txt:

```
D:\Dataset(Test)\Sumitomo(CM088A)\220316\file_20220316083442\20220208_REFERENCE_DATA_01\220208142415\220208142415_img\000003.jpg 0.002355 735.588013 8.579786 796.169678 69.028137
D:\Dataset(Test)\Sumitomo(CM088A)\220316\file_20220316083442\20220208_REFERENCE_DATA_01\220208142415\220208142415_img\000004.jpg 0.002856 735.764648 7.264225 794.745361 68.298630
D:\Dataset(Test)\Sumitomo(CM088A)\220316\file_20220316083442\20220208_REFERENCE_DATA_01\220208142415\220208142415_img\000010.jpg 0.995857 1002.637329 420.485291 1220.185913 604.217163
D:\Dataset(Test)\Sumitomo(CM088A)\220316\file_20220316083442\20220208_REFERENCE_DATA_01\220208142415\220208142415_img\000011.jpg 0.998493 974.717773 354.667572 1151.623779 562.967651
```
