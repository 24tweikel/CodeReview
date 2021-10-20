from typing import Optional, Union
from uuid import uuid4, UUID

from django.db import models

from Users.models import User


def val_uuid(src: Union[str, UUID]) -> Optional[UUID]:
    try:
        return UUID(src) if type(src) == str else src
    except ValueError:
        return None


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    class Meta:
        abstract = True

    @classmethod
    def max_length(cls, field_name: str) -> int:
        return cls._meta.get_field(field_name).max_length


class Review(BaseModel):
    class Status(models.TextChoices):
        OPEN = 'O', "Open"
        ASSIGNED = 'A', "Taken"
        CLOSED = 'C', "Completed"

    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="student")
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviewer", null=True)
    schoology_id = models.CharField(max_length=10, null=True, help_text="The ID of the schoology assignment that this review pertains to")
    status = models.CharField(choices=Status.choices, default=Status.OPEN, max_length=1)
    rubric = models.ForeignKey("Instructor.Rubric", on_delete=models.CASCADE, related_name="source_rubric", help_text="The rubric the reviewer will use to grade your code")
    additional_comments = models.TextField(blank=True, null=True, help_text="Any additional comments you have on the code")
    date_created = models.DateTimeField(auto_now_add=True)
    date_completed = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-date_completed', '-date_created']

    def __str__(self):
        return f"Review from {str(self.student)}"

    def score_fraction(self):
        if self.status == Review.Status.CLOSED:
            my_score = 0
            max_score = self.rubric.max_score
            for scoredRow in self.scoredrow_set.all():
                if scoredRow.score == -1:
                    max_score -= scoredRow.source_row.max_score
                else:
                    my_score += scoredRow.score
            return f'{my_score}/{max_score}'
        else:
            return None

    @staticmethod
    def get_status_from_string(status):
        return Review.Status.labels[Review.Status.values.index(status)]
