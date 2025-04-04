import json
from essentia import standard as es
import io
import tempfile
from pydub import AudioSegment
import os
import base64
import numpy as np
# from audio_genre.labels import labels


'''
NOTE Version required for TensorflowPredictEffnetDiscogs is essentia-tensorflow==2.1b6.dev1177
This may also require a new python version

Using a new venv for this environment, need to adjust the python version such that the newer version of essentia can be
found when using lambda

CD into folder before runnning test?
'''

# python3.10 -m venv .venv310
# source .venv310/bin/activate  

# pip install essentia==2.1b6.dev1177


labels = labels = [
    "Blues---Boogie Woogie",
    "Blues---Chicago Blues",
    "Blues---Country Blues",
    "Blues---Delta Blues",
    "Blues---Electric Blues",
    "Blues---Harmonica Blues",
    "Blues---Jump Blues",
    "Blues---Louisiana Blues",
    "Blues---Modern Electric Blues",
    "Blues---Piano Blues",
    "Blues---Rhythm & Blues",
    "Blues---Texas Blues",
    "Brass & Military---Brass Band",
    "Brass & Military---Marches",
    "Brass & Military---Military",
    "Children's---Educational",
    "Children's---Nursery Rhymes",
    "Children's---Story",
    "Classical---Baroque",
    "Classical---Choral",
    "Classical---Classical",
    "Classical---Contemporary",
    "Classical---Impressionist",
    "Classical---Medieval",
    "Classical---Modern",
    "Classical---Neo-Classical",
    "Classical---Neo-Romantic",
    "Classical---Opera",
    "Classical---Post-Modern",
    "Classical---Renaissance",
    "Classical---Romantic",
    "Electronic---Abstract",
    "Electronic---Acid",
    "Electronic---Acid House",
    "Electronic---Acid Jazz",
    "Electronic---Ambient",
    "Electronic---Bassline",
    "Electronic---Beatdown",
    "Electronic---Berlin-School",
    "Electronic---Big Beat",
    "Electronic---Bleep",
    "Electronic---Breakbeat",
    "Electronic---Breakcore",
    "Electronic---Breaks",
    "Electronic---Broken Beat",
    "Electronic---Chillwave",
    "Electronic---Chiptune",
    "Electronic---Dance-pop",
    "Electronic---Dark Ambient",
    "Electronic---Darkwave",
    "Electronic---Deep House",
    "Electronic---Deep Techno",
    "Electronic---Disco",
    "Electronic---Disco Polo",
    "Electronic---Donk",
    "Electronic---Downtempo",
    "Electronic---Drone",
    "Electronic---Drum n Bass",
    "Electronic---Dub",
    "Electronic---Dub Techno",
    "Electronic---Dubstep",
    "Electronic---Dungeon Synth",
    "Electronic---EBM",
    "Electronic---Electro",
    "Electronic---Electro House",
    "Electronic---Electroclash",
    "Electronic---Euro House",
    "Electronic---Euro-Disco",
    "Electronic---Eurobeat",
    "Electronic---Eurodance",
    "Electronic---Experimental",
    "Electronic---Freestyle",
    "Electronic---Future Jazz",
    "Electronic---Gabber",
    "Electronic---Garage House",
    "Electronic---Ghetto",
    "Electronic---Ghetto House",
    "Electronic---Glitch",
    "Electronic---Goa Trance",
    "Electronic---Grime",
    "Electronic---Halftime",
    "Electronic---Hands Up",
    "Electronic---Happy Hardcore",
    "Electronic---Hard House",
    "Electronic---Hard Techno",
    "Electronic---Hard Trance",
    "Electronic---Hardcore",
    "Electronic---Hardstyle",
    "Electronic---Hi NRG",
    "Electronic---Hip Hop",
    "Electronic---Hip-House",
    "Electronic---House",
    "Electronic---IDM",
    "Electronic---Illbient",
    "Electronic---Industrial",
    "Electronic---Italo House",
    "Electronic---Italo-Disco",
    "Electronic---Italodance",
    "Electronic---Jazzdance",
    "Electronic---Juke",
    "Electronic---Jumpstyle",
    "Electronic---Jungle",
    "Electronic---Latin",
    "Electronic---Leftfield",
    "Electronic---Makina",
    "Electronic---Minimal",
    "Electronic---Minimal Techno",
    "Electronic---Modern Classical",
    "Electronic---Musique Concrète",
    "Electronic---Neofolk",
    "Electronic---New Age",
    "Electronic---New Beat",
    "Electronic---New Wave",
    "Electronic---Noise",
    "Electronic---Nu-Disco",
    "Electronic---Power Electronics",
    "Electronic---Progressive Breaks",
    "Electronic---Progressive House",
    "Electronic---Progressive Trance",
    "Electronic---Psy-Trance",
    "Electronic---Rhythmic Noise",
    "Electronic---Schranz",
    "Electronic---Sound Collage",
    "Electronic---Speed Garage",
    "Electronic---Speedcore",
    "Electronic---Synth-pop",
    "Electronic---Synthwave",
    "Electronic---Tech House",
    "Electronic---Tech Trance",
    "Electronic---Techno",
    "Electronic---Trance",
    "Electronic---Tribal",
    "Electronic---Tribal House",
    "Electronic---Trip Hop",
    "Electronic---Tropical House",
    "Electronic---UK Garage",
    "Electronic---Vaporwave",
    "Folk, World, & Country---African",
    "Folk, World, & Country---Bluegrass",
    "Folk, World, & Country---Cajun",
    "Folk, World, & Country---Canzone Napoletana",
    "Folk, World, & Country---Catalan Music",
    "Folk, World, & Country---Celtic",
    "Folk, World, & Country---Country",
    "Folk, World, & Country---Fado",
    "Folk, World, & Country---Flamenco",
    "Folk, World, & Country---Folk",
    "Folk, World, & Country---Gospel",
    "Folk, World, & Country---Highlife",
    "Folk, World, & Country---Hillbilly",
    "Folk, World, & Country---Hindustani",
    "Folk, World, & Country---Honky Tonk",
    "Folk, World, & Country---Indian Classical",
    "Folk, World, & Country---Laïkó",
    "Folk, World, & Country---Nordic",
    "Folk, World, & Country---Pacific",
    "Folk, World, & Country---Polka",
    "Folk, World, & Country---Raï",
    "Folk, World, & Country---Romani",
    "Folk, World, & Country---Soukous",
    "Folk, World, & Country---Séga",
    "Folk, World, & Country---Volksmusik",
    "Folk, World, & Country---Zouk",
    "Folk, World, & Country---Éntekhno",
    "Funk / Soul---Afrobeat",
    "Funk / Soul---Boogie",
    "Funk / Soul---Contemporary R&B",
    "Funk / Soul---Disco",
    "Funk / Soul---Free Funk",
    "Funk / Soul---Funk",
    "Funk / Soul---Gospel",
    "Funk / Soul---Neo Soul",
    "Funk / Soul---New Jack Swing",
    "Funk / Soul---P.Funk",
    "Funk / Soul---Psychedelic",
    "Funk / Soul---Rhythm & Blues",
    "Funk / Soul---Soul",
    "Funk / Soul---Swingbeat",
    "Funk / Soul---UK Street Soul",
    "Hip Hop---Bass Music",
    "Hip Hop---Boom Bap",
    "Hip Hop---Bounce",
    "Hip Hop---Britcore",
    "Hip Hop---Cloud Rap",
    "Hip Hop---Conscious",
    "Hip Hop---Crunk",
    "Hip Hop---Cut-up/DJ",
    "Hip Hop---DJ Battle Tool",
    "Hip Hop---Electro",
    "Hip Hop---G-Funk",
    "Hip Hop---Gangsta",
    "Hip Hop---Grime",
    "Hip Hop---Hardcore Hip-Hop",
    "Hip Hop---Horrorcore",
    "Hip Hop---Instrumental",
    "Hip Hop---Jazzy Hip-Hop",
    "Hip Hop---Miami Bass",
    "Hip Hop---Pop Rap",
    "Hip Hop---Ragga HipHop",
    "Hip Hop---RnB/Swing",
    "Hip Hop---Screw",
    "Hip Hop---Thug Rap",
    "Hip Hop---Trap",
    "Hip Hop---Trip Hop",
    "Hip Hop---Turntablism",
    "Jazz---Afro-Cuban Jazz",
    "Jazz---Afrobeat",
    "Jazz---Avant-garde Jazz",
    "Jazz---Big Band",
    "Jazz---Bop",
    "Jazz---Bossa Nova",
    "Jazz---Contemporary Jazz",
    "Jazz---Cool Jazz",
    "Jazz---Dixieland",
    "Jazz---Easy Listening",
    "Jazz---Free Improvisation",
    "Jazz---Free Jazz",
    "Jazz---Fusion",
    "Jazz---Gypsy Jazz",
    "Jazz---Hard Bop",
    "Jazz---Jazz-Funk",
    "Jazz---Jazz-Rock",
    "Jazz---Latin Jazz",
    "Jazz---Modal",
    "Jazz---Post Bop",
    "Jazz---Ragtime",
    "Jazz---Smooth Jazz",
    "Jazz---Soul-Jazz",
    "Jazz---Space-Age",
    "Jazz---Swing",
    "Latin---Afro-Cuban",
    "Latin---Baião",
    "Latin---Batucada",
    "Latin---Beguine",
    "Latin---Bolero",
    "Latin---Boogaloo",
    "Latin---Bossanova",
    "Latin---Cha-Cha",
    "Latin---Charanga",
    "Latin---Compas",
    "Latin---Cubano",
    "Latin---Cumbia",
    "Latin---Descarga",
    "Latin---Forró",
    "Latin---Guaguancó",
    "Latin---Guajira",
    "Latin---Guaracha",
    "Latin---MPB",
    "Latin---Mambo",
    "Latin---Mariachi",
    "Latin---Merengue",
    "Latin---Norteño",
    "Latin---Nueva Cancion",
    "Latin---Pachanga",
    "Latin---Porro",
    "Latin---Ranchera",
    "Latin---Reggaeton",
    "Latin---Rumba",
    "Latin---Salsa",
    "Latin---Samba",
    "Latin---Son",
    "Latin---Son Montuno",
    "Latin---Tango",
    "Latin---Tejano",
    "Latin---Vallenato",
    "Non-Music---Audiobook",
    "Non-Music---Comedy",
    "Non-Music---Dialogue",
    "Non-Music---Education",
    "Non-Music---Field Recording",
    "Non-Music---Interview",
    "Non-Music---Monolog",
    "Non-Music---Poetry",
    "Non-Music---Political",
    "Non-Music---Promotional",
    "Non-Music---Radioplay",
    "Non-Music---Religious",
    "Non-Music---Spoken Word",
    "Pop---Ballad",
    "Pop---Bollywood",
    "Pop---Bubblegum",
    "Pop---Chanson",
    "Pop---City Pop",
    "Pop---Europop",
    "Pop---Indie Pop",
    "Pop---J-pop",
    "Pop---K-pop",
    "Pop---Kayōkyoku",
    "Pop---Light Music",
    "Pop---Music Hall",
    "Pop---Novelty",
    "Pop---Parody",
    "Pop---Schlager",
    "Pop---Vocal",
    "Reggae---Calypso",
    "Reggae---Dancehall",
    "Reggae---Dub",
    "Reggae---Lovers Rock",
    "Reggae---Ragga",
    "Reggae---Reggae",
    "Reggae---Reggae-Pop",
    "Reggae---Rocksteady",
    "Reggae---Roots Reggae",
    "Reggae---Ska",
    "Reggae---Soca",
    "Rock---AOR",
    "Rock---Acid Rock",
    "Rock---Acoustic",
    "Rock---Alternative Rock",
    "Rock---Arena Rock",
    "Rock---Art Rock",
    "Rock---Atmospheric Black Metal",
    "Rock---Avantgarde",
    "Rock---Beat",
    "Rock---Black Metal",
    "Rock---Blues Rock",
    "Rock---Brit Pop",
    "Rock---Classic Rock",
    "Rock---Coldwave",
    "Rock---Country Rock",
    "Rock---Crust",
    "Rock---Death Metal",
    "Rock---Deathcore",
    "Rock---Deathrock",
    "Rock---Depressive Black Metal",
    "Rock---Doo Wop",
    "Rock---Doom Metal",
    "Rock---Dream Pop",
    "Rock---Emo",
    "Rock---Ethereal",
    "Rock---Experimental",
    "Rock---Folk Metal",
    "Rock---Folk Rock",
    "Rock---Funeral Doom Metal",
    "Rock---Funk Metal",
    "Rock---Garage Rock",
    "Rock---Glam",
    "Rock---Goregrind",
    "Rock---Goth Rock",
    "Rock---Gothic Metal",
    "Rock---Grindcore",
    "Rock---Grunge",
    "Rock---Hard Rock",
    "Rock---Hardcore",
    "Rock---Heavy Metal",
    "Rock---Indie Rock",
    "Rock---Industrial",
    "Rock---Krautrock",
    "Rock---Lo-Fi",
    "Rock---Lounge",
    "Rock---Math Rock",
    "Rock---Melodic Death Metal",
    "Rock---Melodic Hardcore",
    "Rock---Metalcore",
    "Rock---Mod",
    "Rock---Neofolk",
    "Rock---New Wave",
    "Rock---No Wave",
    "Rock---Noise",
    "Rock---Noisecore",
    "Rock---Nu Metal",
    "Rock---Oi",
    "Rock---Parody",
    "Rock---Pop Punk",
    "Rock---Pop Rock",
    "Rock---Pornogrind",
    "Rock---Post Rock",
    "Rock---Post-Hardcore",
    "Rock---Post-Metal",
    "Rock---Post-Punk",
    "Rock---Power Metal",
    "Rock---Power Pop",
    "Rock---Power Violence",
    "Rock---Prog Rock",
    "Rock---Progressive Metal",
    "Rock---Psychedelic Rock",
    "Rock---Psychobilly",
    "Rock---Pub Rock",
    "Rock---Punk",
    "Rock---Rock & Roll",
    "Rock---Rockabilly",
    "Rock---Shoegaze",
    "Rock---Ska",
    "Rock---Sludge Metal",
    "Rock---Soft Rock",
    "Rock---Southern Rock",
    "Rock---Space Rock",
    "Rock---Speed Metal",
    "Rock---Stoner Rock",
    "Rock---Surf",
    "Rock---Symphonic Rock",
    "Rock---Technical Death Metal",
    "Rock---Thrash",
    "Rock---Twist",
    "Rock---Viking Metal",
    "Rock---Yé-Yé",
    "Stage & Screen---Musical",
    "Stage & Screen---Score",
    "Stage & Screen---Soundtrack",
    "Stage & Screen---Theme",
]

