from texttospeech import TextToSpeech
from PyPDF2 import PdfReader

# Instructions:
# 1. Drop your file into the Input folder.
# 2. Select the language your pdf is in.
# 3. Run the Text to Speech script.

#---------------- READ PDF ----------------#

reader = PdfReader("Input/Manuel Gutiérrez Nájera.pdf")
number_of_pages = len(reader.pages)
page = reader.pages[0]
pdf_text = page.extract_text()

#---------------- SELECT LANGUAGE AND VOICE ----------------#

available_voices = {'voices':
                        {'StreamElements':
                             {'MALE': ['', 'Brian (English, British)', 'Joey (English, American)', 'Sebastian (German)', 'Miguel (Spanish, American)', 'Mathieu (French)'],
                              'FEMALE': ['', 'Amy (English, British)', 'Ivy (English, American)', 'Marlene (German)', 'Mia (Spanish, Mexican)', 'Céline (French)']
                              }
                        }
                    }

# Select voices from dictionary based on user's choice. IDEA: Buscar en los elementos en la lista, por eso el 0 vacío...
print("In which language is your text?")
# Make it an int between 1 and 5
language = int(input(" 1. English, British\n 2. English, American\n 3. German\n 4. Spanish\n 5. French\n"))
print("Do you want to hear this in a male or female voice?")
# Make it an int between 1 and 2
gender = int(input(" 1. Male\n 2. Female\n"))

# Acceder al diccionario:
if gender == 1:
    y = "MALE"
else:
    y = "FEMALE"

names_list = available_voices['voices']['StreamElements'][y]
chosen_voice = names_list[language].split(" ")[0]
print(chosen_voice)

#---------------- CONVERT TO AUDIO ----------------#

converter = TextToSpeech()
converter.get_audiolink(pdf_text=pdf_text, chosen_voice=chosen_voice)
