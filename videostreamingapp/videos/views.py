from django.shortcuts import render, redirect, get_object_or_404,HttpResponse
from .forms import SignUpForm
from django.contrib.auth.decorators import login_required
from .models import Video
#from .forms import VideoForm
import cv2
import threading
from django.http import StreamingHttpResponse
from django.views.decorators import gzip
from django.http import HttpResponse
import os
from django.shortcuts import get_object_or_404
from pytube import YouTube
from django.db.models import Q


@login_required(login_url='/login')
def home(request):
    return render(request,"main/home.html",{})


def register(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Redirect to login page after successful registration
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})

# def create_video(request):
#     if request.method == 'POST':
#         form = VideoForm(request.POST)
#         if form.is_valid():
#             video = form.save(commit=False)
#             video.owner = request.user
#             video.save()
#             return redirect("/create_video")
#     else:
#         form = VideoForm()
#     return render(request, 'main/create_video.html', {'form': form})

def create_video(request):
    search_query = request.GET.get('search')
    datas = Video.objects.all()
    print("datas",datas)
    if search_query:
        datas = datas.filter(
            Q(name__icontains=search_query) |
            Q(video_url__icontains=search_query) 
            
        )
        
        video_data = []
        for video in datas:
            video_info = {
                'video': video,
                
            }
            video_data.append(video_info)

        return render(request, "main/create_video.html", {"datas": video_data})
    
    if request.method == 'POST':
        obj = Video()
        obj.name = request.POST.get('name')
        obj.video_url = request.POST.get('video_url')
        

        obj.save()
        return redirect('/create_video')
    datas = Video.objects.all()
    return render(request,"main/create_video.html",{"datas":datas})

# def update_video(request, video_id):
#     video = get_object_or_404(Video, pk=video_id)
#     if request.method == 'POST':
#         form = VideoForm(request.POST, instance=video)
#         if form.is_valid():
#             form.save()
#             return redirect('/update_video')  # Redirect to video list page after updating video
#     else:
#         form = VideoForm(instance=video)
#     return render(request, 'main/update_video.html', {'form': form})

def update_video(request):
    video_id = request.GET.get('video_id')
    data = Video.objects.get(id=video_id)
    if request.method == 'POST':
        data.name = request.POST.get('name')
        data.video_url = request.POST.get('video_url')

        data.save(update_fields=['name','video_url'])
        return redirect('/create_video')
    return render(request,"main/update_video.html",{'data':data})

# def delete_video(request, video_id):
#     video = get_object_or_404(Video, pk=video_id)
#     if request.method == 'POST':
#         video.delete()
#         return redirect('/create_video')  # Redirect to video list page after deleting video
#     return render(request, 'main/delete_video.html', {'video': video})

def delete_video(request):
    video_id = request.GET.get('video_id')
    Video.objects.get(id=video_id).delete()
    return redirect('/create_video')




class VideoCamera:
    def __init__(self, video_url):
        # Use pytube to extract the direct video URL
        yt = YouTube(video_url)
        stream = yt.streams.filter(file_extension='mp4').first()
        direct_video_url = stream.url
        
        # Use the direct video URL for cv2.VideoCapture
        self.video = cv2.VideoCapture(direct_video_url)
        
    def __del__(self):
        self.video.release()

    def get_frame(self):
        success, image = self.video.read()
        if success:
            return image
        else:
            return None

    def getf(self):
        return self.get_frame()

# class VideoCamera:
#     def __init__(self, video_url):
#         self.video = cv2.VideoCapture(video_url)

#     def __del__(self):
#         self.video.release()

#     def get_frame(self):
#         print("2")
#         # Capture a frame from the video
#         success, image = self.video.read()
#         if success:
#             return image
            
#             # ret, jpeg = cv2.imencode('.jpg', image)
#             # return jpeg.tobytes()
#         else:
#             return None



#     def getf(self):
#         print("1")
#         # Call the get_frame method and return its result
#         return self.get_frame()

def gen(camera):
    while True:
        frame = camera.getf()
        if frame is not None:
            # Convert raw frame to MJPEG format
            _, jpeg = cv2.imencode('.jpg', frame)  # Convert frame to JPEG
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')
        else:
            break

@gzip.gzip_page
def video_feed(request):
    video_id = request.GET.get('video_id')
    print(video_id)
    video = get_object_or_404(Video, id=video_id)
    # video = Video.objects.get(id=video_id)
    print("video", video)
    video_camera = VideoCamera(video.video_url)
    print(video.video_url)
    print("video_camera", video_camera)
    return StreamingHttpResponse(gen(video_camera), content_type="multipart/x-mixed-replace; boundary=frame")

def handle_multiple_video_feeds(video_ids):
    threads = []

    for video_id in video_ids:
        # Create a new thread for each video feed
        thread = threading.Thread(target=video_feed, args=(video_id,))
        threads.append(thread)
        thread.start()

    # Join all the threads to ensure they complete
    for thread in threads:
        thread.join()



