FROM python:3.12.0-slim-buster

# Set the working directory in the container

WORKDIR /app

# Copy the dependencies file to the working directory

COPY requirements.txt .

# Install any dependencies

RUN pip install --no-cache-dir -r requirements.txt


# Copy the content of the local src directory to the working directory

COPY . .

# Create a volume for the SQLite database file

VOLUME ["/app/db/db.sqlite3"]

# Specify the port number the container should expose

EXPOSE 8000

# Run the application

CMD ["python", "manage.py", "runserver"]

