"""
Management command para enviar recordatorios de citas.

Uso:
    python manage.py send_reminders
    python manage.py send_reminders --hours=48

Para configurar como cron job (8 AM diario):
    0 8 * * * cd /path/to/project && python manage.py send_reminders
"""

from django.core.management.base import BaseCommand

from apps.notifications.services import send_daily_reminders, get_appointments_for_reminder


class Command(BaseCommand):
    help = 'Envía recordatorios de citas para las próximas 24 horas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--hours',
            type=int,
            default=24,
            help='Horas antes de la cita para enviar recordatorio (default: 24)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Solo muestra las citas que recibirían recordatorio sin enviar'
        )

    def handle(self, *args, **options):
        hours = options['hours']
        dry_run = options['dry_run']

        appointments = get_appointments_for_reminder(hours)
        count = appointments.count()

        if dry_run:
            self.stdout.write(
                self.style.WARNING(f'[DRY RUN] Se encontraron {count} citas para recordatorio:')
            )
            for apt in appointments:
                self.stdout.write(
                    f'  - {apt.date} {apt.start_time}: {apt.patient} '
                    f'con {apt.professional} ({apt.patient.phone})'
                )
            return

        if count == 0:
            self.stdout.write(
                self.style.SUCCESS('No hay citas que requieran recordatorio.')
            )
            return

        self.stdout.write(f'Enviando recordatorios para {count} citas...')

        sent, failed = send_daily_reminders()

        self.stdout.write(
            self.style.SUCCESS(f'Recordatorios enviados: {sent}')
        )
        if failed > 0:
            self.stdout.write(
                self.style.ERROR(f'Recordatorios fallidos: {failed}')
            )
