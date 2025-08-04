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
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework import viewsets
from django.contrib.auth import authenticate
from django.contrib.auth import logout, login
from rest_framework.authtoken.models import Token
from core.customPagination import CustomPagination
from django.core.files.storage import default_storage
from django.utils import timezone

# Create your views here.

class ApigetUserType(APIView):
	authentication_classes = [SessionAuthentication]
	permission_classes = [AllowAny]

	def post(self, request):
		data=request.data
		usr = User.objects.get(username=data['username'])
		if not usr:
			return Response({'status':False, 'message':'User not found.'}, status=status.HTTP_404_NOT_FOUND)
		# userio = usuario.objects.filter(usr=usr).first()
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
			tipo_usuario=1,
			grado=dat_usr['grado'],
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

# ========== TASK MANAGEMENT VIEWSETS ==========

class TareasViewSet(viewsets.ModelViewSet):
	queryset = tareas.objects.all().order_by('-fecha_creacion')
	serializer_class = TareasSerializer
	permission_classes = [IsAuthenticated]
	pagination_class = CustomPagination

	def get_queryset(self):
		user = self.request.user
		usuario_obj = usuario.objects.get(usr=user)
		
		# Teachers can see all tasks, students only see assigned tasks
		if usuario_obj.tipo_usuario == usuario.TiposUsuario.MAESTRO:
			return tareas.objects.all().order_by('-fecha_creacion')
		else:
			# Students see tasks assigned to them
			asignaciones = TareaAsignacion.objects.filter(
				Q(estudiante=usuario_obj) | Q(grupo=usuario_obj.grupo)
			)
			return tareas.objects.filter(asignaciones__in=asignaciones).distinct().order_by('-fecha_creacion')

	def perform_create(self, serializer):
		user = self.request.user
		usuario_obj = usuario.objects.get(usr=user)
		
		# Only teachers can create tasks
		if usuario_obj.tipo_usuario != usuario.TiposUsuario.MAESTRO:
			raise PermissionError("Solo los maestros pueden crear tareas")
		
		serializer.save(creado_por=usuario_obj)

	def create(self, request):
		"""Create task with optional file attachment"""
		user = request.user
		usuario_obj = usuario.objects.get(usr=user)
		
		# Only teachers can create tasks
		if usuario_obj.tipo_usuario != usuario.TiposUsuario.MAESTRO:
			return Response({'error': 'Solo los maestros pueden crear tareas'}, status=403)
		
		data = request.data
		archivo = request.FILES.get('archivo')
		
		archivo_url = None
		if archivo:
			if not archivo.name.endswith(('.jpg', '.png', '.pdf', '.doc', '.docx', '.txt')):
				return Response({'status': False, 'message': 'Tipo de archivo no permitido.'}, status=400)
			
			# Add timestamp to filename to avoid conflicts
			import time
			timestamp = str(int(time.time()))
			filename = f"{timestamp}_{archivo.name}"
			file_path = f'media/tareas/{filename}'
			saved_file = default_storage.save(file_path, archivo)
			archivo_url = f"/{saved_file}"
		
		try:
			# Parse date fields
			fecha_vencimiento = None
			if data.get('fecha_vencimiento'):
				from datetime import datetime
				fecha_vencimiento = datetime.fromisoformat(data['fecha_vencimiento'].replace('Z', '+00:00'))
			
			tarea = tareas.objects.create(
				nombre=data['nombre'],
				descripcion=data.get('descripcion', ''),
				instrucciones=data.get('instrucciones', ''),
				es_general=data.get('es_general', 'false').lower() == 'true',
				creado_por=usuario_obj,
				fecha_vencimiento=fecha_vencimiento,
				puntos_maximos=int(data.get('puntos_maximos', 100)),
				estado=data.get('estado', tareas.EstadoTarea.BORRADOR),
				archivo_adjunto=archivo_url
			)
			
			serializer = self.get_serializer(tarea)
			return Response({'status': True, 'data': serializer.data, 'message': 'Tarea creada correctamente'})
			
		except Exception as e:
			return Response({'status': False, 'message': f'Error al crear tarea: {str(e)}'}, status=400)

	@action(detail=True, methods=['post'], url_path='asignar')
	def asignar_tarea(self, request, pk=None):
		"""Asignar tarea a estudiantes o grupos"""
		user = self.request.user
		usuario_obj = usuario.objects.get(usr=user)
		
		# Only teachers can assign tasks
		if usuario_obj.tipo_usuario != usuario.TiposUsuario.MAESTRO:
			return Response({'error': 'Solo los maestros pueden asignar tareas'}, status=status.HTTP_403_FORBIDDEN)
		
		tarea = self.get_object()
		data = request.data
		
		estudiante_ids = data.get('estudiante_ids', [])
		grupo_ids = data.get('grupo_ids', [])
		fecha_vencimiento_personalizada = data.get('fecha_vencimiento_personalizada')
		
		asignaciones_creadas = []
		
		# Asignar a estudiantes individuales
		for estudiante_id in estudiante_ids:
			try:
				estudiante = usuario.objects.get(id=estudiante_id, tipo_usuario=usuario.TiposUsuario.ALUMNO)
				asignacion, created = TareaAsignacion.objects.get_or_create(
					tarea=tarea,
					estudiante=estudiante,
					defaults={
						'asignado_por': usuario_obj,
						'fecha_vencimiento_personalizada': fecha_vencimiento_personalizada
					}
				)
				if created:
					asignaciones_creadas.append(asignacion)
			except usuario.DoesNotExist:
				continue
		
		# Asignar a grupos
		for grupo_id in grupo_ids:
			try:
				grupo = Grupo.objects.get(id=grupo_id)
				asignacion, created = TareaAsignacion.objects.get_or_create(
					tarea=tarea,
					grupo=grupo,
					defaults={
						'asignado_por': usuario_obj,
						'fecha_vencimiento_personalizada': fecha_vencimiento_personalizada
					}
				)
				if created:
					asignaciones_creadas.append(asignacion)
			except Grupo.DoesNotExist:
				continue
		
		return Response({
			'status': True,
			'message': f'Tarea asignada a {len(asignaciones_creadas)} destinatarios',
			'asignaciones_creadas': len(asignaciones_creadas)
		})

	@action(detail=False, methods=['get'], url_path='mis-tareas')
	def mis_tareas(self, request):
		"""Get tasks for current user based on their role"""
		user = request.user
		usuario_obj = usuario.objects.get(usr=user)
		
		if usuario_obj.tipo_usuario == usuario.TiposUsuario.MAESTRO:
			# Teachers get tasks they created
			tareas_usuario = tareas.objects.filter(creado_por=usuario_obj).order_by('-fecha_creacion')
			message = "Tareas que has creado"
		else:
			# Students get assigned tasks
			asignaciones = TareaAsignacion.objects.filter(
				Q(estudiante=usuario_obj) | Q(grupo=usuario_obj.grupo)
			)
			tareas_usuario = tareas.objects.filter(asignaciones__in=asignaciones).distinct().order_by('-fecha_creacion')
			message = "Tareas asignadas a ti"
		
		serializer = self.get_serializer(tareas_usuario, many=True)
		return Response({
			'status': True,
			'message': message,
			'data': serializer.data
		})

	@action(detail=True, methods=['get'], url_path='estadisticas')
	def estadisticas(self, request, pk=None):
		"""Get statistics for a specific task"""
		user = request.user
		usuario_obj = usuario.objects.get(usr=user)
		
		if usuario_obj.tipo_usuario != usuario.TiposUsuario.MAESTRO:
			return Response({'error': 'Solo los maestros pueden ver estadísticas'}, status=403)
		
		tarea = self.get_object()
		
		# Count assignments by status
		asignaciones = TareaAsignacion.objects.filter(tarea=tarea)
		total_asignaciones = asignaciones.count()
		entregadas = asignaciones.filter(estado=TareaAsignacion.EstadoAsignacion.ENTREGADA).count()
		calificadas = asignaciones.filter(estado=TareaAsignacion.EstadoAsignacion.CALIFICADA).count()
		pendientes = total_asignaciones - entregadas
		
		# Get average grade
		entregas_calificadas = TareaEntrega.objects.filter(
			asignacion__tarea=tarea,
			revision__isnull=False
		)
		
		if entregas_calificadas.exists():
			total_calificaciones = sum([e.revision.calificacion for e in entregas_calificadas if e.revision.calificacion])
			promedio = total_calificaciones / entregas_calificadas.count() if entregas_calificadas.count() > 0 else 0
		else:
			promedio = 0
		
		return Response({
			'status': True,
			'data': {
				'tarea': tarea.nombre,
				'total_asignaciones': total_asignaciones,
				'entregadas': entregadas,
				'calificadas': calificadas,
				'pendientes': pendientes,
				'promedio_calificacion': round(promedio, 2),
				'puntos_maximos': tarea.puntos_maximos
			}
		})

	@action(detail=False, methods=['get'], url_path='mi-progreso')
	def mi_progreso(self, request):
		"""Get progress for current student"""
		user = request.user
		usuario_obj = usuario.objects.get(usr=user)
		
		if usuario_obj.tipo_usuario != usuario.TiposUsuario.ALUMNO:
			return Response({'error': 'Solo los estudiantes pueden ver su progreso'}, status=403)
		
		# Get student's assignments
		asignaciones = TareaAsignacion.objects.filter(
			Q(estudiante=usuario_obj) | Q(grupo=usuario_obj.grupo)
		)
		
		total_asignaciones = asignaciones.count()
		entregadas = asignaciones.filter(estado=TareaAsignacion.EstadoAsignacion.ENTREGADA).count()
		calificadas = asignaciones.filter(estado=TareaAsignacion.EstadoAsignacion.CALIFICADA).count()
		pendientes = total_asignaciones - entregadas
		
		# Get average grade
		entregas_estudiante = TareaEntrega.objects.filter(
			estudiante=usuario_obj,
			revision__isnull=False
		)
		
		if entregas_estudiante.exists():
			total_puntos = sum([e.revision.calificacion for e in entregas_estudiante if e.revision.calificacion])
			total_posibles = sum([e.asignacion.tarea.puntos_maximos for e in entregas_estudiante])
			promedio = (total_puntos / total_posibles * 100) if total_posibles > 0 else 0
		else:
			promedio = 0
		
		# Get recent submissions
		entregas_recientes = TareaEntrega.objects.filter(
			estudiante=usuario_obj
		).order_by('-fecha_entrega')[:5]
		
		entregas_data = TareaEntregaConRevisionSerializer(entregas_recientes, many=True).data
		
		return Response({
			'status': True,
			'data': {
				'total_tareas': total_asignaciones,
				'entregadas': entregadas,
				'calificadas': calificadas,
				'pendientes': pendientes,
				'promedio_general': round(promedio, 2),
				'entregas_recientes': entregas_data
			}
		})

