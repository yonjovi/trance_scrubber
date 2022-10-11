import whisper
import streamlit as st
import streamlit_ext as ste
import boto3
import time
import pytube


s3 = boto3.client('s3',
                  region_name=st.secrets['region_name'],
                  aws_access_key_id=st.secrets['aws_access_key_id'],
                  aws_secret_access_key=st.secrets['aws_secret_access_key'])

formatted_result_app = None
p_url = None
yt_video = None


def upload_audio_to_s3(file, bucket, s3_file):
    try:
        s3.upload_fileobj(file, bucket, s3_file)
        return True
    except FileNotFoundError:
        time.sleep(9)
        st.error('File not found.')
        return False


st.header('Transcribe this!')
st.write('Upload an audio file in any language and let me transcribe it for you 🥳')
st.write('')
transcribe_choice = st.radio(
    'Upload your audio or choose a Youtube video to transcribe:',
    key='choices',
    options=['Upload audio file', 'Transcribe Youtube video']
)
st.write(transcribe_choice)

with st.form('silent-whisper', clear_on_submit=False):
    if transcribe_choice == 'Upload audio file':
        uploaded_file = st.file_uploader('Choose an audio file', accept_multiple_files=False, type=['wav', 'aif', 'mp3',
                                                                                                    'aiff', 'flac',
                                                                                                    'aac', 'mp4',
                                                                                                    'wma', 'ogg'])
        submitted = st.form_submit_button('TRANSCRIBE!')

        if uploaded_file is not None:
            try:
                with st.spinner('Getting ready...'):
                    upload_audio_to_s3(uploaded_file, st.secrets['bucket_name'], uploaded_file.name)

                    p_url = s3.generate_presigned_url(
                        ClientMethod='get_object',
                        Params={'Bucket': st.secrets['bucket_name'], 'Key': uploaded_file.name},
                        ExpiresIn=1800
                    )
                if p_url is not None:
                    st.success('Let\'s go!', icon='🕺')
                with st.spinner('Transcribing...'):
                    model = whisper.load_model('base')
                    result = model.transcribe(p_url, fp16=False)
                    result_app = result['text']
                    if result_app == '':
                        st.warning('I have no words...(to transcribe)', icon='🤖')
                    else:
                        formatted_result_app = f'Transcribed text from "{uploaded_file.name}": \n\n{result_app}'
                        st.subheader(f'Transcribed text from "{uploaded_file.name}":')
                        st.write(result_app)
                        st.write('')
                        st.write('')
            except RuntimeError:
                st.warning('Please upload an audio file or try again!', icon='🧐')
    elif transcribe_choice == 'Transcribe Youtube video':
        try:
            yt_link = st.text_input("Enter a Youtube link:")
            submitted = st.form_submit_button('TRANSCRIBE!')
            if submitted:
                with st.spinner('Fetching video'):
                    yt_video = pytube.YouTube(yt_link)
                    yt_video_filter = yt_video.streams.filter(file_extension='mp4')
                    yt_stream = yt_video.streams.get_by_itag(139)
                    yt_filename = f'{yt_video.title}.mp4'
                    yt_stream_dl = yt_stream.download('', yt_filename)
                    # time.sleep(1)
                with st.spinner('Transcribing...'):
                    with open(yt_stream_dl, 'rb') as f:
                        s3.upload_fileobj(f, st.secrets['bucket_name'], yt_filename)

                    p_url = s3.generate_presigned_url(
                        ClientMethod='get_object',
                        Params={'Bucket': st.secrets['bucket_name'], 'Key': yt_filename},
                        ExpiresIn=1800
                    )
                    model = whisper.load_model('base')
                    result = model.transcribe(p_url, fp16=False)
                    result_app = result['text']
                    if result_app == '':
                        st.warning('I have no words...(to transcribe)', icon='🤖')
                    else:
                        formatted_result_app = f'Transcribed text from "{yt_video.title}": \n\n{result_app}'
                        st.subheader(f'Transcribed text from "{yt_video.title}":')
                        st.caption("results below the video")
                        st.video(str(yt_link))
                        st.write(result_app)
                        st.write('')
                        st.write('')

        except:
            st.error('Hmm that doesn\'t look like a Youtube link to me...🙄🙄🙄 Try again perhaps? 🤷‍')
if formatted_result_app is not None and yt_video is not None:
    ste.download_button('Download', formatted_result_app,
                        f'{yt_video.title} transcribed.txt')
elif formatted_result_app is not None and uploaded_file is not None:
    ste.download_button('Download', formatted_result_app,
                        f'{uploaded_file.name} transcribed.txt')
