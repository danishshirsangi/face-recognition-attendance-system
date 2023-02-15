from face_attendace.celery import app
from .models import Student, Department, Division
import base64
import face_recognition
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import TemporaryUploadedFile
import json
from face_recognition.face_recognition_cli import image_files_in_folder
import os
import math
from sklearn import neighbors
import pickle

@app.task
def trainModel(train_dir, model_path = None, n_neighbors=None, knn_algo='ball_tree', verbose=False, usn='general'):
    X = []
    y = [] #USN Folder Name given string
    for img_path in image_files_in_folder(train_dir):
        image = face_recognition.load_image_file(img_path)
        face_bounding_boxes = face_recognition.face_locations(image)

        X.append(face_recognition.face_encodings(image, known_face_locations=face_bounding_boxes)[0])
        y.append(usn)
        
    if n_neighbors is None:
        n_neighbors = int(round(math.sqrt(len(X))))
        if verbose:
            print("Chose n_neighbors automatically:", n_neighbors)
    knn_clf = neighbors.KNeighborsClassifier(n_neighbors=n_neighbors, algorithm=knn_algo, weights='distance')
    knn_clf.fit(X, y)

    # Save the trained KNN classifier
    if model_path is not None:
        with open(model_path, 'wb') as f:
            pickle.dump(knn_clf, f)
    #todo - use get_or_create query here & no need to return knn_clf
    return knn_clf


@app.task
def registerStudent(name, usn, dept, div, imgs):
    tempFiles = []
    dept = Department.objects.get(id=dept)
    div = Division.objects.get(id=div)
    for i in range(len(imgs)):
        ct = imgs[f'image{i+1}']['content-type']
        nameF = f'image{i+1}.jpeg'
        imageData = imgs[f'image{i+1}']['data']
        imageData = base64.b64decode((imageData))
        file = TemporaryUploadedFile(name=nameF,content_type=ct,size=0,charset='base64')
        file.write(imageData)
        tempFiles.append(file)
    
    croppedFaces = []
    for img in tempFiles:
        fName = img.name
        imageSample = face_recognition.load_image_file(img)
        face_locations = face_recognition.face_locations(imageSample, number_of_times_to_upsample=0, model="cnn")
        #face_locations = face_recognition.face_locations(imageSample)
        for face_location in face_locations:
            top, right, bottom, left = face_location
            face_image = imageSample[top:bottom, left:right]
            pil_image = Image.fromarray(face_image)
            buff = BytesIO()
            pil_image.save(buff, format="png")
            new_image_string = base64.b64encode(buff.getvalue())
            new_image_string = base64.b64decode((new_image_string))
            croppedFace = TemporaryUploadedFile(name= fName, content_type='image/png',size=0,charset='utf-8')
            croppedFace.write(new_image_string)
            croppedFaces.append(croppedFace)
    del tempFiles

    #print(croppedFaces)
    stu = Student.objects.create(
        name = name,
        usn = usn,
        dept = dept,
        div = div,
        img1 = croppedFaces[0],
        img2 = croppedFaces[1],
        img3 = croppedFaces[2],
        img4 = croppedFaces[3],
        img5 = croppedFaces[4]
    )
    stu.save()
    del croppedFaces