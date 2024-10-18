# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables for OpenAI API key
ENV OPENAI_API_KEY="your_openai_api_key"

# Define the user's email as an environment variable for MusicBrainz
ENV MUSICBRAINZ_EMAIL="your_email@example.com"

# Make port 8080 available to the world outside this container (if using a web interface)
EXPOSE 8080

# Set the entry point so that the script will build the MusicBrainz user-agent string dynamically
CMD ["sh", "-c", "python ./script.py --email $MUSICBRAINZ_EMAIL"]