def get_genres(audio_bytes):
    '''Return the top n genres for a given audio'''
    assert audio_bytes, "audio_bytes must not be empty"
    assert isinstance(audio_bytes, bytes), "audio_bytes must be of type bytes"

    # Create mp3 audio
    audio_bytes = io.BytesIO(audio_bytes)
    audio = AudioSegment.from_file(audio_bytes, format="mp3")
    number_of_channels = audio.channels
    sample_width = audio.sample_width
    frame_rate = audio.frame_rate

    # Use temp file to get around essentia disk only read , using wav to avoid loss from compression
    temp_audio_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    audio.export(temp_audio_file.name, format="wav")
    # store temp file name
    temp_file_path = temp_audio_file.name
    temp_audio_file.close()

    # load the audio
    audio = es.MonoLoader(filename=temp_file_path, sampleRate=frame_rate, resampleQuality=4)()

    # remove the temp file
    os.remove(temp_audio_file.name)

        
    embedding_model = es.TensorflowPredictEffnetDiscogs(graphFilename="discogs-effnet-bs64-1.pb", output="PartitionedCall:1")
    embeddings = embedding_model(audio)

    model = es.TensorflowPredict2D(graphFilename="genre_discogs400-discogs-effnet-1.pb", input="serving_default_model_Placeholder", output="PartitionedCall:0")
    activations = model(embeddings)

    activations_mean = np.mean(activations, axis=0)

    out = dict(zip(labels, activations_mean.tolist()))
    return out


