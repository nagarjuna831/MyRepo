from django.contrib import admin
from .models import Template, Fields, FormData

# Register your models here.
admin.site.register(Template)
admin.site.register(Fields)
admin.site.register(FormData)
