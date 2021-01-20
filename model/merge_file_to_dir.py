#!/usr/bin/python

import re
import os
import shutil

# 将文件按照文件名复制到对应的目录
def split_dir(src_path, dst_path):
  files = os.listdir(src_path)
  for file in files:
    matchObj = re.match("\d+[\w_]\d+[\w_]2[\w_]", file)  # '53_0_3'
    # matchObj = re.match("\d+[\w_]\d+", file) # '53_0'
    # matchObj = re.match("\d+", file) # '53'
    if matchObj:
        list = matchObj.group().split('_')
        dir = list[1]
        print('dir: ' + dir)
        if os.path.isdir(dst_path +'/' + dir):
            shutil.copyfile(src_path + '/' + file, dst_path + '/' + dir + '/' + file)
        else:
            os.mkdir(dst_path + '/' + dir)
            shutil.copyfile(src_path + '/' + file, dst_path + '/' + dir + '/' + file)
    else:
        print('No Match')


if __name__ == '__main__':
  split_dir("/Volumes/t5/prg/dataset/UTKFace/aligned&cropped-faces/UTKFace", "/Volumes/t5/prg/dataset/UTKFace/aligned&cropped-faces/UTKFace_GENDER_Asia")
