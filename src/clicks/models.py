from django.db import models


class Click(models.Model):
    campaign = models.IntegerField(db_index=True)
    timestamp = models.DateTimeField()

    class Meta:
        indexes = [
            models.Index(fields=["campaign", "timestamp"])
        ]

    @classmethod
    def count_campaign_clicks(cls,
                              campaign: int,
                              after_date: str = None,
                              before_date: str = None) -> int:
        """
        SQL:
            SELECT count(*)
            FROM click_logs_click
            WHERE campaign = '4510461'
              AND timestamp BETWEEN '2021-11-07 03:10:00'
              AND '2021-11-07 03:30:00';
        """
        qs = cls.objects.filter(campaign=campaign)
        if after_date:
            qs = qs.filter(timestamp__gt=after_date)
        if before_date:
            qs = qs.filter(timestamp__lt=before_date)
        return qs.count()

    def __repr__(self):
        return f'Click(campaign={self.campaign}, timestamp={self.timestamp})'

    def __str__(self):
        return repr(self)
