from django.shortcuts import render
import datetime
import random
import string
from django.db.models import Q
from .models import *
import json
import os
from .serializers import *
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework import viewsets
from django.contrib.auth import authenticate
from django.contrib.auth import logout, login
from rest_framework.authtoken.models import Token
from core.customPagination import CustomPagination
from django.core.files.storage import default_storage

# Create your views here.

class ApigetUserType(APIView):
	authentication_classes = [SessionAuthentication]
	permission_classes = [AllowAny]

	def post(self, request):
		data=request.data
		usr = User.objects.get(username=data['username'])
		if not usr:
			return Response({'status':False, 'message':'User not found.'}, status=status.HTTP_404_NOT_FOUND)
		userio = usuario.objects.filter(usr=usr).first()
		if userio:
			if userio.tipo_usuario in [1]:
				return Response({'status':False, 'message':'The user you are trying to log in with is invalid.', 'title': 'Verify your information'}, status=status.HTTP_400_BAD_REQUEST)
		if usr.is_active == False:
			return Response({'status':False, 'message':'Your account has been deactivated. Please contact an administrator.', 'title': 'Account deactivated'}, status=status.HTTP_400_BAD_REQUEST)

		print(f"User {usr.username} logged in successfully.")
		return Response({'status':True, 'tipo': usr.usuario.tipo_usuario, 'id': usr.usuario.id, 'username': usr.usuario.usr.email})

class LogoutView(APIView):

	def post(self, request):
		try:
			logout(request)
			return Response(status=status.HTTP_204_NO_CONTENT)
		except Token.DoesNotExist:
			return Response({'error': 'Token not found'}, status=status.HTTP_400_BAD_REQUEST)

class UsuariosViewSet(viewsets.ModelViewSet):
	queryset = usuario.objects.all().order_by('-id')
	serializer_class = usuariosSerializer
	permission_classes = [AllowAny]  # Permite acceso sin autenticación
	pagination_class = CustomPagination

	@action(detail=False, methods=['post'], url_path='create-account')
	def Create_contribuyent(self, request):
		data = request.data
		dat_usr = data.get('usuario')
		if User.objects.filter(email=dat_usr['email']).exists():
			return Response({'status': False, 'message': 'El email ya está registrado.'}, status=400)

		enf = User.objects.create(
			first_name=dat_usr['first_name'],
			last_name=dat_usr['last_name'],
			email=dat_usr['email'].strip(),
			username=dat_usr['email'],
			is_staff=True,
			is_superuser=False
		)
		enf.set_password(dat_usr['password'])
		enf.save()
		userio = usuario.objects.create(
			usr=enf,
			tipo_usuario=2,
			grado=dat_usr['grado'],
			tareastes=None,
			bocabularioasing=None,
			grupo=None,
		)
		userio.save()

		return Response({'status': True, 'message': 'Usuario registrado correctamente.'})

	def list(self, request):
		nombre = request.query_params.get('nombre', '').strip().lower()  # Re-enable filtering by name
		queryset = self.get_queryset()
		if nombre:
			queryset = queryset.filter(name__icontains=nombre)
		queryset = queryset.order_by('id')
		queryset = self.filter_queryset(queryset)

		page = self.paginate_queryset(queryset)
		if page is not None:
			serializer = self.get_serializer(page, many=True)
			return self.get_paginated_response(serializer.data)

		serializer = self.get_serializer(queryset, many=True)
		return Response(serializer.data)

class abcedarioViewSet(viewsets.ModelViewSet):
	queryset = abcedario.objects.all().order_by('id')
	serializer_class = abcedarioSerializer
	permission_classes = [AllowAny]  # Permite acceso sin autenticación
	pagination_class = CustomPagination

	def list(self, request):
		nombre = request.query_params.get('nombre', '').strip().lower()

		queryset = self.get_queryset()
		if nombre:
			queryset = queryset.filter(name__icontains=nombre)
		queryset = queryset.order_by('id')
		queryset = self.filter_queryset(queryset)

		page = self.paginate_queryset(queryset)
		if page is not None:
			serializer = self.get_serializer(page, many=True)
			return self.get_paginated_response(serializer.data)

		serializer = self.get_serializer(queryset, many=True)
		return Response(serializer.data)

