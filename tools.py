'''
Date: 2023-01-19 17:27:47
LastEditTime: 2023-01-26 10:10:36
Author: Tridagger
Email: san.limeng@qq.com
'''
import subprocess
import os
from uuid import uuid4
from random import randint
from hashlib import md5

DETACHED_PROCESS = 0x00000008
PASSWORD = "72BAB1C1649A581C"


class MergeError(Exception):
    pass


class EncryptError(Exception):
    pass


class EncryptTestError(Exception):
    pass


class OtherFileError(Exception):
    pass


class ExtractError(Exception):
    pass


class DecryptError(Exception):
    pass


def mkv_extractor(file: str, output: str) -> None:
    """
    使用 mkvextract 提取 mkv 中的附件

    Arguments:
        file -- mkv 文件
        output -- 提取出的附件存放
    """
    extract_cmd: str = f".\\bin\\mkvextract.exe \"{file}\" attachments 1:\"{output}\""
    if subprocess.call(extract_cmd, creationflags=DETACHED_PROCESS):
        raise ExtractError


def decryptor(encrypted_file: str, dir: str, password: str) -> None:
    """
    使用 7z 解密文件

    Arguments:
        encrypted_file -- 已加密的文件
        dir -- 解压到指定目录
        password -- 密码
    """
    encrypt_cmd: str = f".\\bin\\7z.exe x \"{encrypted_file}\" -p{password} -o\"{dir}\""
    if subprocess.call(encrypt_cmd, creationflags=DETACHED_PROCESS):
        raise DecryptError


def encryptor(raw_file: str, encrypted_file: str, password: str) -> None:
    """
    使用 7z 加密文件

    Arguments:
        raw_file -- 加密前的原文件
        encrypted_file -- 加密后的文件
        password -- 密码
    """
    encrypt_cmd = f".\\bin\\7z.exe a -mx0 \"{encrypted_file}\" \"{raw_file}\" -p{password} -mhe"
    if subprocess.call(encrypt_cmd, creationflags=DETACHED_PROCESS):
        raise EncryptError
    encrypt_test_cmd = f".\\bin\\7z.exe t \"{encrypted_file}.7z\" -p{password}"
    if subprocess.call(encrypt_test_cmd, creationflags=DETACHED_PROCESS):
        raise EncryptTestError
    os.rename(f"{encrypted_file}.7z", f"{encrypted_file}")
    os.remove(raw_file)


def mkv_merger(file: str, pretended_file: str, output: str) -> None:
    """
    使用 mkvmerge 将文件已附件的形式添加到 mkv 文件中

    Arguments:
        file -- 需要处理的文件
        pretended_file -- 伪装的视频文件
        output -- 生成的 mkv 文件
    """
    merger_cmd = f".\\bin\\mkvmerge.exe --output \"{output}\" " +\
                 f"--language 0:zh --language 1:zh \"{pretended_file}\" " +\
        "--attachment-name attachment " +\
        "--attachment-mime-type application/octet-stream " +\
                 f"--attach-file \"{file}\" " +\
        "--track-order 0:0,0:1"
    if subprocess.call(merger_cmd, creationflags=DETACHED_PROCESS):
        raise MergeError


def extractor(file: str) -> None:
    """
    文件提取

    Arguments:
        file -- 已伪装的MKV文件
        password -- 密码
    """
    dir = os.path.dirname(file)
    tmp_file = str(uuid4())
    attachment = os.path.join(dir, f'{tmp_file}')
    mkv_extractor(file, attachment)
    if os.path.exists(attachment):
        os.remove(file)
        n = len(os.listdir(dir))
        decryptor(attachment, dir, PASSWORD)
        if n+1 == len(os.listdir(dir)):
            os.remove(attachment)


def merger(file: str, video: str):
    dir = os.path.dirname(file)
    attachment = os.path.join(dir, "attachment")
    encryptor(file, attachment, PASSWORD)
    n = len(os.listdir(dir))
    new_name = file.replace('.mp4', '.mkv')
    mkv_merger(attachment, video, new_name)
    if len(os.listdir(dir)) == n+1:
        os.remove(attachment)
    else:
        raise MergeError


def get_files(dir: str) -> list:
    """
    获取目录下所有文件

    Arguments:
        dir -- 指定目录

    Returns:
        文件列表
    """
    files_list = []
    for root, _, files in os.walk(dir):
        for f in files:
            files_list.append(os.path.join(root.replace('\\', '/')+"/", f))
    return files_list


def get_all_mp4(files: list):
    return [file for file in files if file.endswith('.mp4')]


def get_all_mkv(files: list):
    return [file for file in files if file.endswith('.mkv')]


def generate_md5(file) -> str:
    m = md5()
    with open(file, mode='rb') as f:
        while True:
            data = f.read(1024*1024*20)
            if len(data) == 0:
                break
            m.update(data)
    return m.hexdigest()


def rename_and_md5(dir: str):
    files = get_files(dir)
    if len(files) == 1:
        os.rename(files[0], os.path.join(dir, 'Movie.mkv'))
    else:
        for file in files:
            newname = os.path.join(dir, file.split(' - ')[-1])
            os.rename(file, newname)
    new_files = get_all_mkv(get_files(dir))
    with open(os.path.join(dir, 'Validation.md5'), mode='w+', encoding='utf8') as f:
        for file in new_files:
            f.write(f"{generate_md5(file)} *{os.path.basename(file)}\n")


def split_dir(multi_dir: str) -> list:
    files = []
    start = 0
    while True:
        index = multi_dir.find(';', start)
        file = multi_dir[0:index]
        if index == -1:
            files.append(multi_dir)
            break
        elif os.path.isfile(file):
            files.append(file)
            multi_dir = multi_dir[index+1:]
            start = 0
        else:
            start = index+1
    return files
