import datetime
from haystack import indexes
from .models import Equipment


class EquipmentIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    asset_number = indexes.CharField(model_attr='asset_number')
    serial_number = indexes.CharField(model_attr='serial_number')
    timestamp = indexes.DateTimeField(model_attr='timestamp')

    def get_model(self):
        return Equipment

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.filter(timestamp__lte=datetime.datetime.now())