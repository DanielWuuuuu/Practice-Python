# 克隆資料集

### 1. 來源資料集目錄結構:

```python
dataset            # clone_dir  
├─ 0               ## clone_images_folder  
│  ├─ img          ### clone_images_folder, clone_images_folder_dir  
│  │  ├─ 0000.jpg  #### clone_images_absolute_paths[0]  
│  │  ├─ ..
│  │  └─ 1999.jpg
│  └─ vocAnots      ### clone_annotations_folder, clone_annotations_folder_dir  
│     ├─ 0000.xml   #### clone_labels_absolute_paths[0]  
│     ├─ ..
│     └─ 1999.xml
├─ 1                ## clone_images_folder  
├─ ..               ## clone_images_folder    
└─ 18
```

### 2. 輸出資料集目錄結構:

```python
new_dataset        # save_dataset_dir  
├─ images          ## save_images_folder  
│  ├─ train        ### data_split['train']  
│  │  ├─ 0000.jpg  
│  │  └─ ..  
│  ├─ val          ### data_split['val']  
│  │  ├─ 0001.jpg  
│  │  └─ ..  
│  └─ test         ### data_split['test']  
│     ├─ 0003.jpg  
│     └─ ..  
└─ labels          ## save_annotations_folder  
   ├─ train  
   ├─ val 
   └─ test
```

### 3. 修改變數(Variable)說明

- 來源資料集目錄:
  
  ```python
  clone_dir = 'C:\\Users\\danielwu\\Desktop\\dataset'
  ```

- 輸出資料集目錄:
  
  ```python
  save_dataset_dir = 'C:\\Users\\danielwu\\Desktop\\new_dataset'
  ```

- 來源資料集影像資料夾名稱:
  
  ```python
  clone_images_folder = 'img'
  ```

- 來源資料集標籤資料夾名稱:
  
  ```python
  clone_annotations_folder = 'vocAnots'
  ```

- 來源資料集影像副檔名:
  
  ```python
  clone_images_format = '.jpg'
  ```

- 來源資料集標籤副檔名:
  
  ```python
  clone_annotations_format = '.xml'
  ```

- 輸出資料集影像資料夾名稱:
  
  ```python
  save_images_folder = 'images'
  ```

- 輸出資料集標籤資料夾名稱:
  
  ```python
  save_annotations_folder = 'labels'
  ```

- 訓練、驗證、測試集比例:
  
  ```python
  data_split = {'train': 0.6,
                'val':   0.2,
                'test':  0.2}
  ```

- 克隆標籤是否轉檔:
  
  ```python
  isConvert_format = True
  ```

- 標籤類別:
  
  ```python
  class_mapping = {'0': 'person'}
  ```
  
  


