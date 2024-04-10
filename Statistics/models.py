from django.utils import timezone

# Create your models here.
import random
import string
from django.db import models
from Api.models import FoundPerson, MissingPerson
from Users.models import User

# Create your models here.


class Case(models.Model):
    case_number = models.CharField(
        max_length=50, default="", unique=True, editable=False)
    missing_person = models.ForeignKey(
        MissingPerson, on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=20, choices=[(
        'open', 'Open'), ('closed', 'Closed')], default='open')
    found_person = models.ForeignKey(
        FoundPerson, on_delete=models.CASCADE, null=True, blank=True)
    type = models.CharField(max_length=20, choices=[(
        'missing', 'Missing'), ('found', 'Found')])
    created_at = models.DateField(default=timezone.now)

    def generate_case_number(self):
        case_number = ''.join(random.choices(
            string.ascii_uppercase + string.digits, k=8))

        if not Case.objects.filter(case_number=case_number).exists():
            return case_number

    def __str__(self):
        return f"Case {self.case_number}"

    def save(self, *args, **kwargs):
        if not self.case_number:
            self.case_number = self.generate_case_number()
        super().save(*args, **kwargs)


class Remark(models.Model):
    case_id = models.ForeignKey(
        Case, on_delete=models.CASCADE, null=True, blank=True)
    remarks = models.TextField(blank=True, default="")
    created_at = models.DateField(default=timezone.now)
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True)


class Notification(models.Model):
    message = models.TextField(default="", blank=True)
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications_creator'
    )
    recepient = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications_receiver'
    )
