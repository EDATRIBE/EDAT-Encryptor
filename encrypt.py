'''
Date: 2023-01-15 23:17:17
LastEditTime: 2023-01-26 11:00:56
Author: Tridagger
Email: san.limeng@qq.com
'''
import os
import PySimpleGUI as sg
from tools import get_files, get_all_mp4, merger, rename_and_md5, EncryptTestError, EncryptError, MergeError

VERSION = '1.0'
VIDEO = 'video/video.mp4'
ICON = "./ico/encrypt.ico"

sg.theme('default1')

layout = [
    [sg.VPush()],
    [sg.Push(), sg.FolderBrowse(button_text="选择文件夹", size=(10, 1),  key='-选择文件夹-', target="-IN-"),
     sg.In(size=(100, 20), disabled=True, key="-IN-"), sg.Push()],
    [sg.Push(), sg.Button(button_text="加密", size=(10, 1), key='-加密-'),
     sg.ProgressBar(max_value=100, size=(100, 20), key='-progressbar-'), sg.Push()],
    [sg.VPush()]
]


window = sg.Window(f'英配部落加密专用 V{VERSION}', layout,
                   icon=ICON, size=(800, 100))
progress_bar = window['-progressbar-']

while True:
    event, values = window.read()  # type: ignore
    if event in (None, sg.WIN_CLOSED):
        break
    elif event == '-加密-':
        if values['-IN-']:
            dir = values['-IN-']
            all_files = get_files(dir)
            wrong_flag = 0
            for file in all_files:
                if file[-4:] not in ['.mp4']:
                    sg.popup_ok(f'{dir} 存在其他类型文件！', title='',
                                icon=ICON)
                    window['-IN-'].update(value='')
                    wrong_flag = 1
                    break
            mp4_files = get_all_mp4(all_files)
            if mp4_files and not wrong_flag:
                for i, file in enumerate(mp4_files):
                    try:
                        if not wrong_flag:
                            merger(file, VIDEO)

                    except MergeError:
                        sg.popup_ok(f'{file} 出现合并错误！', title='',
                                    icon=ICON)
                        window['-IN-'].update(value='')
                        wrong_flag = 1
                        break
                    except EncryptError:
                        sg.popup_ok(f'{file} 出现加密错误！', title='',
                                    icon=ICON)
                        window['-IN-'].update(value='')
                        wrong_flag = 1
                        break
                    except EncryptTestError:
                        sg.popup_ok(f'{file} 出现测试错误！', title='',
                                    icon=ICON)
                        window['-IN-'].update(value='')
                        wrong_flag = 1
                        break
                    progress_bar.UpdateBar(  # type: ignore
                        i+1, max=len(mp4_files))
                if not wrong_flag:
                    rename_and_md5(dir)
                    sg.popup_ok('所有视频已全部加密完成！', title='',
                                icon=ICON)
                    window['-IN-'].update(value='')
            elif not wrong_flag:
                sg.popup_ok('文件夹内没有MP4格式的文件！', title='',
                            icon=ICON)
                window['-IN-'].update(value='')

        else:
            sg.popup_ok('请选择一个文件夹！', title='',
                        icon=ICON)

window.close()
