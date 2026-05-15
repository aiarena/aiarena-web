from django.conf import settings
from django.db import models


class ApiUsage(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="api_usage")
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    call_count = models.PositiveIntegerField()
    total_duration_ms = models.PositiveBigIntegerField()
    p50_duration_ms = models.PositiveIntegerField()
    p75_duration_ms = models.PositiveIntegerField()
    p95_duration_ms = models.PositiveIntegerField()
    p99_duration_ms = models.PositiveIntegerField()

    class Meta:
        unique_together = [("user", "period_start", "period_end")]
        indexes = [models.Index(fields=["period_end"])]
