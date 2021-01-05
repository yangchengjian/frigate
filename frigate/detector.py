import base64
import cv2
import logging
import numpy as np
import tflite_runtime.interpreter as tflite
from frigate.util import yuv_region_2_rgb
from frigate.video import create_tensor_input

logger = logging.getLogger(__name__)

string_pred_age = ['1', '10', '100', '101', '103', '105', '11', '110', '111', '115', '116', '12', '13', '14', '15', '16', '17', '18', '19', '2', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '3', '30', '31', '32', '33', '34', '35', '36', '37', '38', '39', '4', '40', '41', '42', '43', '44', '45', '46', '47',
                   '48', '49', '5', '50', '51', '52', '53', '54', '55', '56', '57', '58', '59', '6', '60', '61', '62', '63', '64', '65', '66', '67', '68', '69', '7', '70', '71', '72', '73', '74', '75', '76', '77', '78', '79', '8', '80', '81', '82', '83', '84', '85', '86', '87', '88', '89', '9', '90', '91', '92', '93', '95', '96', '99']
string_pred_gen = ['F', 'M']

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
    print(f"region_rgb.shape: {region_rgb.shape}")
    ## transform region_rgb to region_bgr（realy need?）
    region_bgr = cv2.cvtColor(region_rgb, cv2.COLOR_RGB2BGR)
    print(f"region_bgr.shape: {region_bgr.shape}")

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
        print(f"region_face_rgb.shape: {region_face_rgb.shape}")

        ## adapting tensorflow input format
        tensor_input_raw = cv2.resize(region_face_rgb, (224,224))
        print(f"tensor_input_raw.shape: {tensor_input_raw.shape}")
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
        print(f"age: {string_pred_age[index_pred_age]}, gender: {string_pred_gen[index_pred_gender]}")
        base64_region_face =  base64.b64encode(cv2.imencode('.jpg', region_face_rgb)[1]).decode('utf-8')
        
        prezic_result.append({
            'timestamp_detect': timestamp,
            'age': string_pred_age[index_pred_age], 
            'gender': string_pred_gen[index_pred_gender], 
            'face': base64_region_face
            })

    return prezic_result
