import json
import os
import pickle
from django.shortcuts import render, redirect
import base64
import cv2
from django.http import StreamingHttpResponse
import face_recognition
from .tasks import registerStudent
from .models import Student, Department, Division, TempFileTest, Classrooms
from .predict import predict
from .threading import CameraWidget

def home_redirect(request):
    return redirect('studentregister')

def gen_frames(model):
    camera = cv2.VideoCapture(1)

    while True:
        _, frame = camera.read()
        print(predict(frame, model))
        #print(frame.shape)
        frame = cv2.imencode('.jpeg', frame)[1].tobytes()
        yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

        if cv2.waitKey(1) == 13:
            camera.release()
            cv2.destroyAllWindows()
            break

def vidfeed(request, dept, div):
    for_path = Student.objects.all()[0]
    path_model = for_path.img1.path
    path_model = os.path.split(path_model)
    for _ in range(4):
        path_model = os.path.split(path_model[0])
    path_model = f"{path_model[0]}\\models\\{dept}\\{div}\\model.pkl"
    #t1= CameraWidget(dept, div, path_model)
    file = open(path_model, 'rb')
    model = pickle.load(file)
    file.close()
    #t1.start()
    #print(t1)
    return StreamingHttpResponse(gen_frames(model),content_type='multipart/x-mixed-replace; boundary=frame')
    #return StreamingHttpResponse(t1.gen_frames(),content_type='multipart/x-mixed-replace; boundary=frame')

def test_page(request, dept, div):
    return render(request, 'student/base.html', {"dept":dept, "div":div})

def home_page(request):
    return render(request, 'index.html')

def student_home(request):
    divs = Division.objects.all() 
    depts = Department.objects.all()
    context = {}
    context['dept'] = depts
    context['div'] = divs
    if request.method =="POST":
        imgs = json.loads(request.POST['images'])
        name = request.POST['name']
        usn = request.POST['usn']
        dept = Department.objects.get(name=request.POST['dept'])
        div = Division.objects.get(div_name=request.POST['div'])
        registerStudent.delay(name, usn, dept.id, div.id, imgs)
        return redirect('studentregister')
    return render(request, 'student/register.html', context)

def classromm_list(request):
    context = {}
    context['classrooms'] = Classrooms.objects.all()
    return render(request, 'student/classrooms.html', context)

def register_class(request):
    context = {}
    context['classrooms'] = Classrooms.objects.all()
    context['depts'] = Department.objects.all()
    context['divs'] = Division.objects.all()
    if request.method == "POST":
        cno = request.POST.get("cno")
        dept = request.POST.get("dept")
        div = request.POST.get("div")
        cip = request.POST.get("cip")

        classObj = Classrooms.objects.create(
            cno=cno,
            dept = Department.objects.get(name=dept),
            div = Division.objects.get(div_name=div),
            cip = cip
        )
        classObj.save()
        return redirect('classrooms')
    return render(request, 'student/registerclass.html', context)

