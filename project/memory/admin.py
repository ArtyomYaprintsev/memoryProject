from django.contrib import admin

from .models import Memory


# Register your models here.
@admin.register(Memory)
class MemoryAdmin(admin.ModelAdmin):
    pass
