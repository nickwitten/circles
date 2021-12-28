from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

import json

from django.core.files.base import ContentFile
from django.forms import model_to_dict

from circles import settings


class DictMixin:

    def to_dict(self):
        data = model_to_dict(self)
        for key, value in data.items():
            if isinstance(value, list) and isinstance(next(iter(value), None), models.Model):
                data[key] = [model.pk for model in value]
        return data


class JsonM2MFieldModelMixin:
    JsonM2MFields = []

    def save(self, *args, **kwargs):
        """ Gets dicts from json field and adds those
            objects to manytomany relationship.  Dicts
            must contain pk key to be added to model    """
        model = super().save(*args, **kwargs)
        for i, field in enumerate(self.JsonM2MFields):
            # Get field value
            try:
                field_value = json.loads(getattr(self, field[0]))
            except Exception as e:
                return model
            items = [item for item in field_value if 'pk' in item]
            pks = [item['pk'] for item in items]
            attached_models = self.get_attached_models(field[1], pks)
            self.remove_invalid_items(field, field_value, attached_models, items)
            self.set_attached_models(field, attached_models)
        return super().save()

    def get_attached_models(self, klass, items):
        pks = [item['pk'] for item in items]
        return klass.objects.filter(pk__in=pks)

    def remove_invalid_items(self, field, field_value, attached_models, items):
        for item in items:
            if item['pk'] not in list(attached_models.values_list('pk', flat=True)):
                for j, value in enumerate(field_value):
                    if 'pk' in value and value['pk'] == item['pk']:
                        field_value.pop(j)
        setattr(self, field[0], json.dumps(field_value))

    def set_attached_models(self, field, attached_models):
        objects_field = getattr(self, field[0] + '_objects')
        objects_field.clear()
        objects_field.add(*attached_models)

    def to_dict(self):
        if hasattr(super(), 'to_dict'):
            model_info = super().to_dict()
        else:
            model_info = model_to_dict(self)
        for field in self.JsonM2MFields:
            model_info.pop(field[0]+'_objects')
        return model_info


class FileFieldMixin:
    """ Mixin to manage a "files" field for
        a model.  Operations are to create, 
        delete, and set (copy) files.
        
        FileModelClass:  The model for each
            file object, must contain attributes:
                "model" - ForeignKey for parent model
                "file" - FileField for the file
                "title" - Char title for the file

    """
    FileModelClass = None

    def to_dict(self, *args, **kwargs):
        if hasattr(super(), 'to_dict'):
            model_info = super().to_dict()
        else:
            model_info = model_to_dict(self)
        files_info = [(file.title, file.pk, file.file.url)
                      for file in self.files.all()]
        model_info['files'] = files_info
        return model_info

    def save(self, *args, **kwargs):
        """ Overrides the model's save to handle
            files key word.  Files is a dictionary:

            files = {
                "$(FileTitle)": $(FileObject),
                "delete_files": [$(file_pk), ],
                "set_files": [$(target_model_pk), ],
            }

            Where each file title is a key, and the object
            is a value.  To delete a file pass it's pk under the
            key "delete_files".  To set all of this model's
            files as equal to another model's files, pass
            the target model's pk under the key set_files.
            These are lists, but will only act on the first
            pk passed. (Change this).
        """
        files_with_options = kwargs.pop('files', None)
        super().save(*args, **kwargs)
        if files_with_options:
            delete_files = files_with_options.pop('delete_files', None)
            set_files = files_with_options.pop('set_files', None)
            files = files_with_options
            if delete_files is not None:
                # Not sure why this is a nested list, but unpack
                [delete_files] = delete_files
            if set_files is not None:
                # Same for set files
                [set_files] = set_files
            if set_files is not None and self.pk != int(set_files):
                self._set_files(set_files)
            else:
                self._create_delete_files(files, delete_files)
            # files_with_options['delete_files'] = delete_files
            # files_with_options['set_files'] = set_files

    def _create_delete_files(self, files, delete_files):
        """ Create and delete files
            files: {$(title): $(file), }
            delete_files: [$(pk), ]
        """
        for title, file in files.items():
            file_info = {'title': title, 'file': file, 'model': self}
            file_model = self.FileModelClass(**file_info)
            file_model.save()
        for pk in delete_files or []:
            file = self.FileModelClass.objects.filter(pk=pk).first()
            if file:
                file.delete()

    def _set_files(self, set_files):
        """ Copy all files from target model to this model """
        target_model = self.__class__.objects.filter(pk=int(set_files or 0)).first()
        if target_model:
            for file in self.files.all():
                file.delete()
            for target_file in target_model.files.all():
                title = target_file.title
                nf_model = self.FileModelClass(model=self, title=title)
                target_file.file.seek(0)
                nf = ContentFile(target_file.file.read())
                nf.name = target_file.file.name.split('/')[-1]
                nf_model.file = nf
                nf_model.save()


class DashboardContent(models.Model):
    content = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User,on_delete=models.CASCADE)

