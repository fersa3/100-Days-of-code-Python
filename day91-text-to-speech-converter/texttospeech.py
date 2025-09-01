import requests


class TextToSpeech():
    def __init__(self):
        self.url = "https://express-voic-text-to-speech.p.rapidapi.com/"


    def get_services(self):
        """ Gives yhou a list of 12 services like TikTok, Google Translate, iSpeech... """
        url = f"{self.url}getServices"

        headers = {
            "x-rapidapi-key": "ef9ce7c8d4msh1598df6e919b4cap171091jsnd75e64a52a86",
            "x-rapidapi-host": "express-voic-text-to-speech.p.rapidapi.com"
        }

        response = requests.get(url, headers=headers)

        print(response.json())

    def get_voice(self):
        """ Given a Service from the list above, will give you a dictionary with male and female lists of voices to choose from """
        import requests

        url = f"{self.url}getVoice"

        querystring = {"service": "StreamElements"}

        headers = {
            "x-rapidapi-key": "ef9ce7c8d4msh1598df6e919b4cap171091jsnd75e64a52a86",
            "x-rapidapi-host": "express-voic-text-to-speech.p.rapidapi.com"
        }

        response = requests.get(url, headers=headers, params=querystring)

        print(response.json())

    def get_all_voice(self):
        """ Gives you all the services and voices available. """
        url = f"{self.url}getAllVoice"

        headers = {
            "x-rapidapi-key": "ef9ce7c8d4msh1598df6e919b4cap171091jsnd75e64a52a86",
            "x-rapidapi-host": "express-voic-text-to-speech.p.rapidapi.com"
        }

        response = requests.get(url, headers=headers)

        print(response.json())

    def get_audiolink(self, pdf_text, chosen_voice):
        """ Given a text-to-speech service, a voice and a text, will provide an audio url (.mp3)"""
        url = f"{self.url}getAudioLink"

        querystring = {"service": "StreamElements", "voice": chosen_voice,  # Example: "Brian"
                       "text": pdf_text}

        headers = {
            "x-rapidapi-key": "ef9ce7c8d4msh1598df6e919b4cap171091jsnd75e64a52a86",
            "x-rapidapi-host": "express-voic-text-to-speech.p.rapidapi.com"
        }

        response = requests.get(url, headers=headers, params=querystring)
        print(response.json())



