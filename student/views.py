import json
from django.shortcuts import render, redirect
import base64
import cv2
from django.http import StreamingHttpResponse
import face_recognition
from .tasks import registerStudent
from .models import Student, Department, Division, TempFileTest

# Create your views here.
def gen_frames():
    cap = cv2.VideoCapture(1)

    while True:
        ret, img = cap.read()

        face = cv2.resize(img,(500,500))

        frame = cv2.imencode('.jpg', face)[1].tobytes()
        yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

        if cv2.waitKey(1) == 13:
            break
            cap.release()
            cv2.destroyAllWindows()

def vidfeed_dataset(request):
    return StreamingHttpResponse(gen_frames(),content_type='multipart/x-mixed-replace; boundary=frame')

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

def test_page(request):
    return render(request, 'student/test.html')

