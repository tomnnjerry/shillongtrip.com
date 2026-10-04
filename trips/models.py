from django.db import models


class Enquiry(models.Model):
    """A trip enquiry from any form on the site (contact page, footer, pop-up)."""
    created = models.DateTimeField(auto_now_add=True)
    source = models.CharField(max_length=40, blank=True, help_text='contact, footer, popup')
    name = models.CharField(max_length=120)
    phone = models.CharField(max_length=40)
    email = models.EmailField(blank=True)
    month = models.CharField(max_length=20, blank=True)
    nights = models.CharField(max_length=10, blank=True)
    pax = models.CharField(max_length=80, blank=True)
    states = models.CharField(max_length=200, blank=True)
    tier = models.CharField(max_length=20, blank=True)
    tour = models.CharField(max_length=300, blank=True, help_text='Package(s) the visitor asked about')
    message = models.TextField(blank=True)
    page = models.CharField(max_length=300, blank=True)
    page_title = models.CharField(max_length=300, blank=True)
    shortlist = models.CharField(max_length=500, blank=True)
    attribution = models.JSONField(null=True, blank=True)
    handled = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created']
        verbose_name_plural = 'enquiries'

    def __str__(self):
        return f'{self.name} · {self.phone} · {self.created:%d %b %Y}'

