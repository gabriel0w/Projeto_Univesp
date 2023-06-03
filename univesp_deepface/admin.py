from django.contrib import admin
from deepemotion.models import Person

@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ['name', 'emotion1', 'emotion2']