def process_genres(predictions, n):
    '''Return top n outputs from the function'''
    assert n < len(predictions), 'N must be less than the number of predictions'
    output = dict(sorted(predictions.items(), key=lambda item: item[1], reverse=True)[:n])

    return output

def handler(event, context):
    try:
        # Check structure
        if "body" not in event:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing body in request"})
            }
        
        # Check encoding
        is_base64 = event.get("isBase64Encoded", False)
        if not is_base64:
            return {
                "statusCode": 422,
                "body": json.dumps({"error": "Audio file must be in base64 encoding"})
            }
        
        parameters = event.get("queryStringParameters", False)
        if not parameters:
            return {
                "statusCode": 422,
                "body": json.dumps({"client error": "Missing query parameters - queryStringParameters: params_dict"})
            }
        top_n = parameters.get("top_n", False) 
        if not top_n:
            return {
                "statusCode": 422,
                "body": json.dumps({"client error": "Missing query parameters (top_n)"})
            }
        try:
            top_n = int(top_n)
        except Exception as e:
            return {
                "statusCode": 422,
                "body": json.dumps({"client error": "top_n parameter is not a string"})
            }
    
        # Main function code
        try:
            # Decode body
            binary_data = base64.b64decode(event["body"])
            # Run duration function
            full_output = get_genres(binary_data)
            final_output = process_genres(full_output,top_n)

            return {
                "statusCode": 200,
                "body": json.dumps(final_output)
            }
        # Handle exception from main function
        except Exception as e:
            print("Error:", str(e))
            return {
                "statusCode": 500,
                "body": json.dumps({"error, decoding or duration function failed": str(e)})
            }

    # Catch any other exceptions
    except Exception as e:
        print("Error:", str(e))
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }


