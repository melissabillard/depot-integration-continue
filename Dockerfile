FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install packages from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Define port
EXPOSE 8000

# We can define environment variables here if needed

# Run app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "info"]