# 下載youtube影片

 說明: 於終端機輸入指令下載影片 0 ~ sec 秒，輸出output.mp4檔案

```python
$ python download_youtube.py -u <url> -o <output.mp4> -s <sec>
```

例如: 擷取[老公不要亂看別人啦 討厭！！ - YouTube](https://youtu.be/CUfFgRcKzAg) 0~10秒，並輸出成save.mp4檔案

```pathon
$ python download_youtube.py -u https://youtu.be/CUfFgRcKzAg -o save.mp4 -s 10
```
