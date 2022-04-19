```python
# import os library
import os
```

# 絕對路徑與相對路徑

作業系統允許路徑有兩種指定方式：

1. 「絕對路徑」是從根目錄開始。
2. 「相對路徑」是檔案相對於檔案系統某一個參考點的位置，若參考點改變，最後指到的位置就會不一樣。

那麼要如何取得「參考點」的位置？有兩種方式可以達到：

1. 將相對路徑附加到絕對路徑的後面，從而產生新的絕對路徑。
2. 將目前工作目錄當作參考點。

那麼要如何取得「目前工作目錄」？

# os.getcwd() — 目前工作目錄

目前工作目錄（current working directory），可以簡稱為cwd。  
可以利用`os.getcwd()`函式取得目前工作目錄，並且可以用`os.chdir()`來切換變更目錄。

```python
print('改變前: {}'.format(os.getcwd()))
os.chdir('../')
print('改變後: {}'.format(os.getcwd()))
```

```python
# output:

改變前: d:\code\jupyter_yolov5
改變後: d:\code
```

# os.listdir() — 路徑下所有檔案清單

可以取得指定路徑下所有子目錄與檔案的清單。  
透過 `os.curdir`作為`os.listdir()`的參數，可以取得目前工作目錄裡面的清單。

```python
os.listdir(os.curdir)
```

```python
# output:

['CR1',
 'darknet-master',
 'iCatch',
 'jupyter_torch',
 'jupyter_yolov5',
 'test.csv',
 'test2.csv',
 'yolov5-pytorch',
 'yolov5-yolov5',
 'yolo_zip-file']
```

# glob模組

在使用`os.listdir`的時候，可能會發現路徑中有一些檔案並不是你想要處理的檔案。  
可以使用glob模組中的glob函式來進行篩選。glob函式會回傳目前工作目錄中與條件符合的檔案。

```python
import glob
glob.glob（path_name)
```

`glob.glob(path_name)`，這裡的 path_name可以是絕對路徑，也可以是相對路徑。  
我們可以用萬用字元(*)加上其他的字串，取出想要的檔案。萬用字元可以對應任何數量的任何字元。  

如下，我們可以找到資料夾裡面所有副檔名為csv的檔案。

```python
import glob
glob.glob("*.csv")
```

```python
# output:

['test.csv', 'test2.csv']
```

# os.path — 處理路徑名稱

os.path模組裡面有很多與檔案名稱和檔案的路徑有關的函式。  
因為os.path是os模組裡面的模組，只需要import os到py檔案裡面就可以使用了。  
我們可以使用os.path來取得路徑名稱。

如果要拼接路徑的話，可以使用`os.path.join()`。  

os.path會依照目前正在使用的作業系統以系統正確的分隔符號來分割資料夾和檔名。  
無論是使用哪一個作業系統，`os.path.join()`都不會檢查參數是否合法。  
**因此在使用時，最好是自己寫一個函式來檢查路徑的合法性**。

## os.path.join()

```python
files = ["index.html","main.css","main.js"]
for filename in files:
    print(os.path.join("new_project", filename))
```

```python
# output:

new_project\index.html
new_project\main.css
new_project\main.js
```

### 與os.curdir搭配使用

我們可以用下面方式取得目前工作目錄下面的特定資料夾：  
下面程式碼可以取得目前工作目錄下面jupyter_yolov5資料夾中的所有檔案名稱。

```python
url = os.path.join(os.curdir,'jupyter_yolov5')
os.listdir(url)
```

```python
# output:

['.ipynb_checkpoints',
 'capture_livestream.ipynb',
 'capture_livestream.py',
 'os.ipynb',
 'VLC module in Python – An Introduction.ipynb',
 'YouTube Media Audio Download using Python – pafy and vlc.ipynb']
```

## os.path.basename(path)

basename是指路徑最後的目錄或檔案名稱。  
使用`os.path.basename()`，會擷取路徑最後的資料夾或檔案名稱。

```python
os.path.basename(url)
```

```python
# output:

'jupyter_yolov5'
```

承上，這個程式碼會取得的結果是jupyter_yolov5。因為jupyter_yolov5是最後的目錄。

## os.path.split(path)

會將basename與路徑的其他部分分開，並且以tuple的型態傳回。

## os.path.dirname(path)

會傳回路徑中不包括basename的部分。

## os.path.splitext(path)

可以取得檔案的副檔名，並且以tuple的型態傳回，第一個元素是路徑第二個元素是副檔名。

```python
import os
a = os.path.join('product','men','clothes','index.html')
split = os.path.split(a)
basename = os.path.basename(a)
dirname = os.path.dirname(a)
splitext = os.path.splitext(a)
print(a)
print('split: ' + str(split))
print('basename: '+ basename)
print('dirname: '+ dirname)
print('splitext: '+ str(splitext))
```

```python
# output:

product\men\clothes\index.html
split: ('product\\men\\clothes', 'index.html')
basename: index.html
dirname: product\men\clothes
splitext: ('product\\men\\clothes\\index', '.html')
```

## os.path.abspath(path)

如果你只知道相對路徑，可以透過呼叫`os.path.abspath()`取得絕對路徑。這是將相對路徑轉換為絕對路徑的一個簡單方法。

## os.path.isabs(path)

如果path是絕對路徑的話，就會返回True，反之如果path是相對路徑的話，，就會返回False。

## os.path.isdir(path)

確認路徑是否存在，若存在回傳True，反之回傳False。

# 建立資料夾（目錄）

可以利用`os.makedirs()`函式來建立資料夾。例如：
`os.makedirs("new_project")`
上面的程式將會建立一個new_project資料夾。  
如果是下面的程式碼，則會建立一個new_project資料夾與一個jupyter子資料夾：
`os.makedirs("new_project/jupyter")`
如果資料夾已經存在的話，該如何？  
由於makedirs的預設屬性是False，因此若資料夾已經存在，會顯示錯誤訊息。  
反之，如果想要覆蓋已存在的資料夾，可以加上 `exist_ok = True`參數。
`os.makedirs("new_project/jupyter", exist_ok = True)`
值得注意的是，使用`os.makedirs()`或`os.mkdir()`都可以建立新目錄。  
這兩個函式的差別在於`os.mkdir()`**不會自動建立多層目錄**，而`os.makedirs()`**可以建立多層目錄**。

# 其他操作

## os.rename() — 重新命名檔案

可以重新命名檔案或目錄。

## os.remove() — 刪除檔案

可以刪除檔案但是不可以刪除資料夾。

## os.rmdir() — 刪除資料夾（目錄）

可以刪除資料夾，條件是該資料夾必須是**空白資料夾**。

# 檔案與資料夾的複製

shutil模組可以幫助你在Python程式中搬移、複製、修改檔名或刪除檔案。使用前，要先匯入shutil模組。

```python
import shutil
```

## shutil.copy() — 複製檔案

```python
# 將來源路徑的檔案（src_file）複製到目的路徑（des）的資料夾裡面。
shutil.copy(src_file, des) 
```
