import cv2
from gc import collect


def pick_color(img):
    S_red = 0
    S_green = 0
    S_blue = 0
    n = 0
    height, width, channels = img.shape
    for y in range(0, height, 3):
        for x in range(0, width, 4):
            try:
                color = img[y, x]
                S_red = S_red + int(color[0])
                S_green = S_green + int(color[1])
                S_blue = S_blue + int(color[2])
                n = n + 1
                del color
                if x % 90 == 0:
                    collect()
            except:
                pass

    return (round(S_red / n), round(S_green / n), round(S_blue / n))

def upload_models():
    face1 = "model_files\\opencv_face_detector.pbtxt"
    face2 = "model_files\\opencv_face_detector_uint8.pb"
    age1 = "model_files\\age_deploy.prototxt"
    age2 = "model_files\\age_net.caffemodel"
    gen1 = "model_files\\gender_deploy.prototxt"
    gen2 = "model_files\\gender_net.caffemodel"

    face = cv2.dnn.readNet(face2, face1)

    age = cv2.dnn.readNet(age2, age1)

    gen = cv2.dnn.readNet(gen2, gen1)
    
    print('models_ulpoaded')
    
    return face, age, gen


def analize(filename_: str, face, age, gen):
    res = []
    
    MODEL_MEAN_VALUES = (78.4263377603, 87.7689143744, 114.895847746)

    la = [(0, 2), (4, 6), (8, 12), (15, 20), (25, 32), (38, 43), (48, 53), (60, 100)]
    lg = ["Male", "Female"]

    image = cv2.imread(filename_)

    fr_h = image.shape[0]
    fr_w = image.shape[1]
    blob = cv2.dnn.blobFromImage(image, 1.0, (300, 300), [104, 117, 123], True, False)

    face.setInput(blob)
    detections = face.forward()

    faceBoxes = []
    for i in range(detections.shape[2]):

        # Bounding box creation if confidence > 0.7
        confidence = detections[0, 0, i, 2]
        if confidence > 0.7:

            x1 = int(detections[0, 0, i, 3] * fr_w)
            y1 = int(detections[0, 0, i, 4] * fr_h)
            x2 = int(detections[0, 0, i, 5] * fr_w)
            y2 = int(detections[0, 0, i, 6] * fr_h)

            faceBoxes.append([x1, y1, x2, y2])

            cv2.rectangle(
                image, (x1, y1), (x2, y2), (0, 255, 0), int(round(fr_h / 150)), 8
            )

    if not faceBoxes:
        print("No face detected")
        return res
    else:

        # Final results (otherwise)
        # Loop for all the faces detected
        for faceBox in faceBoxes:

            # Extracting face as per the faceBox
            face = image[faceBox[1] : faceBox[3], faceBox[0] : faceBox[2]]

            # Extracting the main blob part
            blob = cv2.dnn.blobFromImage(
                face, 1.0, (227, 227), MODEL_MEAN_VALUES, swapRB=False
            )

            # Prediction of gender
            gen.setInput(blob)
            genderPreds = gen.forward()
            gender_ = lg[genderPreds[0].argmax()]

            # Prediction of age
            age.setInput(blob)
            agePreds = age.forward()

            age_ = la[agePreds[0].argmax()]
            if age_ != (48, 53) and age_ != (60, 100) and age_ != (0, 2):
                age_ = la[agePreds[0].argmax() + 1]
            else:
                age_ = la[agePreds[0].argmax()]

            try:
                color_ = pick_color(
                    image[faceBox[3] : image.shape[1], faceBox[0] : faceBox[2]]
                )
            except:
                color_ = (0, 0, 0)

            res.append([gender_, age_, color_])

        return res