class TareaAsignacionViewSet(viewsets.ModelViewSet):
	queryset = TareaAsignacion.objects.all().order_by('-fecha_asignacion')
	serializer_class = TareaAsignacionSerializer
	permission_classes = [IsAuthenticated]
	pagination_class = CustomPagination

	def get_queryset(self):
		user = self.request.user
		usuario_obj = usuario.objects.get(usr=user)
		
		if usuario_obj.tipo_usuario == usuario.TiposUsuario.MAESTRO:
			# Teachers see all assignments they made
			return TareaAsignacion.objects.filter(asignado_por=usuario_obj).order_by('-fecha_asignacion')
		else:
			# Students see their own assignments
			return TareaAsignacion.objects.filter(
				Q(estudiante=usuario_obj) | Q(grupo=usuario_obj.grupo)
			).order_by('-fecha_asignacion')

	@action(detail=False, methods=['get'], url_path='mi-progreso')
	def mi_progreso(self, request):
		"""Get progress for current student"""
		user = request.user
		usuario_obj = usuario.objects.get(usr=user)
		
		if usuario_obj.tipo_usuario != usuario.TiposUsuario.ALUMNO:
			return Response({'error': 'Solo los estudiantes pueden ver su progreso'}, status=403)
		
		# Get student's assignments
		asignaciones = TareaAsignacion.objects.filter(
			Q(estudiante=usuario_obj) | Q(grupo=usuario_obj.grupo)
		)
		
		total_asignaciones = asignaciones.count()
		entregadas = asignaciones.filter(estado=TareaAsignacion.EstadoAsignacion.ENTREGADA).count()
		calificadas = asignaciones.filter(estado=TareaAsignacion.EstadoAsignacion.CALIFICADA).count()
		pendientes = total_asignaciones - entregadas
		
		# Get average grade
		entregas_estudiante = TareaEntrega.objects.filter(
			estudiante=usuario_obj,
			revision__isnull=False
		)
		
		if entregas_estudiante.exists():
			total_puntos = sum([e.revision.calificacion for e in entregas_estudiante if e.revision.calificacion])
			total_posibles = sum([e.asignacion.tarea.puntos_maximos for e in entregas_estudiante])
			promedio = (total_puntos / total_posibles * 100) if total_posibles > 0 else 0
		else:
			promedio = 0
		
		# Get recent submissions
		entregas_recientes = TareaEntrega.objects.filter(
			estudiante=usuario_obj
		).order_by('-fecha_entrega')[:5]
		
		entregas_data = TareaEntregaConRevisionSerializer(entregas_recientes, many=True).data
		
		return Response({
			'status': True,
			'data': {
				'total_tareas': total_asignaciones,
				'entregadas': entregadas,
				'calificadas': calificadas,
				'pendientes': pendientes,
				'promedio_general': round(promedio, 2),
				'entregas_recientes': entregas_data
			}
		})

