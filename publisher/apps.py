from __future__ import unicode_literals

from django.apps import AppConfig


class PublisherConfig(AppConfig):
    name = 'publisher'

    def ready(self):
        from publisher import signals
