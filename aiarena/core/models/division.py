from django.db import models
from aiarena.core.models.competition import Competition


class Division(models.Model):

    name = models.CharField(max_length=50)
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, related_name='divisions')

    @property
    def get_bots(self):
        return self.bots.all()

    def __str__(self):
        return f"[{self.name}] Active Bots: [{len(self.get_bots())}]"