class TareaEntregaViewSet(viewsets.ModelViewSet):
	queryset = TareaEntrega.objects.all().order_by('-fecha_entrega')
	serializer_class = TareaEntregaSerializer
	permission_classes = [IsAuthenticated]
	pagination_class = CustomPagination

	def get_queryset(self):
		user = self.request.user
		usuario_obj = usuario.objects.get(usr=user)
		
		if usuario_obj.tipo_usuario == usuario.TiposUsuario.MAESTRO:
			# Teachers see all submissions for tasks they created or assigned
			return TareaEntrega.objects.filter(
				Q(asignacion__tarea__creado_por=usuario_obj) | 
				Q(asignacion__asignado_por=usuario_obj)
			).order_by('-fecha_entrega')
		else:
			# Students see only their own submissions
			return TareaEntrega.objects.filter(estudiante=usuario_obj).order_by('-fecha_entrega')

	def perform_create(self, serializer):
		user = self.request.user
		usuario_obj = usuario.objects.get(usr=user)
		
		# Only students can create submissions
		if usuario_obj.tipo_usuario != usuario.TiposUsuario.ALUMNO:
			raise PermissionError("Solo los estudiantes pueden entregar tareas")
		
		asignacion_id = self.request.data.get('asignacion')
		asignacion = TareaAsignacion.objects.get(id=asignacion_id)
		
		# Verify the student is assigned to this task
		if not (asignacion.estudiante == usuario_obj or 
				(asignacion.grupo and asignacion.grupo == usuario_obj.grupo)):
			raise PermissionError("No tienes permiso para entregar esta tarea")
		
		serializer.save(estudiante=usuario_obj)

	def create(self, request):
		data = request.data
		archivo = request.FILES.get('archivo')
		
		archivo_url = None
		if archivo:
			if not archivo.name.endswith(('.jpg', '.png', '.pdf', '.doc', '.docx', '.txt')):
				return Response({'status': False, 'message': 'Tipo de archivo no permitido.'}, status=400)
			
			# Add timestamp to filename to avoid conflicts
			import time
			timestamp = str(int(time.time()))
			filename = f"{timestamp}_{archivo.name}"
			file_path = f'media/entregas/{filename}'
			saved_file = default_storage.save(file_path, archivo)
			archivo_url = f"/{saved_file}"
		
		# Create the submission
		try:
			user = request.user
			usuario_obj = usuario.objects.get(usr=user)
			asignacion = TareaAsignacion.objects.get(id=data['asignacion'])
			
			# Verify permissions
			if not (asignacion.estudiante == usuario_obj or 
					(asignacion.grupo and asignacion.grupo == usuario_obj.grupo)):
				return Response({'error': 'No tienes permiso para entregar esta tarea'}, status=403)
			
			# Check if submission already exists
			existing_submission = TareaEntrega.objects.filter(
				asignacion=asignacion, 
				estudiante=usuario_obj
			).first()
			
			if existing_submission and existing_submission.estado == TareaEntrega.EstadoEntrega.ENTREGADA:
				return Response({'error': 'Ya has entregado esta tarea'}, status=400)
			
			# If exists but is draft, update it; otherwise create new
			if existing_submission and existing_submission.estado == TareaEntrega.EstadoEntrega.BORRADOR:
				existing_submission.contenido = data['contenido']
				if archivo_url:
					existing_submission.archivo_adjunto = archivo_url
				existing_submission.estado = data.get('estado', TareaEntrega.EstadoEntrega.BORRADOR)
				existing_submission.save()
				entrega = existing_submission
			else:
				entrega = TareaEntrega.objects.create(
					asignacion=asignacion,
					estudiante=usuario_obj,
					contenido=data['contenido'],
					archivo_adjunto=archivo_url,
					estado=data.get('estado', TareaEntrega.EstadoEntrega.BORRADOR)
				)
			
			# Update assignment status
			if entrega.estado == TareaEntrega.EstadoEntrega.ENTREGADA:
				asignacion.estado = TareaAsignacion.EstadoAsignacion.ENTREGADA
				asignacion.save()
			
			serializer = self.get_serializer(entrega)
			return Response({'status': True, 'data': serializer.data, 'message': 'Entrega guardada correctamente'})
			
		except TareaAsignacion.DoesNotExist:
			return Response({'status': False, 'message': 'Asignación no encontrada'}, status=404)
		except usuario.DoesNotExist:
			return Response({'status': False, 'message': 'Usuario no encontrado'}, status=404)
		except Exception as e:
			return Response({'status': False, 'message': f'Error interno: {str(e)}'}, status=500)

	@action(detail=True, methods=['post'], url_path='entregar')
	def entregar(self, request, pk=None):
		"""Submit the task officially"""
		entrega = self.get_object()
		user = request.user
		usuario_obj = usuario.objects.get(usr=user)
		
		if entrega.estudiante != usuario_obj:
			return Response({'error': 'No tienes permiso para entregar esta tarea'}, status=403)
		
		entrega.estado = TareaEntrega.EstadoEntrega.ENTREGADA
		entrega.save()
		
		# Update assignment status
		entrega.asignacion.estado = TareaAsignacion.EstadoAsignacion.ENTREGADA
		entrega.asignacion.save()
		
		return Response({'status': True, 'message': 'Tarea entregada correctamente'})

