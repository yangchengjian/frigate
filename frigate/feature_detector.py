import cv2
import logging
import numpy as np
import tflite_runtime.interpreter as tflite

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

images = []


def detect_age_and_gender(frame, region):
    # logger.info(
    #     f"detect_age_and_gender frame: {frame}")
    logger.info(
        f"detect_age_and_gender region: {region}")

    faces = face_cascade.detectMultiScale(
        frame, scaleFactor=1.2, minNeighbors=5)
    for x, y, w, h in faces:

        tensor_input_raw = create_tensor_input(
        frame, (224, 224), (x, y, x + w, y + h))
        # logger.info(
        #     f"detect_age_and_gender tensor_input_raw: {tensor_input_raw}")

        tensor_input_raw = tensor_input_raw.astype('float')
        tensor_input_raw = tensor_input_raw / 255
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
        prezic_age = string_pred_age[index_pred_age]
        prezic_gender = string_pred_gen[index_pred_gender]

        logger.info(f"prezic_age: {prezic_age}, prezic_gender: {prezic_gender}")

    return prezic_age, prezic_gender, frame
