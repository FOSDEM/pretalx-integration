from django.dispatch import receiver
from pretalx.common.signals import register_data_exporters


@receiver(register_data_exporters, dispatch_uid="exporter_fosdem_json")
def register_data_exporter(sender, **kwargs):
    from pretalx_nanoc_export.json import FosdemJsonExporter

    return FosdemJsonExporter
