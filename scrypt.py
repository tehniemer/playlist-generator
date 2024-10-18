import os
import openai
import requests
from musicbrainzngs import set_useragent, search_recordings

# Set up OpenAI API key from environment variable
openai.api_key = os.getenv('OPENAI_API_KEY')

# Get the MusicBrainz email from the environment variable and construct the MusicBrainz user-agent string
musicbrainz_email = os.getenv('MUSICBRAINZ_EMAIL', 'default@example.com')
set_useragent("LocalPlaylistGenerator", "1.0", musicbrainz_email)

# Directory where the local music files are stored
MUSIC_LIBRARY_PATH = "/path/to/local/music"

# Function to interact with OpenAI API to process user input
def interpret_prompt(prompt):
    response = openai.Completion.create(
        engine="text-davinci-003",  # Choose the model
        prompt=f"Interpret the following music request: {prompt}",
        max_tokens=100
    )
    return response['choices'][0]['text'].strip()

# Function to search for music in local library based on metadata
def search_local_music(query):
    matching_files = []
    for root, dirs, files in os.walk(MUSIC_LIBRARY_PATH):
        for file in files:
            if file.endswith(('.mp3', '.flac', '.wav')) and query.lower() in file.lower():
                matching_files.append(os.path.join(root, file))
    return matching_files

# Function to query MusicBrainz for metadata
def get_musicbrainz_data(track_name, artist_name=None):
    try:
        if artist_name:
            results = search_recordings(artist=artist_name, recording=track_name, limit=1)
        else:
            results = search_recordings(recording=track_name, limit=1)
        return results['recording-list'][0] if results['recording-list'] else None
    except Exception as e:
        print(f"Error querying MusicBrainz: {e}")
        return None

# Function to create an M3U playlist
def create_m3u_playlist(tracks, playlist_name="playlist.m3u"):
    with open(playlist_name, 'w') as playlist:
        playlist.write("#EXTM3U\n")
        for track in tracks:
            playlist.write(f"{track}\n")
    print(f"M3U playlist saved as {playlist_name}")

# Main function to create a playlist from a natural language prompt
def create_playlist_from_prompt(prompt):
    # Step 1: Interpret the user prompt
    interpreted_prompt = interpret_prompt(prompt)
    print(f"Interpreted Prompt: {interpreted_prompt}")

    # Step 2: Search local music based on interpreted details
    # For simplicity, let's assume interpreted prompt includes a keyword like genre or artist
    matching_tracks = search_local_music(interpreted_prompt)
    print(f"Found {len(matching_tracks)} matching tracks in the local library.")

    # Step 3: Optionally get more metadata from MusicBrainz (could be slow)
    final_tracks = []
    for track in matching_tracks:
        track_name = os.path.basename(track)
        musicbrainz_data = get_musicbrainz_data(track_name)
        if musicbrainz_data:
            print(f"Found metadata for {track_name}")
        final_tracks.append(track)

    # Step 4: Create an M3U playlist
    create_m3u_playlist(final_tracks, playlist_name="my_playlist.m3u")

# Example usage
if __name__ == "__main__":
    user_prompt = input("Enter your playlist request: ")
    create_playlist_from_prompt(user_prompt)
