from django.contrib import admin
from .models import CustomUser,OwnerProfile
from .models import BrokerProfile


# Register your models here.
admin.site.register(CustomUser)

admin.site.register(BrokerProfile)

admin.site.register(OwnerProfile)
