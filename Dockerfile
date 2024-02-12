# Use an official Python runtime as a parent image
FROM python:3.9.11

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . .

# Install any needed packages specified in requirements.txt
COPY /app/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Make port 8501 available to the world outside this container
EXPOSE 8501

# Define environment variable
ENV NAME World

# Run streamlit when the container launches
CMD ["streamlit", "run", "./app/experiments/frontend_experiments.py"]

