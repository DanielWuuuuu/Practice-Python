#!/usr/bin/env python
# coding: utf-8

# In[ ]:


'''
REFERENCE

[1] CAVE Education. 2020. "Pytorch深度學習框架X NVIDIA JetsonNano應用-YOLOv5辨識台灣即時路況 (繁體)"
    [Online]. Available: https://www.rs-online.com/designspark/pytorchx-nvidia-jetsonnano-yolov5-cn
    [Accessed Feb. 15, 2022]

'''


# In[ ]:


### 下載yotube影片 
# 說明: 於終端機輸入指令下載影片，並剪裁 0 ~ t 秒
# $ python capture_livestream.py -u https://youtu.be/CUfFgRcKzAg -o save.mp4 -s 10

### IMPORT LIBRARY
import argparse
import time
import pafy
import vlc
from moviepy.video.io.VideoFileClip import VideoFileClip
import urllib.request


# In[ ]:


### DEFINE FUNCTION
### 取得terminal視窗大小
def get_cmd_size():
    import shutil
    col, line = shutil.get_terminal_size()
    return col, line


### 打印分隔用
def print_div(text=None):
    col,line = get_cmd_size()
    col = col-1
    if text == None:
        print('-'*col)
    else:
        print('-'*col)
        print(text)
        print('-'*col)


### 確認url是否有效
def check_url(url):
    import urllib.request
    code = urllib.request.urlopen(url).getcode()
    if str(code).startswith('2') or str(code).startswith('3'):
        print('影片連結正常!')
    else:
        print('影片連結失效!')


### 擷取特定秒數並儲存
def cut_video(video_name, sec, save_name):
    print_div()
    print('Cutting Video Used Moviepy\n')
    time.sleep(1)
    
    with VideoFileClip(video_name) as video:
        new = video.subclip(0, sec)
        new.write_videofile(save_name)
   
    print_div(f'save file {save_name}')


# In[ ]:


### DEFINE MANI FUNCTION
def capture_video(opt):

    # 欲儲存影片之名稱(原始影片)
    org_video_name = 'org.mp4'      

    # 裁剪影片名稱   
    save_name = opt.output     
  
    # 欲保留秒數
    sec = opt.second        

    # 取得Youtube影片
    video = pafy.new(opt.url)   
    
### 取得影片來源列表，並選擇影片
    streams = video.streams   
    for i, stream in enumerate(streams):
        print('{}. {}'.format(i+1, stream))

    idx = int(input('請選擇影片格式之序號:'))
    while idx not in range(1, i+2):
        idx = int(input('超出範圍!!請重新選擇影片格式之序號:'))

    target_video = streams[idx-1] 
    print('您選擇的影片格式是: {}'.format(target_video))
#     print('影片URL: {}'.format(target_video.url))

### 下載影片
    # creating a vlc instance
    vlc_instance = vlc.Instance()

    # creating a media player
    player = vlc_instance.media_player_new()

    # creating a media
    media = vlc_instance.media_new(target_video.url)

    # 命名欲儲存之影片
    media.get_mrl()
    media.add_option(f"sout=file/ts:{org_video_name}") 

    # setting media to the player
    player.set_media(media)

    # play the video
    player.play()

    # 確認影片為下載階段或下載完畢
    t = 0
    sign = '.'
    end = '\r'
    good_states = ["State.Playing", "State.NothingSpecial", "State.Opening"]
    
    while str(player.get_state()) in good_states:
#         print('Stream is working. Current state = {}'.format(player.get_state()))
        bar = t*sign + ' '*(3-t)
        print('Download{}'.format(bar), end=end)
        t += 1
        if t > 3:
            t = 0
        time.sleep(0.5)
    
    # 裁切影片
    cut_video(org_video_name, sec, save_name)             
        
### 關閉資源
    # 關閉撥放器以及釋放媒體
    player.stop()                              


# In[ ]:


if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--url', type=str, help='youtube url')
    parser.add_argument('-o', '--output', type=str, default='sample.mp4' , help='save file path\name')
    parser.add_argument('-s', '--second',type=int, default=10 , help='video length')
    opt = parser.parse_args()
    capture_video(opt)

