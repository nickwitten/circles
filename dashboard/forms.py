class CustomFormMixin:

    def save(self, commit=True, **kwargs):
        super().save(commit=False)
        for key, value in kwargs.items():
            setattr(self.instance, key, value)
        return super().save(commit)

    def get_fields(self):
        fields_fieldtype = {}
        fields = list(self.base_fields)
        for field in list(self.declared_fields):
            if field not in fields:
                fields.append(field)
        for field in fields:
            widget = self.fields[field].widget
            if hasattr(widget, 'input_type'):
                input_type = widget.input_type
            else:
                input_type = 'text'
            fields_fieldtype[field] = input_type
        return fields_fieldtype
