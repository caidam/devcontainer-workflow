# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory in the container to /app
WORKDIR /app

# Add the current directory contents into the container at /app
ADD . /app

# Upgrade pip to the latest version
RUN pip install --no-cache-dir --upgrade pip

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 5000
EXPOSE 80
EXPOSE 443

# Run db_utils.py and then app.py when the container launches
CMD ["sh", "-c", "python db_utils.py && python app.py"]