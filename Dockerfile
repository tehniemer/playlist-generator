# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the requirements.txt file into the container
COPY requirements.txt .  # Make sure we copy requirements.txt first

# Install system dependencies required to build Python packages
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
COPY . .

# Set environment variables for OpenAI API key
ENV OPENAI_API_KEY="your_openai_api_key"

# Set environment variable for MusicBrainz email
ENV MUSICBRAINZ_EMAIL="your_email@example.com"

# Make port 8080 available to the world outside this container (if using a web interface)
EXPOSE 8080

# Set the entry point so that the script will build the MusicBrainz user-agent string dynamically
CMD ["sh", "-c", "python ./script.py --email $MUSICBRAINZ_EMAIL"]
