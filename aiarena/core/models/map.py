from django.db import models

from aiarena.core.storage import OverwriteStorage


def map_file_upload_to(instance, filename):
    return '/'.join(['maps', instance.name])


class Map(models.Model):
    name = models.CharField(max_length=50, unique=True)
    file = models.FileField(upload_to=map_file_upload_to, storage=OverwriteStorage())
    active = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    @staticmethod
    def random_active():
        # todo: apparently this is really slow
        # https://stackoverflow.com/questions/962619/how-to-pull-a-random-record-using-djangos-orm#answer-962672
        return Map.objects.filter(active=True).order_by('?').first()

    def activate(self):
        self.active = True
        self.save()

    def deactivate(self):
        self.active = False
        self.save()
