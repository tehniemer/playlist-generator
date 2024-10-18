# Stage 1: Build stage
FROM python:3.10-slim as build

# Install system dependencies required to build Python packages
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies in a separate layer to cache them
RUN pip install --no-cache-dir openai musicbrainzngs

# Stage 2: Final stage
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the installed dependencies from the build stage
COPY --from=build /usr/local/lib/python3.10 /usr/local/lib/python3.10
COPY --from=build /usr/local/bin/ /usr/local/bin/

# Copy the rest of the application files
COPY . .

# Set environment variables for OpenAI API key
ENV OPENAI_API_KEY="your_openai_api_key"

# Set environment variable for MusicBrainz email
ENV MUSICBRAINZ_EMAIL="your_email@example.com"

# Expose directories for volume mounts (music files and output playlist)
VOLUME ["/music", "/output"]

# Make port 8080 available to the world outside this container (if using a web interface)
EXPOSE 8080
