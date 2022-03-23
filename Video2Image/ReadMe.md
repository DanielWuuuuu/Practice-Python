# 影片轉圖片

### args:

1. `isLog`                : 是否顯示log
2. `case`                  : 功能選擇 ( 參考 case_list )
3. `interval`          : 幀數間格 (每幾幀擷取一張影像)
4. `H1_DIR`              : 影片母資料夾路徑
5. `H1_image_DIR`  : 影像母資料夾路徑

```python
case_list = {'Video2ImageOneDir' : 0,   # 輸出1個影像母資料夾
             'Video2ImageTwoDir' : 1,   # 輸出2個影像資料夾
             'CloneImageOneDir'  : 2,   # 
             'CloneImageTwoDir'  : 3}   # 
```

### 影片資料夾樹狀圖:

說明:

1. for CASE 1 and CASE 2
2. 資料夾可為多階層 ( 以下為範例 )
   
   ```
   H1_DIR  
   ├─ H2_FOLDER  
   │  ├─ H3_FOLDER  
   │  │  ├─ video01.mov  
   │  │  ├─ ..  
   │  │  └─ videoXX.mov  
   │  ├─ H3_FOLDER  
   │  ├─ ..  
   │  └─ H3_FOLDER  
   ├─  ..  
   └─ H2_FOLDER  
   ```

---

### CASE 'Video2ImageOneDir' : 輸出1個影像母資料夾

說明:

1. 輸出影像資料夾樹狀圖 ( 階層會與來源相同 ):
   
   ```
   H1_DIR_video2image
   ├─ H2_FOLDER
   │  ├─ H3_FOLDER
   │  │  ├─ video01
   │  │  │  ├─ image01.jpg
   │  │  │  ├─ ..
   │  │  │  ├─ imageXX.jpg
   │  │  │  └─ video01.MOV
   │  │  ├─ ..
   │  │  └─ videoXX
   │  ├─ H3_FOLDER
   │  ├─ ..
   │  └─ H3_FOLDER
   ├─  ..
   └─ H2_FOLDER
   ```

---

### CASE 'Video2ImageTwoDir' : 輸出2個影像資料夾

說明:

1. 輸出1樹狀圖: 切片影像 ( 輸出的影像序號會接續下去 )
   
   ```
   H1_DIR_all_image
   ├─ image01.jpg
   ├─  ..
   └─ imageXX.jpg
   ```

2. 輸出2樹狀圖: 影像上方有影像出處
   
   ```
   H1_DIR_info_image
   ├─ image01.jpg
   ├─  ..
   └─ imageXX.jpg
   ```

---

### CASE 'CloneImageOneDir' : 克隆影像

說明:

1. 輸入資料夾可為多階層,底層為.jpg檔
2. 輸出影像資料夾: ( 輸出的影像序號會接續下去 )
   
   ```
   H1_DIR_all_image
   ├─ image01.jpg
   ├─  ..  
   └─ imageXX.jpg
   ```

---

### CASE 4 'CloneImageTwoDir' : 克隆影像ver2

說明:

1. 輸入資料夾可為多階層,底層為.jpg檔
2. 輸出影像資料夾: ( 輸出的影像序號會接續下去 )
   
   ```
   H1_DIR_all_image
   ├─ image01.jpg
   ├─  ..  
   └─ imageXX.jpg
   ```
3. 輸出影像 ( 影像上方有影像出處資訊 ) 資料夾:
   
   ```
   H1_DIR_info_image
   ├─ image01.jpg
   ├─  ..  
   └─ imageXX.jpg
   ```
