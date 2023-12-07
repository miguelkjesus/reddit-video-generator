# original file from: https://github.com/oscie57/tiktok-voice
# slightly modified for use in this project

import threading, requests, base64, re
from playsound import playsound

VOICES = [
    # DISNEY VOICES
    'en_us_ghostface',            # Ghost Face
    'en_us_chewbacca',            # Chewbacca
    'en_us_c3po',                 # C3PO
    'en_us_stitch',               # Stitch
    'en_us_stormtrooper',         # Stormtrooper
    'en_us_rocket',               # Rocket

    # ENGLISH VOICES
    'en_au_001',                  # English AU - Female
    'en_au_002',                  # English AU - Male
    'en_uk_001',                  # English UK - Male 1
    'en_uk_003',                  # English UK - Male 2
    'en_us_001',                  # English US - Female (Int. 1)
    'en_us_002',                  # English US - Female (Int. 2)
    'en_us_006',                  # English US - Male 1
    'en_us_007',                  # English US - Male 2
    'en_us_009',                  # English US - Male 3
    'en_us_010',                  # English US - Male 4

    # EUROPE VOICES
    'fr_001',                     # French - Male 1
    'fr_002',                     # French - Male 2
    'de_001',                     # German - Female
    'de_002',                     # German - Male
    'es_002',                     # Spanish - Male

    # AMERICA VOICES
    'es_mx_002',                  # Spanish MX - Male
    'br_001',                     # Portuguese BR - Female 1
    'br_003',                     # Portuguese BR - Female 2
    'br_004',                     # Portuguese BR - Female 3
    'br_005',                     # Portuguese BR - Male

    # ASIA VOICES
    'id_001',                     # Indonesian - Female
    'jp_001',                     # Japanese - Female 1
    'jp_003',                     # Japanese - Female 2
    'jp_005',                     # Japanese - Female 3
    'jp_006',                     # Japanese - Male
    'kr_002',                     # Korean - Male 1
    'kr_003',                     # Korean - Female
    'kr_004',                     # Korean - Male 2

    # SINGING VOICES
    'en_female_f08_salut_damour',  # Alto
    'en_male_m03_lobby',           # Tenor
    'en_female_f08_warmy_breeze',  # Warmy Breeze
    'en_male_m03_sunshine_soon',   # Sunshine Soon

    # OTHER
    'en_male_narration',           # narrator
    'en_male_funny',               # wacky
    'en_female_emotional',         # peaceful
]

ENDPOINTS = ['https://tiktok-tts.weilnet.workers.dev/api/generation', "https://tiktoktts.com/api/tiktok-tts"]
current_endpoint = 0
# in one conversion, the text can have a maximum length of 300 characters
TEXT_BYTE_LIMIT = 300

# create a list by splitting a string, every element has n chars
def split_string(string: str, chunk_size: int) -> list[str]:
    sentences = re.split(r"(?<=\w[\.,]) |\n+", string)
    result = []
    current_chunk = ''
    for i, sentence in enumerate(sentences):
        if len(sentence) > chunk_size:
            raise ValueError(f"Sentence {i} is longer than {chunk_size} characters.")
        elif len(current_chunk) + len(sentence) + 1 <= chunk_size:  # Check if adding the sentence exceeds the chunk size
            current_chunk += ' ' + sentence
        else:
            if current_chunk:  # Append the current chunk if not empty
                result.append(current_chunk.strip())
            current_chunk = sentence

    if current_chunk:  # Append the last chunk if not empty
        result.append(current_chunk.strip())
        
    return result

# checking if the website that provides the service is available
def get_api_response() -> requests.Response:
    url = f'{ENDPOINTS[current_endpoint].split("/a")[0]}'
    response = requests.get(url)
    return response

# send POST request to get the audio data
def generate_audio(text: str, voice: str) -> bytes:
    url = f'{ENDPOINTS[current_endpoint]}'
    headers = {'Content-Type': 'application/json'}
    data = {'text': text, 'voice': voice}
    response = requests.post(url, headers=headers, json=data)
    return response.content


# creates an text to speech audio file
def tts(text: str, voice: str = None, outpath: str = None) -> bytes:
    # checking if the website is available
    global current_endpoint

    if get_api_response().status_code != 200:
        current_endpoint = (current_endpoint + 1) % 2
        if get_api_response().status_code != 200:
            raise Exception("Service not available and probably temporarily rate limited, try again later...")
    
    # checking if arguments are valid
    if voice is None:
        raise ValueError("No voice has been selected")
    
    if not voice in VOICES:
        raise ValueError("Voice does not exist")

    if len(text) == 0:
        raise ValueError("Text must be > 0 characters")

    # creating the audio file
    try:
        if len(text) < TEXT_BYTE_LIMIT:
            audio = generate_audio((text), voice)
            if current_endpoint == 0:
                audio_base64_data = str(audio).split('"')[5]
            else:
                audio_base64_data = str(audio).split('"')[3].split(",")[1]
            
            if audio_base64_data == "error":
                raise ValueError("This voice is unavailable right now")
                
        else:
            # Split longer text into smaller parts
            text_parts = split_string(text, 299)
            audio_base64_data = [None] * len(text_parts)
            
            # Define a thread function to generate audio for each text part
            def generate_audio_thread(text_part, index):
                audio = generate_audio(text_part, voice)
                if current_endpoint == 0:
                    base64_data = str(audio).split('"')[5]
                else:
                    base64_data = str(audio).split('"')[3].split(",")[1]

                if audio_base64_data == "error":
                    raise ValueError("This voice is unavailable right now")
            
                audio_base64_data[index] = base64_data

            threads = []
            for index, text_part in enumerate(text_parts):
                # Create and start a new thread for each text part
                thread = threading.Thread(target=generate_audio_thread, args=(text_part, index))
                thread.start()
                threads.append(thread)

            # Wait for all threads to complete
            for thread in threads:
                thread.join()

            # Concatenate the base64 data in the correct order
            audio_base64_data = "".join(audio_base64_data)
            
        audio_bytes = base64.b64decode(audio_base64_data)
        if outpath is not None:
            with open(outpath, "wb") as file:
                file.write(audio_bytes)

        return audio_bytes
    
    except Exception as e:
        print("Error occurred while generating audio:", e)
