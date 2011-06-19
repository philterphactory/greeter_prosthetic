from django.db import models


class WeavrGreeterGroupMembership(models.Model):
    """Group Weavrs, so only Weavrs in the same group communicate"""
    group = models.IntegerField()
    weavr_token = models.ForeignKey('webapp.AccessToken',
                                    related_name='greeter_group_weavr_toekn')

    def __str__(self):
        return "%i: %s" % (self.group, self.weavr_token.weavr_name)


def other_weavrs_in_group(weavr_token):
    """Get all the tokens for the weavrs user, except this one"""
    me = WeavrGreeterGroupMembership.objects.get(weavr_token=weavr_token)
    group = me.group
    return WeavrGreeterGroupMembership.objects.filter(group=group).\
        exclude(weavr_token=weavr_token)
