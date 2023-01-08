from django.db import models
from django.contrib.auth.models import User

from .validators import validate_location


# Create your models here.
class Memory(models.Model):
    """
    The model is related to User model.

    Contains information about user memories.
    It includes:
        user:       foreign key to User model.
        name:       required string field with max_length=100,
                    name of the memory.
        location:   required string field with max_length=100,
                    value like: '[x_coord,y_coord]'
                    the entry must match the validate_location validator
        description:
                    text field with max_length=250, contains
                    additional information about the memory.
        created_date:
                    required datetime field, information about
                    the day when the memory was created.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, null=False, blank=False)
    location = models.CharField(
        max_length=100, null=False, blank=False,
        validators=[
            validate_location
        ]
    )
    description = models.TextField(
        max_length=250, null=False,
        blank=True, default=""
    )

    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Memory"
        verbose_name_plural = "Memories"
        ordering = ['-created_date']
        unique_together = [
            ['user', 'name'],
            ['user', 'location']
        ]

    def __str__(self):
        return f"'{self.name}' memory of {self.user.username}"

    def memory_info(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "location": self.location,
            "created_date": self.created_date.strftime("%d.%m.%Y, %H:%M:%S")
        }
