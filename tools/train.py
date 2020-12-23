import numpy as np

import tensorflow as tf
#assert tf.__version__.startswith('2')

from tflite_model_maker import configs
from tflite_model_maker import ExportFormat
from tflite_model_maker import image_classifier
from tflite_model_maker import ImageClassifierDataLoader
from tflite_model_maker import model_spec

import matplotlib.pyplot as plt

import socket
import socks #PySocks
socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 1080)
socket.socket = socks.socksocket

# 从网络下载
# image_path = tf.keras.utils.get_file(
#       'flower_photos',
#       'https://storage.googleapis.com/download.tensorflow.org/example_images/flower_photos.tgz',
#       untar=True)
# data = ImageClassifierDataLoader.from_folder(image_path)

# 本地导入
data = ImageClassifierDataLoader.from_folder("/Users/yangchengjian/test")
train_data, test_data = data.split(0.9)

model = image_classifier.create(train_data)

loss, accuracy = model.evaluate(test_data)

model.export(export_dir='.', tflite_filename='test-age-model.tflite') # 导出模型
model.export(export_dir='.', label_filename='test-age-labels.txt', export_format=ExportFormat.LABEL)  # 导出标签

def get_label_color(val1, val2):
  if val1 == val2:
    return 'black'
  else:
    return 'red'

# Then plot 100 test images and their predicted labels.
# If a prediction result is different from the label provided label in "test"
# dataset, we will highlight it in red color.
plt.figure(figsize=(20, 20))
predicts = model.predict_top_k(test_data)
for i, (image, label) in enumerate(test_data.dataset.take(100)):
  ax = plt.subplot(10, 10, i+1)
  plt.xticks([])
  plt.yticks([])
  plt.grid(False)
  plt.imshow(image.numpy(), cmap=plt.cm.gray)

  predict_label = predicts[i][0][0]
  color = get_label_color(predict_label,
                          test_data.index_to_label[label.numpy()])
  ax.xaxis.label.set_color(color)
  plt.xlabel('Predicted: %s' % predict_label)
plt.show()