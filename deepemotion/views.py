from django.core.files.storage import FileSystemStorage
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth, TruncYear
from .forms import UploadFileForm
from deepface import DeepFace
from .models import Person
import tempfile
import os
import base64
from PIL import Image
import json
from faker import Faker
from datetime import datetime, timedelta
import random


def deep_emotion(request):
    return render(request, 'deepemotion.html')

def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        print(form.errors)
        if form.is_valid():
            file = request.FILES['file']
            fs = FileSystemStorage(location=tempfile.gettempdir())
            filename = fs.save(file.name, file)

            analysis = DeepFace.analyze(os.path.join(tempfile.gettempdir(), filename), actions=['emotion'])
            emotion = analysis[0]['dominant_emotion']

            # Store details in session
            request.session['emotion1'] = emotion
            request.session['name'] = request.POST['name']

            previous_uploads = [{
                'name': request.POST['name'],
                'temp_image_base64': image_to_base64(os.path.join(tempfile.gettempdir(), filename))
            }]
            request.session['previous_uploads'] = previous_uploads

            fs.delete(filename)

            return redirect('confirm')
    else:
        form = UploadFileForm()
    return render(request, 'upload.html', {'form': form})

def confirm(request):
    previous_uploads = request.session.get('previous_uploads', [])
    current_upload = previous_uploads[-1] if previous_uploads else None

    if current_upload:
        name = current_upload.get('name', '')
        temp_image_base64 = current_upload['temp_image_base64']
    else:
        name = request.session.get('name', '')
        temp_image_base64 = ''

    context = {
        'emotion1' : request.session.get('emotion1', ''),
        'name': name,
        'temp_image_base64': temp_image_base64,
    }

    return render(request, 'confirm.html', context)

def upload_second_file(request):
    name = request.GET.get('name')
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            fs = FileSystemStorage(location=tempfile.gettempdir())
            filename = fs.save(file.name, file)

            analysis = DeepFace.analyze(os.path.join(tempfile.gettempdir(), filename), actions=['emotion'])
            emotion = analysis[0]['dominant_emotion']

            # Update session with second emotion
            request.session['emotion2'] = emotion

            previous_uploads = request.session.get('previous_uploads', [])
            previous_uploads[-1]['temp_image_base64_2'] = image_to_base64(os.path.join(tempfile.gettempdir(), filename))
            request.session['previous_uploads'] = previous_uploads

            fs.delete(filename)

            return redirect('confirm_second')
    else:
        form = UploadFileForm()
    return render(request, 'upload_second.html', {'form': form, 'name': name})

def confirm_second(request):
    previous_uploads = request.session.get('previous_uploads', [])
    current_upload = previous_uploads[-1] if previous_uploads else None

    if current_upload:
        temp_image_base64_1 = current_upload.get('temp_image_base64', '')
        temp_image_base64_2 = current_upload.get('temp_image_base64_2', '')
    else:
        temp_image_base64_1 = ''
        temp_image_base64_2 = ''

    context = {
        'name': request.session.get('name', ''),
        'emotion1': request.session.get('emotion1', ''),
        'emotion2': request.session.get('emotion2', ''),
        'temp_image_base64_1': temp_image_base64_1,
        'temp_image_base64_2': temp_image_base64_2
    }

    return render(request, 'confirm_second.html', context)

def create_person(request):
    name = request.session.get('name', '')
    emotion1 = request.session.get('emotion1', '')
    emotion2 = request.session.get('emotion2', '')

    person = Person.objects.create(name=name, emotion1=emotion1, emotion2=emotion2)

    # Clear the session
    request.session.flush()

    return render(request, 'success.html', {'person': person})

def data_visualization(request):
    data = {}

    # Group data by day/month/year
    person_data = Person.objects.values('createDate').distinct().annotate(count=Count('id'))

    for item in person_data:
        date = item['createDate']
        date_key = date.strftime("%d/%m/%Y %H:%M")

        # Get unique values for each field
        unique_values = Person.objects.filter(createDate=date).values_list('name', 'emotion1', 'emotion2').distinct()

        # Convert the unique values queryset to lists
        name_list, emotion1_list, emotion2_list = zip(*unique_values)

        data[date_key] = {
            'name': list(name_list),
            'emotion1': list(emotion1_list),
            'emotion2': list(emotion2_list)
        }

    # Serialize data to JSON
    data_json = json.dumps(data)

    return render(request, 'data_visualization.html', {'data': data_json})

def populate_data_base(request):
    fake = Faker()
    emotions = ['anger', 'fear', 'sad', 'disgust', 'neutral', 'happy', 'surprise']
    start_date = datetime(2022, 1, 1)
    end_date = datetime(2023, 12, 31)

    for _ in range(100):
        random_seconds = random.randint(0, int((end_date - start_date).total_seconds()))
        random_date = start_date + timedelta(seconds=random_seconds)

        person = Person(
            name=fake.name(),
            emotion1=random.choice(emotions),
            emotion2=random.choice(emotions),
            createDate=random_date
        )
        person.save()

def image_to_base64(image_path):
    with open(image_path, 'rb') as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')
