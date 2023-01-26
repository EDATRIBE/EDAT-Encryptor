'''
Date: 2023-01-15 23:17:17
LastEditTime: 2023-01-26 10:59:56
Author: Tridagger
Email: san.limeng@qq.com
'''
import os
import PySimpleGUI as sg
from tools import get_files, extractor, get_all_mkv, split_dir, ExtractError, DecryptError

VERSION = '1.0'
ICON = "./ico/decrypt.ico"
sg.theme('default1')

layout = [
    [sg.VPush()],
    [sg.Push(), sg.FilesBrowse(button_text="选择文件", size=(10, 1), key='-选择文件-', enable_events=True, target="-选择文件-", file_types=(('Matroska files', '*.mkv'),)),
     sg.In(size=(100, 20), disabled=True, key="-IN1-"), sg.Push()],
    [sg.Push(), sg.FolderBrowse(button_text="选择文件夹", size=(10, 1), key='-选择文件夹-', enable_events=True, target="-选择文件夹-"),
     sg.In(size=(100, 20), disabled=True, key="-IN2-"), sg.Push()],
    [sg.Push(), sg.Button(button_text="解密", size=(10, 1), key='-解密-'),
     sg.ProgressBar(max_value=100, size=(100, 20), key='-progressbar-'), sg.Push()],
    [sg.VPush()]
]


window = sg.Window(f'英配部落解密专用 V{VERSION}', layout,
                   icon=ICON, size=(800, 120))
progress_bar = window['-progressbar-']

while True:
    event, values = window.read()  # type: ignore
    if event in (None, sg.WIN_CLOSED):
        break
    elif event == '-选择文件-':
        window['-IN1-'].update(value=values['-选择文件-'])
        window['-IN2-'].update(value='')
    elif event == '-选择文件夹-':
        window['-IN2-'].update(value=values['-选择文件夹-'])
        window['-IN1-'].update(value='')
    elif event == '-解密-':
        if values['-IN1-'] or values['-IN2-']:
            if values['-IN1-']:
                files = split_dir(values['-IN1-'])
                all_files = []
            else:
                dir = values['-IN2-']
                all_files = get_files(dir)
                files = get_all_mkv(all_files)
            wrong_flag = 0
            if files:
                for i, file in enumerate(files):
                    try:
                        if not wrong_flag:
                            extractor(file)
                    except ExtractError:
                        sg.popup_ok(f'{file} 文件提取错误！', title='',
                                    icon="./ico/encrypt.ico")
                        window['-IN1-'].update(value='')
                        window['-IN2-'].update(value='')
                        wrong_flag = 1
                        break
                    except DecryptError:
                        sg.popup_ok(f'{file} 文件解密错误！', title='',
                                    icon="./ico/encrypt.ico")
                        window['-IN1-'].update(value='')
                        window['-IN2-'].update(value='')
                        wrong_flag = 1
                        break
                    progress_bar.UpdateBar(i+1, max=len(files))  # type: ignore

                if not wrong_flag:
                    for file in all_files:
                        if file.endswith('.md5'):
                            os.remove(file)
                    sg.popup_ok('所有文件已全部解密完成！', title='',
                                icon=ICON)
                    window['-IN1-'].update(value='')
                    window['-IN2-'].update(value='')
            else:
                sg.popup_ok('文件夹内没有可解密文件！', title='',
                            icon=ICON)
                window['-IN1-'].update(value='')
                window['-IN2-'].update(value='')

        else:
            sg.popup_ok('请选择文件或者文件夹！', title='',
                        icon=ICON)

window.close()
