import os
import logging
import openai
import requests
from musicbrainzngs import set_useragent, search_recordings

# Set up logging for better debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set up OpenAI API key from environment variable
openai.api_key = os.getenv('OPENAI_API_KEY')

# Get the MusicBrainz email from the environment variable and construct the MusicBrainz user-agent string
musicbrainz_email = os.getenv('MUSICBRAINZ_EMAIL', 'default@example.com')
set_useragent("LocalPlaylistGenerator", "1.0", musicbrainz_email)

# Directory where local music files are stored (via volume mount)
MUSIC_LIBRARY_PATH = "/music"

# Directory to save the M3U playlist (via volume mount)
OUTPUT_PATH = "/output"


# Function to interpret prompt using OpenAI
def interpret_prompt(prompt):
    try:
        logger.info("Interpreting user prompt with OpenAI")
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=f"Interpret the following music request: {prompt}",
            max_tokens=100
        )
        return response['choices'][0]['text'].strip()
    except Exception as e:
        logger.error(f"Error interpreting prompt: {e}")
        return None


# Function to search for local music based on interpreted details
def search_local_music(query):
    matching_files = []
    for root, dirs, files in os.walk(MUSIC_LIBRARY_PATH):
        for file in files:
            if file.endswith(('.mp3', '.flac', '.wav')) and query.lower() in file.lower():
                matching_files.append(os.path.join(root, file))
    return matching_files


# Function to query MusicBrainz API with error handling
def get_musicbrainz_data(track_name, artist_name=None):
    try:
        if artist_name:
            results = search_recordings(artist=artist_name, recording=track_name, limit=1)
        else:
            results = search_recordings(recording=track_name, limit=1)
        if results['recording-list']:
            return results['recording-list'][0]
        else:
            logger.warning(f"No MusicBrainz data found for {track_name}")
            return None
    except Exception as e:
        logger.error(f"Error querying MusicBrainz for {track_name}: {e}")
        return None


# Function to create an M3U playlist
def create_m3u_playlist(tracks, playlist_name="playlist.m3u"):
    playlist_path = os.path.join(OUTPUT_PATH, playlist_name)
    try:
        with open(playlist_path, 'w') as playlist:
            playlist.write("#EXTM3U\n")
            for track in tracks:
                playlist.write(f"{track}\n")
        logger.info(f"M3U playlist saved as {playlist_path}")
    except Exception as e:
        logger.error(f"Error creating M3U playlist: {e}")


# Main function to create a playlist from a natural language prompt
def create_playlist_from_prompt(prompt):
    # Interpret the user prompt
    interpreted_prompt = interpret_prompt(prompt)
    if not interpreted_prompt:
        logger.error("Failed to interpret the prompt.")
        return

    logger.info(f"Interpreted Prompt: {interpreted_prompt}")

    # Search local music files
    matching_tracks = search_local_music(interpreted_prompt)
    logger.info(f"Found {len(matching_tracks)} matching tracks in the local library.")

    # Get additional metadata from MusicBrainz
    final_tracks = []
    for track in matching_tracks:
        track_name = os.path.basename(track)
        musicbrainz_data = get_musicbrainz_data(track_name)
        if musicbrainz_data:
            logger.info(f"Found metadata for {track_name}")
        final_tracks.append(track)

    # Create the M3U playlist
    create_m3u_playlist(final_tracks, playlist_name="my_playlist.m3u")


# Example usage
if __name__ == "__main__":
    user_prompt = input("Enter your playlist request: ")
    create_playlist_from_prompt(user_prompt)
