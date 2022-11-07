# 擴增資料集

### Introduction

擴增有標籤之影像，擴增方法為隨機水平翻轉、隨機salt & pepper noise、隨機gaussian noise，三種隨機組合。

### Inputs

- `ROOT`            - 輸入影像/標籤根目錄

- `saveROOT`    - 儲存影像/標籤根目錄

組合示意如下：

```
+-------+-------+-------+  
|       |   -   |h-flip |  
+-------+-------+-------+  
|none   |   -   |    na |  
+-------+-------+-------+  
|s&p    |    na |    na |  
+-------+-------+-------+  
|gauss  |    na |    na |  
+-------+-------+-------+  
|s&p+g  |    na |    na |  
+-------+-------+-------+  
```

根目錄資料夾樹狀圖:  

- **注意**：影像與標籤要在同一個資料夾

- 資料夾可以分好幾層，不一定只能一層而已

```
ROOT  
└─ image_and_label_folder  
   ├─ image01.jpg  
   ├─ image01.txt  
   ├─ ..  
   ├─ imageXX.jpg  
   └─ imageXX.txt  
```

輸出根目錄資料夾樹狀圖：

```
saveROOT                    # 程式產生  
├─ image_and_label_folder  
│  ├─ image01.jpg  
│  ├─ image01.txt  
│  ├─ ..  
│  ├─ imageXX.jpg  
│  └─ imageXX.txt  
├─ labels  
│  ├─ image01.txt  
│  ├─ ..  
│  └─ imageXX.txt  
└─ image_augmentation_log.txt  
```
