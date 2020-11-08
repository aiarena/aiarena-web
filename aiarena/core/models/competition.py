from django.db import models


class CompetitionType(models.TextChoices):
    TOURNAMENT = u'T', 'Tournament'
    LEAGUE = u'L', 'League'
    CUSTOM = u'C', 'Custom'


class Competition(models.Model):
    competition_types = (
            ("T", "TOURNAMENT"),
            ("L", "LEAGUE"),
            ("C", "CUSTOM"),
    )

    name = models.CharField(max_length=50, unique=True)
    type = models.CharField(max_length=32,
                            choices=CompetitionType.choices,
                            default=CompetitionType.LEAGUE)

    def get_type(self):
        return CompetitionType(self.type).name.title()

    def get_divisions(self):
        return self.divisions.all()

    def __str__(self):
        return f"[{self.name}, {self.get_type()}, Divisions: {self.get_divisions()}]"
