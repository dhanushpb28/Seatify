from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import Branch, Semester, SeatingArrangement, SeatingArrangementDataset
from .forms import SeatingArrangementForm, BranchForm, SemesterForm
import random
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from datetime import datetime
from django.contrib.auth.models import User
from django import forms
from django.core.exceptions import ValidationError

# Add a new branch
def add_branch(request):
    if request.method == 'POST':
        form = BranchForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = BranchForm()
    return render(request, 'Seatifyapp/add_branch.html', {'form': form})

# Add a new semester
def add_semester(request):
    if request.method == 'POST':
        form = SemesterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = SemesterForm()
    return render(request, 'Seatifyapp/add_semester.html', {'form': form})

# Delete a branch
def delete_branch(request, branch_id):
    branch = get_object_or_404(Branch, id=branch_id)
    branch.delete()
    return redirect('dashboard')

# Delete a semester
def delete_semester(request, semester_id):
    semester = get_object_or_404(Semester, id=semester_id)
    semester.delete()
    return redirect('dashboard')


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ['email', 'password1', 'password2']
        # We're using email as the username, so no 'username' field is required

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email.endswith('@mgits.ac.in'):
            raise ValidationError("Please use an email ending with '@mgits.ac.in'.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']  # Set the email as the username
        if commit:
            user.save()
        return user

# Update the view to use the custom form
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration successful! You can now log in.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'Seatifyapp/register.html', {'form': form})
@login_required
def dashboard(request):
    branches = Branch.objects.all()
    semesters = Semester.objects.all()
    return render(request, 'Seatifyapp/dashboard.html', {'branches': branches, 'semesters': semesters})

@login_required
def create_seating(request):
    if request.method == 'POST':
        form = SeatingArrangementForm(request.POST)
        if form.is_valid():
            total_strength = form.cleaned_data['total_strength']
            rows = form.cleaned_data['rows']
            columns = form.cleaned_data['columns']
            capacity = rows * columns * 2  # Each desk can hold two students

            if total_strength > capacity:
                form.add_error(None, "The total strength exceeds the available seating capacity. Please adjust rows or columns.")
            else:
                arrangement = form.save()
                return redirect('preview_seating', pk=arrangement.id)
    else:
        form = SeatingArrangementForm()
    
    return render(request, 'Seatifyapp/seating_form.html', {'form': form})

def preview_seating(request, pk):
    arrangement = SeatingArrangement.objects.get(pk=pk)
    
    # Generate seating
    absentees = arrangement.absentees or ""  # Handle None case
    absentees_list = [int(a) for a in absentees.split(',') if a.strip().isdigit()]  # Convert valid numbers only
    total_students = list(set(range(1, arrangement.total_strength + 1)) - set(absentees_list))

    # Shuffle students
    random.shuffle(total_students)
    
    # Initialize seating layout (only store student pairs)
    seating = []
    index = 0
    
    # Create seating arrangement (rows and columns layout)
    for r in range(arrangement.rows):
        row = []
        for c in range(arrangement.columns):
            if index < len(total_students):
                student_pair = (total_students[index], total_students[index + 1] if index + 1 < len(total_students) else None)
                row.append(student_pair)
                index += 2
            else:
                row.append((None, None))  # Empty desk
        seating.append(row)

    # Transpose the seating grid to switch rows and columns
    transposed_seating = [[seating[j][i] for j in range(len(seating))] for i in range(len(seating[0]))]
    
    # Save the seating arrangement to the dataset table
    seating_dataset = SeatingArrangementDataset.objects.create(
        arrangement=arrangement,
        seating_data=transposed_seating
    )
    
    return render(request, 'Seatifyapp/seating_preview.html', {
        'seating': transposed_seating,
        'arrangement': arrangement,
        'rows_range': list(range(arrangement.rows)),
        'columns_range': list(range(arrangement.columns)),
    })

@login_required
def download_pdf(request, pk):
    seating_dataset = SeatingArrangementDataset.objects.filter(arrangement__pk=pk).first()
    if not seating_dataset:
        return HttpResponse("Seating arrangement not found.", status=404)
    
    seating_data = seating_dataset.seating_data
    arrangement = seating_dataset.arrangement
    
    transposed_seating = [[seating_data[j][i] for j in range(len(seating_data))] for i in range(len(seating_data[0]))]
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="seating_arrangement_{pk}.pdf"'
    
    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4
    
    # Title: "Seating Arrangement Preview"
    p.setFont("Helvetica-Bold", 16)
    p.setFillColor(HexColor("#003366"))  # Dark Blue color
    title_width = p.stringWidth("Seating Arrangement Preview", "Helvetica-Bold", 16)
    p.drawString((width - title_width) / 2, height - 50, "Seating Arrangement Preview")
    
    # Reset color to black for normal text
    p.setFillColor(HexColor("#000000"))
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, height - 90, "Branch:")
    p.setFont("Helvetica", 12)
    p.drawString(120, height - 90, arrangement.branch.name)
    
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, height - 110, "Semester:")
    p.setFont("Helvetica", 12)
    p.drawString(120, height - 110, arrangement.semester.name)
    
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, height - 130, "Dates:")
    p.setFont("Helvetica", 12)
    start_date = arrangement.start_date.strftime("%b. %d, %Y")
    end_date = arrangement.end_date.strftime("%b. %d, %Y")
    p.drawString(120, height - 130, f"{start_date} to {end_date}")
    
    # Blackboard Label inside a dark box
    blackboard_text = "Blackboard"
    box_x, box_y, box_width, box_height = 50, height - 180, width - 100, 40
    p.setFillColor(HexColor("#333333"))  # Dark Gray color
    p.rect(box_x, box_y, box_width, box_height, fill=True, stroke=False)
    
    p.setFont("Helvetica-Bold", 14)
    p.setFillColor(HexColor("#FFFFFF"))  # White text for contrast
    text_x = box_x + (box_width - p.stringWidth(blackboard_text, "Helvetica-Bold", 14)) / 2
    text_y = box_y + (box_height / 2) + 5
    p.drawString(text_x, text_y, blackboard_text)
    
    # Reset fill color to black for normal content
    p.setFillColor(HexColor("#000000"))
    
    # Seating arrangement table below this section (adjusted for better readability)
    p.setFont("Helvetica", 9)
    y_position = height - 240  # Adjusted position
    x_position_start = 50
    desk_width, desk_height, x_gap, y_gap = 80, 40, 10, 10  # Increased desk size
    
    for row in transposed_seating:
        x_position = x_position_start
        for student_pair in row:
            p.setStrokeColorRGB(0, 0, 0)
            p.setLineWidth(0.5)
            p.rect(x_position, y_position, desk_width, desk_height)
            student1 = str(student_pair[0]) if student_pair[0] else "Empty"
            student2 = str(student_pair[1]) if student_pair[1] else "Empty"
            p.setFont("Helvetica", 8)
            text_x = x_position + 5
            text_y = y_position + desk_height / 2
            p.drawString(text_x, text_y, f"{student1}, {student2}")  # Horizontally aligned roll numbers
            x_position += desk_width + x_gap
        y_position -= desk_height + y_gap
        if y_position < 100:
            p.showPage()
            y_position = height - 220
    
    p.setFont("Helvetica", 8)
    p.drawString(width - 50, 30, "Page 1")
    p.showPage()
    p.save()
    
    return response