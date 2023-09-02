# Register your receivers here
from django.dispatch import receiver

from pretalx.common.signals import register_data_exporters



print ("*******************registering nanoc exporter signal file")

@receiver(register_data_exporters, dispatch_uid="nanoc_export")
def register_data_exporter(sender, **kwargs):

    print("***registering nanoc exporter***")
    from .nanoc import NanocExporter
    return NanocExporter