class TareaReviewViewSet(viewsets.ModelViewSet):
	queryset = TareaReview.objects.all().order_by('-fecha_revision')
	serializer_class = TareaReviewSerializer
	permission_classes = [IsAuthenticated]
	pagination_class = CustomPagination

	def get_queryset(self):
		user = self.request.user
		usuario_obj = usuario.objects.get(usr=user)
		
		if usuario_obj.tipo_usuario == usuario.TiposUsuario.MAESTRO:
			# Teachers see reviews they made
			return TareaReview.objects.filter(revisor=usuario_obj).order_by('-fecha_revision')
		else:
			# Students see reviews of their submissions
			return TareaReview.objects.filter(entrega__estudiante=usuario_obj).order_by('-fecha_revision')

	def perform_create(self, serializer):
		user = self.request.user
		usuario_obj = usuario.objects.get(usr=user)
		
		# Only teachers can create reviews
		if usuario_obj.tipo_usuario != usuario.TiposUsuario.MAESTRO:
			raise PermissionError("Solo los maestros pueden revisar tareas")
		
		entrega_id = self.request.data.get('entrega')
		entrega = TareaEntrega.objects.get(id=entrega_id)
		
		# Verify the teacher can review this submission
		if not (entrega.asignacion.tarea.creado_por == usuario_obj or 
				entrega.asignacion.asignado_por == usuario_obj):
			raise PermissionError("No tienes permiso para revisar esta entrega")
		
		serializer.save(revisor=usuario_obj)
		
		# Update submission and assignment status
		entrega.estado = TareaEntrega.EstadoEntrega.CALIFICADA
		entrega.save()
		
		entrega.asignacion.estado = TareaAsignacion.EstadoAsignacion.CALIFICADA
		entrega.asignacion.save()

	@action(detail=False, methods=['get'], url_path='pendientes')
	def pendientes(self, request):
		"""Get pending submissions for review"""
		user = request.user
		usuario_obj = usuario.objects.get(usr=user)
		
		if usuario_obj.tipo_usuario != usuario.TiposUsuario.MAESTRO:
			return Response({'error': 'Solo los maestros pueden ver revisiones pendientes'}, status=403)
		
		# Get submissions that need review
		entregas_pendientes = TareaEntrega.objects.filter(
			estado=TareaEntrega.EstadoEntrega.ENTREGADA,
			asignacion__tarea__creado_por=usuario_obj
		).exclude(revision__isnull=False)
		
		serializer = TareaEntregaConRevisionSerializer(entregas_pendientes, many=True)
		return Response(serializer.data)

class GrupoViewSet(viewsets.ModelViewSet):
	queryset = Grupo.objects.all().order_by('nombre')
	serializer_class = GrupoSerializer
	permission_classes = [IsAuthenticated]
	pagination_class = CustomPagination

	def get_queryset(self):
		user = self.request.user
		usuario_obj = usuario.objects.get(usr=user)
		
		if usuario_obj.tipo_usuario == usuario.TiposUsuario.MAESTRO:
			# Teachers see all groups
			return Grupo.objects.all().order_by('nombre')
		else:
			# Students see only their group
			if usuario_obj.grupo:
				return Grupo.objects.filter(id=usuario_obj.grupo.id)
			return Grupo.objects.none()

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
