from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import UserProfile, AIPlan



class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = "Fitness Profile"

class UserAdmin(BaseUserAdmin):
    inlines = [UserProfileInline]
    list_display = ("username", "email", "first_name", "last_name", "is_staff", "get_fitness_category")

    def get_fitness_category(self, instance):
        return instance.profile.fitness_category if hasattr(instance, "profile") else "No Profile"
    get_fitness_category.short_description = "Fitness Category"

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(AIPlan)
class AIPlanAdmin(admin.ModelAdmin):
    list_display = ("user", "plan_type", "created_at", "is_active")
    list_filter = ("is_active", "plan_type", "created_at")
    search_fields = ("user__username", "content")