## 畫ROI及移除超出範圍的bbox (for CM088)

### args:

1. `ROOT` : 根目錄 (包含影像及標籤文件檔)

### 根目錄樹狀圖:

```
ROOT  
├─ labels  
│  ├─ 000000.txt  
│  ├─ 000002.txt  
│  └─ ..  
├─ 000000.jpg  
├─ 000001.jpg  
├─ 000002.jpg  
└─ ..  
```

### 說明:

1. 此程式主要應用在使用自動標籤後，去除超出ROI範圍的bbox，並畫出ROI之界線，以利檢查自動標籤是否有誤。

2. 執行後會畫出藍色與粉色梯形框，其中藍色為較嚴謹的ROI，粉色為較寬鬆的ROI。

3. 載入影像相對應的`labels/xxxxxx.txt`，重新寫入在ROI範圍內之bbox(移除不在ROI範圍內之bbox)。
   
   ![test001.jpg](C:\Users\danielwu\Desktop\test\test001.jpg)
   
   如上圖所示，執行後會在影像上畫出綠色及粉色的梯形框，文件檔僅會保留綠色bbox的資訊，紅色bbox將被刪除。
