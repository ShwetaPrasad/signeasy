import os
import shutil
from base64 import b64decode, b64encode

from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.files import File
from django.http import JsonResponse
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from rest_framework.decorators import api_view

from .models import Access, Document, Event 


@swagger_auto_schema(methods=['post'],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['file_name','file_content'],
        properties={
            'file_name': openapi.Schema(type=openapi.TYPE_STRING),
            'file_content': openapi.Schema(type=openapi.TYPE_STRING)
        }
    ),
    responses={200: 'file uploaded'})
@api_view(['POST'])
def upload(request):
    try:
        user = request.user
        file_name = request.data['file_name']
        file_content = str(request.data['file_content'])
        
        document = Document.objects.create(name=file_name)
        Event.objects.create(user=user, document=document.id, action='upload')
        Access.objects.create(user=user, document=document, role='OWNER')

        target_path = os.path.join(settings.STORAGE_PATH, str(document.id))
        if not os.path.exists(target_path):
            os.mkdir(target_path)

        target_file = os.path.join(target_path, file_name)
        with open(target_file, "w") as text_file:
            text_file.write(str(b64decode(file_content), encoding="utf-8"))

        response = {
            'document_id': document.id,
            'status_message': 'document uploaded'
        }
        status = 200
    except Exception as e:
        print(e)
    finally:
        return JsonResponse(response, status=status)


@swagger_auto_schema(methods=['get'],
    manual_parameters=[openapi.Parameter('document_id', openapi.IN_QUERY, description="document id", type=openapi.TYPE_STRING)],
    responses={200: 'file downloaded', 400: 'document does not exist', 401: 'user does not have access'})
@api_view(['GET'])
def download(request):
    try:
        user = request.user
        document_id = request.query_params['document_id']
    
        document = Document.objects.get(id=document_id)

        if Access.objects.filter(document=document,user=user, role__in=['OWNER','COLLABORATOR']).exists():
            target_path = os.path.join(settings.STORAGE_PATH, str(document.id))
            target_file = os.path.join(target_path, document.name)

            with open(target_file, "rb") as text_file:
                encoded_string = str(b64encode(text_file.read()), encoding="utf-8")
            
            response = {
                'file_content': encoded_string,
                'status_message': f'document_id:{document_id}, fetched content'
            }
            status = 200
        else:
            response = {'status_message': f'user:{user.username} does not have access to download the file'}
            status = 401
    except Document.DoesNotExist:
        response = {'status_message': f'document:{document_id} does not exist'}
        status = 400
    except Exception as e:
        print(e)
    finally:
        return JsonResponse(response, status=status)


@swagger_auto_schema(methods=['post'],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['document_id','file_content'],
        properties={
            'document_id': openapi.Schema(type=openapi.TYPE_STRING),
            'file_content': openapi.Schema(type=openapi.TYPE_STRING)
        }
    ),
    responses={200: 'file edited', 400: 'document does not exist'})
@api_view(['POST'])
def edit(request):
    try:
        user = request.user
        file_content =  request.data['file_content']
        document_id = request.data['document_id']

        document = Document.objects.get(id=document_id)

        user_has_access = Access.objects.filter(document=document,user=user, role__in=['OWNER','COLLABORATOR']).exists()

        if document.is_locked:
            status_message = "document is locked"
            status = 200
        elif not user_has_access:
            status_message = "user does not have edit access"
            status = 401
        else:
            document.is_locked = True
            document.save()

            target_path = os.path.join(settings.STORAGE_PATH, str(document.id))
            target_file = os.path.join(target_path, document.name)

            with open(target_file, "w") as text_file:
                text_file.write(str(b64decode(file_content), encoding="utf-8"))
            
            Event.objects.create(user=user, document=document.id, action='edit')     
            status_message = "Document updated"

            document.is_locked = False
            document.save()
        
        response = {'status_message': status_message}
        status = 200
    except Document.DoesNotExist:
        response = {'status_message': f'document {document_id} does not exist'}
        status = 400
    except Exception as e:
        print(e)
    finally:
        return JsonResponse(response, status=status)


@swagger_auto_schema(methods=['delete'],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['document_id'],
        properties={
            'document_id': openapi.Schema(type=openapi.TYPE_STRING)
        },
    responses={200: 'file deleted', 400: 'document does not exist', 401: 'user is not an owner'}))
@api_view(['DELETE'])
def delete(request):
    try:
        user = request.user
        document_id = request.data['document_id']

        document = Document.objects.get(id=document_id)

        if Access.objects.filter(user=user, document=document, role='OWNER').exists():
            Event.objects.create(user=user, document=document.id, action='delete')
            response = {'status_message': f'document {document.id} is deleted'}
            status = 200
            
            target_path = os.path.join(settings.STORAGE_PATH, str(document.id))
            shutil.rmtree(target_path)
            document.delete()
        else:
            response = {'status_message': f'user: {user.username} is not an owner'}
            status = 401
    except Document.DoesNotExist:
        response = {'status_message': f'document id:{document_id} does not exist'}
        status = 400
    except Exception as e:
        print(e)
    finally:
        return JsonResponse(response, status=status)


@swagger_auto_schema(methods=['post'],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['document_id','collaborator'],
        properties={
            'document_id': openapi.Schema(type=openapi.TYPE_STRING),
            'collaborator': openapi.Schema(type=openapi.TYPE_STRING)
        }
    ),
    responses={200: 'file shared'})
@api_view(['POST'])
def share(request):
    try:
        user = request.user
        document_id = request.data['document_id']
        collaborator = request.data['collaborator']

        document = Document.objects.get(id=document_id)

        if Access.objects.filter(document=document.id, user=user, role='OWNER').exists():
            collaborator = User.objects.get(username=collaborator)
            if Access.objects.filter(document=document, user=collaborator, role='COLLABORATOR').exists():
                response = {'status_message': f'user: {collaborator.username} has already access to {document.id}'}
            else:
                Event.objects.create(user=user, document=document.id, action='share')
                Access.objects.create(user=collaborator, document=document, role='COLLABORATOR')
                response = {'status_message': f'shared document with {collaborator.username}'}
            status = 200
        else:
            response = {'status_message': f'{user.username} is not an owner'}
            status = 401
    except Document.DoesNotExist:
        response = {'status_message': f'document {document_id} does not exist'}
        status = 400
    except User.DoesNotExist:
        response = {'status_message': f'user {collaborator} does not exist'}
        status = 400
    except Exception as e:
        print(e)
    finally:
        return JsonResponse(response, status=status)