FROM python:3.12.8-slim-bookworm

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the content of the local repository to the working directory
COPY . .

RUN python manage.py migrate
RUN python manage.py collectstatic

# Specify the port number the container should expose
EXPOSE 8000

# Run Gunicorn to serve the application using the WSGI application defined in [Seatify/wsgi.py](Seatify/wsgi.py)
CMD ["gunicorn", "Seatify.wsgi:application", "--bind", "0.0.0.0:8000"]