class bocabularioViewSet(viewsets.ModelViewSet):
	queryset = bocabulario.objects.all().order_by('-id')
	serializer_class = bocabularioSerializer
	permission_classes = [AllowAny]  # Permite acceso sin autenticación
	pagination_class = CustomPagination

	def destroy(self, request, pk=None):
		try:
			enf = bocabulario.objects.get(id=pk)

			enf.delete()
			return Response({'status': True, 'message': 'Bocabulario eliminado correctamente.'})
		except bocabulario.DoesNotExist:
			return Response({'status': False, 'message': 'Bocabulario no encontrado.'}, status=404)

	def list(self, request):
		nombre = request.query_params.get('nombre', '').strip().lower()

		queryset = self.get_queryset()
		if nombre:
			queryset = queryset.filter(name__icontains=nombre)
		queryset = queryset.order_by('-id')
		queryset = self.filter_queryset(queryset)

		page = self.paginate_queryset(queryset)
		if page is not None:
			serializer = self.get_serializer(page, many=True)
			return self.get_paginated_response(serializer.data)

		serializer = self.get_serializer(queryset, many=True)
		return Response(serializer.data)

	def create(self, request):
		data = request.data
		archivo = request.FILES.get('archivo')  # Obtener el archivo enviado
		if not archivo.name.endswith(('.jpg', '.png', '.pdf')):
			return Response({'status': False, 'message': 'Tipo de archivo no permitido.'}, status=400)
		if archivo:
			# Guardar el archivo en la carpeta 'media/missAna' usando default_storage
			file_path = f'media/missAna/{archivo.name}'
			saved_file = default_storage.save(file_path, archivo)

			# Generar la ruta relativa del archivo
			relative_url = f"/{saved_file}"  # Asegurar que comience con "/"
			publico = data.get('publico', 'false').lower() == 'true'

			# Crear el objeto del modelo bocabulario
			enf = bocabulario.objects.create(
				nombre=data['nombre'],
				descripcion=data.get('descripcion', ''),
				texturl=relative_url,  # Guardar la ruta relativa en el campo img
				texestanol=data['texestanol'],
				texingles=data['texingles'],
				publico=publico,
				tipo= data['tipo'],
			)
			enf.save()
			return Response({'status': True, 'message': 'Bocabulario registrado correctamente.', 'img_url': relative_url})
		else:
			return Response({'status': False, 'message': 'No se proporcionó un archivo.'}, status=status.HTTP_400_BAD_REQUEST)

	def update(self, request, pk=None):
		try:
			enf = bocabulario.objects.get(id=pk)
			data = request.data
			editimg = data.get('editimg', 'false').lower() == 'true'

			if editimg:
				archivo = request.FILES.get('archivo')
				if archivo and archivo.name.endswith(('.jpg', '.png', '.pdf')):
					file_path = f'media/missAna/{archivo.name}'
					saved_file = default_storage.save(file_path, archivo)
					relative_url = f"/{saved_file}"
					enf.texturl = relative_url
				elif archivo:
					return Response({'status': False, 'message': 'Tipo de archivo no permitido.'}, status=400)

			enf.nombre = data.get('nombre', enf.nombre)
			enf.descripcion = data.get('descripcion', enf.descripcion)
			enf.texestanol = data.get('texestanol', enf.texestanol)
			enf.texingles = data.get('texingles', enf.texingles)
			enf.publico = data.get('publico', str(enf.publico)).lower() == 'true'
			enf.tipo = data.get('tipo', enf.tipo)
			enf.save()

			return Response({'status': True, 'message': 'Bocabulario actualizado correctamente.', 'img_url': enf.texturl})
		except bocabulario.DoesNotExist:
			return Response({'status': False, 'message': 'Bocabulario no encontrado.'}, status=404)

class CustomTokenCreateView(APIView):
	permission_classes = [AllowAny]

	def post(self, request):
		username = request.data.get('username')
		password = request.data.get('password')
		user = authenticate(username=username, password=password)

		if user is not None:
			usru = usuario.objects.get(usr=user)
			# if usru.tipo_usuario in [1, 6, 12]:
			# 	return Response({'error': 'Usuario no autorizado'}, status=status.HTTP_400_BAD_REQUEST)
			token, created = Token.objects.get_or_create(user=user)
			login(request, user)
			return Response({
                'auth_token': token.key,
                'status': True,
                'username': user.username,
                'type': usru.tipo_usuario,
                'id': usru.id
            })
			# makeLogs(request,'Login', 'has logged in')
			# return Response({'auth_token': token.key, 'status': True})
		else:
			return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
