"""
Management command para crear datos iniciales del sistema.

Uso:
    python manage.py setup_initial_data
    python manage.py setup_initial_data --with-demo
"""

from datetime import date, time, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

User = get_user_model()


class Command(BaseCommand):
    help = 'Crea datos iniciales: grupos, permisos, procedimientos, consultorio y datos demo'

    def add_arguments(self, parser):
        parser.add_argument(
            '--with-demo',
            action='store_true',
            help='Incluir datos demo (pacientes, citas, profesionales)',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Iniciando configuración de datos...'))

        self.create_groups()
        self.create_procedures()
        self.create_clinic()
        self.create_message_templates()

        if options['with_demo']:
            self.create_demo_data()

        self.stdout.write(self.style.SUCCESS('¡Configuración completada exitosamente!'))

    def create_groups(self):
        """Crear grupos de usuarios."""
        self.stdout.write('Creando grupos de usuarios...')

        groups_permissions = {
            'Administradores': [],  # Full access via is_staff/is_superuser
            'Recepción': [
                'add_patient', 'change_patient', 'view_patient',
                'add_appointment', 'change_appointment', 'view_appointment', 'delete_appointment',
                'view_professional', 'view_proceduretype',
                'view_clinic', 'view_notificationlog',
            ],
            'Profesionales': [
                'view_patient', 'view_appointment', 'change_appointment',
                'view_professional', 'view_proceduretype', 'view_clinic',
            ],
        }

        for group_name, perms in groups_permissions.items():
            group, created = Group.objects.get_or_create(name=group_name)
            if created:
                self.stdout.write(f'  - Grupo "{group_name}" creado')

            # Add permissions
            for perm_codename in perms:
                try:
                    permission = Permission.objects.get(codename=perm_codename)
                    group.permissions.add(permission)
                except Permission.DoesNotExist:
                    pass

    def create_procedures(self):
        """Crear tipos de procedimientos iniciales."""
        from apps.appointments.models import ProcedureType

        self.stdout.write('Creando tipos de procedimientos...')

        procedures = [
            {'name': 'Evaluación', 'duration_minutes': 30, 'color': '#3B82F6', 'order': 1},
            {'name': 'Profilaxis', 'duration_minutes': 45, 'color': '#10B981', 'order': 2},
            {'name': 'Restauración', 'duration_minutes': 60, 'color': '#F59E0B', 'order': 3},
            {'name': 'Endodoncia', 'duration_minutes': 90, 'color': '#EF4444', 'order': 4},
            {'name': 'Cirugía', 'duration_minutes': 90, 'color': '#8B5CF6', 'order': 5},
            {'name': 'Control', 'duration_minutes': 30, 'color': '#06B6D4', 'order': 6},
        ]

        for proc_data in procedures:
            proc, created = ProcedureType.objects.get_or_create(
                name=proc_data['name'],
                defaults=proc_data
            )
            if created:
                self.stdout.write(f'  - Procedimiento "{proc.name}" creado')

    def create_clinic(self):
        """Crear consultorio por defecto."""
        from apps.clinic.models import Clinic, Schedule

        self.stdout.write('Creando consultorio...')

        clinic, created = Clinic.objects.get_or_create(
            pk=1,
            defaults={
                'name': 'Consultorio Odontológico',
                'phone': '(01) 234-5678',
                'whatsapp': '999-888-777',
                'email': 'contacto@consultoriodental.com',
                'address': 'Av. Principal 123, Lima, Perú',
                'appointment_duration_default': 30,
            }
        )

        if created:
            self.stdout.write(f'  - Consultorio "{clinic.name}" creado')

            # Create default schedules (Monday to Saturday)
            default_schedules = [
                (0, time(9, 0), time(13, 0)),   # Monday morning
                (0, time(15, 0), time(19, 0)),  # Monday afternoon
                (1, time(9, 0), time(13, 0)),   # Tuesday morning
                (1, time(15, 0), time(19, 0)),  # Tuesday afternoon
                (2, time(9, 0), time(13, 0)),   # Wednesday morning
                (2, time(15, 0), time(19, 0)),  # Wednesday afternoon
                (3, time(9, 0), time(13, 0)),   # Thursday morning
                (3, time(15, 0), time(19, 0)),  # Thursday afternoon
                (4, time(9, 0), time(13, 0)),   # Friday morning
                (4, time(15, 0), time(19, 0)),  # Friday afternoon
                (5, time(9, 0), time(13, 0)),   # Saturday morning only
            ]

            for weekday, start, end in default_schedules:
                Schedule.objects.create(
                    clinic=clinic,
                    weekday=weekday,
                    start_time=start,
                    end_time=end,
                )

            self.stdout.write('  - Horarios por defecto creados')

    def create_message_templates(self):
        """Crear plantillas de mensajes."""
        from apps.clinic.models import Clinic, MessageTemplate

        self.stdout.write('Creando plantillas de mensajes...')

        clinic = Clinic.get_default()

        templates = [
            {
                'template_type': 'reminder',
                'subject': 'Recordatorio de cita odontológica',
                'message': '''Estimado/a {paciente},

Le recordamos que tiene una cita programada:

📅 Fecha: {fecha}
🕐 Hora: {hora}
🦷 Procedimiento: {procedimiento}
👨‍⚕️ Doctor/a: {doctor}

📍 {consultorio}
📞 {telefono}

Por favor confirme su asistencia.
Gracias.''',
            },
            {
                'template_type': 'confirmation',
                'subject': 'Confirmación de cita odontológica',
                'message': '''Estimado/a {paciente},

Su cita ha sido confirmada:

📅 Fecha: {fecha}
🕐 Hora: {hora}
🦷 Procedimiento: {procedimiento}
👨‍⚕️ Doctor/a: {doctor}

Le esperamos.
{consultorio}''',
            },
            {
                'template_type': 'cancellation',
                'subject': 'Cita cancelada',
                'message': '''Estimado/a {paciente},

Le informamos que su cita del {fecha} a las {hora} ha sido cancelada.

Por favor comuníquese con nosotros para reprogramar.

📞 {telefono}
{consultorio}''',
            },
            {
                'template_type': 'reschedule',
                'subject': 'Cita reprogramada',
                'message': '''Estimado/a {paciente},

Su cita ha sido reprogramada:

📅 Nueva fecha: {fecha}
🕐 Nueva hora: {hora}
🦷 Procedimiento: {procedimiento}
👨‍⚕️ Doctor/a: {doctor}

{consultorio}''',
            },
        ]

        for tpl_data in templates:
            tpl, created = MessageTemplate.objects.get_or_create(
                clinic=clinic,
                template_type=tpl_data['template_type'],
                defaults=tpl_data
            )
            if created:
                self.stdout.write(f'  - Plantilla "{tpl.get_template_type_display()}" creada')

    def create_demo_data(self):
        """Crear datos de demostración."""
        from apps.clinic.models import Clinic, Professional, Schedule
        from apps.patients.models import Patient
        from apps.appointments.models import Appointment, ProcedureType

        self.stdout.write(self.style.NOTICE('Creando datos de demostración...'))

        clinic = Clinic.get_default()

        # Create admin user if not exists
        admin_user, created = User.objects.get_or_create(
            email='admin@consultorio.com',
            defaults={
                'first_name': 'Admin',
                'last_name': 'Sistema',
                'role': 'admin',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write('  - Usuario admin creado (admin@consultorio.com / admin123)')

        # Create professional users
        professionals_data = [
            {
                'email': 'dra.martinez@consultorio.com',
                'first_name': 'María',
                'last_name': 'Martínez',
                'specialty': 'Odontología General',
                'color': '#1D4ED8',
            },
            {
                'email': 'dr.rodriguez@consultorio.com',
                'first_name': 'Carlos',
                'last_name': 'Rodríguez',
                'specialty': 'Endodoncia',
                'color': '#059669',
            },
        ]

        professionals = []
        for prof_data in professionals_data:
            user, created = User.objects.get_or_create(
                email=prof_data['email'],
                defaults={
                    'first_name': prof_data['first_name'],
                    'last_name': prof_data['last_name'],
                    'role': 'professional',
                }
            )
            if created:
                user.set_password('doctor123')
                user.save()

            professional, created = Professional.objects.get_or_create(
                user=user,
                defaults={
                    'clinic': clinic,
                    'specialty': prof_data['specialty'],
                    'color': prof_data['color'],
                }
            )
            professionals.append(professional)

            if created:
                self.stdout.write(f'  - Profesional "{professional}" creado')

                # Create schedules for professional
                for weekday in range(5):  # Monday to Friday
                    Schedule.objects.create(
                        professional=professional,
                        weekday=weekday,
                        start_time=time(9, 0),
                        end_time=time(18, 0),
                    )

        # Create reception user
        reception_user, created = User.objects.get_or_create(
            email='recepcion@consultorio.com',
            defaults={
                'first_name': 'Ana',
                'last_name': 'García',
                'role': 'reception',
            }
        )
        if created:
            reception_user.set_password('recepcion123')
            reception_user.save()
            self.stdout.write('  - Usuario recepción creado (recepcion@consultorio.com / recepcion123)')

        # Create patients
        patients_data = [
            {'first_name': 'Juan', 'last_name': 'Pérez García', 'phone': '999-111-222', 'email': 'juan.perez@email.com'},
            {'first_name': 'María', 'last_name': 'López Torres', 'phone': '999-222-333', 'email': 'maria.lopez@email.com', 'has_anxiety': True},
            {'first_name': 'Carlos', 'last_name': 'Sánchez Díaz', 'phone': '999-333-444', 'email': 'carlos.sanchez@email.com'},
            {'first_name': 'Ana', 'last_name': 'Ramírez Vega', 'phone': '999-444-555', 'email': 'ana.ramirez@email.com', 'has_allergies': True, 'allergies_detail': 'Alergia a penicilina'},
            {'first_name': 'Pedro', 'last_name': 'Fernández Luna', 'phone': '999-555-666', 'email': 'pedro.fernandez@email.com', 'is_elderly': True},
        ]

        patients = []
        for i, patient_data in enumerate(patients_data, 1):
            patient, created = Patient.objects.get_or_create(
                medical_record_number=f'HC-2024-{i:04d}',
                defaults={
                    'clinic': clinic,
                    'birth_date': date(1990 - i * 5, 1, 15),
                    **patient_data
                }
            )
            patients.append(patient)
            if created:
                self.stdout.write(f'  - Paciente "{patient.full_name}" creado')

        # Create appointments
        procedures = list(ProcedureType.objects.all())
        today = timezone.now().date()

        appointments_data = [
            {'days_offset': 0, 'hour': 9, 'patient_idx': 0, 'prof_idx': 0, 'proc_idx': 0, 'status': 'confirmed'},
            {'days_offset': 0, 'hour': 10, 'patient_idx': 1, 'prof_idx': 0, 'proc_idx': 1, 'status': 'pending'},
            {'days_offset': 0, 'hour': 11, 'patient_idx': 2, 'prof_idx': 1, 'proc_idx': 2, 'status': 'confirmed'},
            {'days_offset': 0, 'hour': 15, 'patient_idx': 3, 'prof_idx': 0, 'proc_idx': 5, 'status': 'pending'},
            {'days_offset': 1, 'hour': 9, 'patient_idx': 4, 'prof_idx': 1, 'proc_idx': 3, 'status': 'pending'},
            {'days_offset': 1, 'hour': 11, 'patient_idx': 0, 'prof_idx': 0, 'proc_idx': 1, 'status': 'pending'},
            {'days_offset': 2, 'hour': 10, 'patient_idx': 1, 'prof_idx': 1, 'proc_idx': 4, 'status': 'pending'},
            {'days_offset': 2, 'hour': 15, 'patient_idx': 2, 'prof_idx': 0, 'proc_idx': 0, 'status': 'pending'},
            {'days_offset': 3, 'hour': 9, 'patient_idx': 3, 'prof_idx': 1, 'proc_idx': 2, 'status': 'pending'},
            {'days_offset': 3, 'hour': 16, 'patient_idx': 4, 'prof_idx': 0, 'proc_idx': 5, 'status': 'pending'},
        ]

        for apt_data in appointments_data:
            apt_date = today + timedelta(days=apt_data['days_offset'])
            procedure = procedures[apt_data['proc_idx'] % len(procedures)]
            start = time(apt_data['hour'], 0)
            end_dt = timezone.datetime.combine(apt_date, start) + timedelta(minutes=procedure.duration_minutes)

            appointment, created = Appointment.objects.get_or_create(
                patient=patients[apt_data['patient_idx']],
                date=apt_date,
                start_time=start,
                defaults={
                    'professional': professionals[apt_data['prof_idx']],
                    'procedure_type': procedure,
                    'clinic': clinic,
                    'end_time': end_dt.time(),
                    'status': apt_data['status'],
                    'created_by': admin_user,
                }
            )
            if created:
                self.stdout.write(f'  - Cita creada: {appointment}')

        self.stdout.write(self.style.SUCCESS('Datos de demostración creados'))
