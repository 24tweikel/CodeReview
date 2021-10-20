from json import JSONDecoder, JSONDecodeError

from django.forms import ModelForm, TextInput
from django.forms.fields import CharField
from jsonschema import ValidationError
from jsonschema.validators import Draft202012Validator

from . import models


class CreateRubricWidget(TextInput):
    template_name = "widgets/rubric_create.html"
    input_type = 'hidden'

    class Media:
        css = {'all': ('css/rubrics/rubric_table.css',)}
        js = ('js/rubrics/rubric-create-widget.js',)


class RubricForm(ModelForm):
    rubric = CharField(widget=CreateRubricWidget, help_text="This rubric will be used by reviewers to grade code")
    _validation_schema = {
        "type": "array",
        "minItems": 1,
        "items": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "minLength": 1,
                },
                "description": {
                    "type": "string",
                    "minLength": 1,
                },
                "cells": {
                    "type": "array",
                    "minItems": 1,
                    "items": {
                        "type": "object",
                        "properties": {
                            "score": {
                                "type": "number",
                                "minimum": 0,
                            },
                            "description": {
                                "type": "string",
                                "minLength": 1,
                            },
                        }
                    }
                }
            }
        }
    }

    class Meta:
        model = models.Rubric
        fields = ['name']

    def __init__(self, *args, **kwargs):
        instance: models.Rubric = kwargs.get("instance", None)
        initial: dict = kwargs.get("initial", {})
        if instance is not None:
            initial['rubric'] = instance.to_json()
        kwargs['initial'] = initial
        self._validation_schema['items', 'properties', 'name', 'maxLength'] = models.RubricRow.max_length("name")
        self._validation_schema['items', 'properties', 'description', 'maxLength'] = models.RubricRow.max_length(
            "description")
        self._validation_schema[
            'items', 'properties', 'cells', 'items', 'properties', 'description'] = models.RubricCell.max_length(
            'description')
        self._json_validator = Draft202012Validator(self._validation_schema)
        super().__init__(*args, **kwargs)

    def save(self, commit=True) -> models.Rubric:
        new_rubric: models.Rubric = super().save(commit=False)
        new_rubric.max_score = 0
        new_rubric.save()
        json: str = self.cleaned_data.get('rubric')
        possible_points = 0

        new_obj = JSONDecoder().decode(json)

        for index, row in enumerate(new_obj):
            new_row, created = models.RubricRow.objects.get_or_create(parent_rubric=new_rubric, index=index, defaults={
                'name': row.get('name'),
                'description': row.get('description'),
                'index': index,
                'parent_rubric': new_rubric,
                'max_score': 0
            })
            if not created:
                new_row.name = row.get('name')
                new_row.description = row.get('description')
                new_row.max_score = 0
            new_row.save()
            for cell_index, cell in enumerate(row.get("cells", [])):
                score = int(cell.get("score"))
                new_row.max_score = max(score, new_row.max_score)
                new_cell, cell_created = models.RubricCell.objects.get_or_create(parent_row=new_row, index=cell_index,
                                                                                 defaults={
                                                                                     'description': cell.get(
                                                                                         "description"),
                                                                                     'score': score,
                                                                                     'parent_row': new_row,
                                                                                     'index': cell_index
                                                                                 })
                if not cell_created:
                    new_cell.description = cell.get('description')
                    new_cell.score = score
                new_cell.save()
            possible_points += new_row.max_score
            new_row.save()

            new_row.rubriccell_set.filter(index__gt=len(row.get("cells", [])) - 1).delete()

        new_rubric.rubricrow_set.filter(index__gt=len(new_obj) - 1).delete()

        new_rubric.max_score = possible_points
        new_rubric.save()
        return new_rubric

    @staticmethod
    def explain_json_error(error: ValidationError) -> str:
        if len(error.relative_path) > 0:
            row_num = error.relative_path[0] + 1
            location = f"in row {row_num}"
            offending_row_elem = error.relative_path[1]
            if offending_row_elem == "description" or offending_row_elem == "name":
                if "too short" in error.message:
                    return f"Please enter a {offending_row_elem} {location}"
                elif "too long" in error.message:
                    return f"{offending_row_elem} is too long {location}"
                else:
                    return f"Unknown Error {location}"
            elif offending_row_elem == "cells":
                if "[] is too short" == error.message:
                    return f"Row {row_num} must have at least one cell"
                else:
                    cell_num = error.relative_path[2] + 1
                    location += f", cell {cell_num}"
                    offending_cell_elem = error.relative_path[3]
                    if offending_cell_elem == "score" and "not of type 'number'" in error.message:
                        return f"Please enter a number for the score {location}"
                    elif offending_cell_elem == "description":
                        if "too short" in error.message:
                            return f"Please enter a description {location}"
                        elif "too long" in error.message:
                            return f"Description is too long {location}"
                    else:
                        return f"Unknown error {location}"
        else:
            if "too short" in error.message:
                return "Please provide at least one row"
            return "Unknown Error"

    def clean(self) -> dict:
        super().clean()
        raw_json: str = self.cleaned_data.get("rubric")

        if raw_json is not None:
            try:
                errors = sorted(self._json_validator.iter_errors(JSONDecoder().decode(raw_json)), key=str)
                [self.add_error('rubric', self.explain_json_error(error) + ".") for error in errors]
            except JSONDecodeError:
                self.add_error('rubric', "Invalid JSON")

        return self.cleaned_data
