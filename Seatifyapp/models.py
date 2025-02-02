from django.db import models
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

# Branch model
class Branch(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

# Semester model (no relationship with Branch)
class Semester(models.Model):
    name = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name

# SeatingArrangement model with a reference to both Branch and Semester
class SeatingArrangement(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    total_strength = models.IntegerField()
    absentees = models.TextField(help_text="Comma-separated roll numbers of absentees.")
    rows = models.IntegerField()
    columns = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f"Arrangement for {self.branch.name} {self.semester.name}"

# Dashboard view to display the dashboard template
class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'Seatifyapp/dashboard.html'


class SeatingArrangementDataset(models.Model):
    arrangement = models.ForeignKey(SeatingArrangement, on_delete=models.CASCADE)
    seating_data = models.JSONField()  # Store seating data as JSON
    created_at = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return f"Seating Arrangement for {self.arrangement} - {self.created_at}"