import base64
import cv2
import logging
import numpy as np
import tflite_runtime.interpreter as tflite
from frigate.util import yuv_region_2_rgb
from frigate.video import create_tensor_input

logger = logging.getLogger(__name__)


string_pred_age = open('/age-labels.txt', 'r').read().split("\n")
string_pred_gen = open('/gender-labels.txt', 'r').read().split("\n")

interpreter_age = tflite.Interpreter(model_path="/age-model.tflite")
interpreter_age.allocate_tensors()

interpreter_gender = tflite.Interpreter(model_path="/gender-model.tflite")
interpreter_gender.allocate_tensors()

# # Get input and output tensors
input_details_age = interpreter_age.get_input_details()
output_details_age = interpreter_age.get_output_details()
input_shape_age = input_details_age[0]['shape']

input_details_gender = interpreter_gender.get_input_details()
output_details_gender = interpreter_gender.get_output_details()
input_shape_gender = input_details_gender[0]['shape']

face_cascade = cv2.CascadeClassifier("/haarcascade_frontalface_default.xml")

def detect_age_and_gender(frame, timestamp, region):
    logger.info(
        f"detect_age_and_gender region: {region}")
    
    prezic_result = []
    
    ## take a region from frame，and transfor to rgb
    ## (use yuv_region_2_rgb avoid region to beyond frame scope)
    region_rgb = yuv_region_2_rgb(frame, region)
    ## transform region_rgb to region_bgr（realy need?）
    region_bgr = cv2.cvtColor(region_rgb, cv2.COLOR_RGB2BGR)

    ## take region
    # frame_region = frame[region[1]: region[3], region[0]: region[2]]
    # print(f"frame_region.shape: {frame_region.shape}")
    ## transfrom to rgb
    # region_rgb = cv2.cvtColor(frame_region, cv2.COLOR_BGR2RGB)
    # print(f"region_rgb.shape: {region_rgb.shape}")

    region_gray = cv2.cvtColor(region_rgb, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(
            region_gray, scaleFactor=1.2, minNeighbors=3)
    print(f"faces: {faces}")
    for x, y, w, h in faces:

        region_face_rgb = region_rgb[y:y+h, x:x+w]

        ## adapting tensorflow input format
        tensor_input_raw = cv2.resize(region_face_rgb, (224,224))
        tensor_input_raw = tensor_input_raw.astype('float')
        tensor_input_raw = tensor_input_raw / 255
        tensor_input_raw = np.expand_dims(tensor_input_raw, axis = 0)
        tensor_input = np.array(tensor_input_raw, dtype=np.float32)

        # Predict
        # logger.info(
        #     f"detect_age_and_gender input_details_age: {input_details_age}")
        # logger.info(
        #     f"detect_age_and_gender output_details_age: {output_details_age}")
        # logger.info(
        #     f"detect_age_and_gender tensor_input: {tensor_input}")

        interpreter_age.set_tensor(
            input_details_age[0]['index'], tensor_input)
        interpreter_age.invoke()

        interpreter_gender.set_tensor(
            input_details_gender[0]['index'], tensor_input)
        interpreter_gender.invoke()

        output_data_age = interpreter_age.get_tensor(
            output_details_age[0]['index'])
        output_data_gender = interpreter_gender.get_tensor(
            output_details_gender[0]['index'])

        index_pred_age = int(np.argmax(output_data_age))
        index_pred_gender = int(np.argmax(output_data_gender))
        print(f"timestamp: {timestamp}, age: {string_pred_age[index_pred_age]}, gender: {string_pred_gen[index_pred_gender]}")
        # base64_region_face =  base64.b64encode(cv2.imencode('.jpg', region_face_rgb)[1]).decode('utf-8')
        
        prezic_result.append({
            'detect_frame_time': timestamp,
            'detect_frame_age': string_pred_age[index_pred_age], 
            'detect_frame_gender': string_pred_gen[index_pred_gender]
            # 'detect_frame_face': 'data:image/jpeg;base64,' + base64_region_face
            })

    return {'detect_frame_result': prezic_result}
