from django.contrib import admin
from django.forms import ModelForm, ModelChoiceField, ModelMultipleChoiceField

from webapp.models import AccessToken

from models import WeavrGreeterGroupMembership


class AccessTokenChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return "%s on %s (%s)"%(obj.weavr_name,
                                obj.prosthetic.server,
                                obj.prosthetic.name)


class WGGMForm(ModelForm):
   weavr_token = AccessTokenChoiceField(AccessToken.objects.all())

   class Meta:
       model = WeavrGreeterGroupMembership


class WeavrGreeterGroupMembershipAdmin(admin.ModelAdmin):
    form = WGGMForm


admin.site.register(WeavrGreeterGroupMembership,
                    WeavrGreeterGroupMembershipAdmin)
