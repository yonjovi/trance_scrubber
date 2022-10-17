# trance_scrubber
## Transcribe youtube videos or get text from audio files you upload.

This is an app created with the recently released Open AI Whisper model.

The App allows you to upload an audio file, or use a Youtube link. The app will then transcribe the text which will be available as a downloadable txt file.

An added feature for the Youtube transcriber option is the fact the text which has been transcribed from the video is then sent for analysis by the Open AI models, which provide a dot point summary of the video's contents, based on the text transcribed.

The files which are uploaded are sent to an Amazon AWS bucket to remove strain from the Streamlit server, but please be mindful to use short videos for this prototype, to avoid impacting the Streamlit server as the app is only using the free tier which provides limited bandwidth.

You can try the app here: https://yonjovi-trance-scrubber-trance-scriber-zbmabx.streamlitapp.com/


Have fun!

Yon
