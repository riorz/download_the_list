import os
import ffmpeg
from pytube import Playlist, YouTube
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import SRTFormatter
import questionary


def combine_video(video: str, audio: str)->None:
    filename = video.split('.')[0]
    video_stream = ffmpeg.input(video)
    audio_stream = ffmpeg.input(audio)
    ffmpeg.output(audio_stream, video_stream, f'{filename}.mp4', loglevel='quiet').run()
    os.remove(video)
    os.remove(audio)


def get_highest_quality(v: YouTube)->None:
    v.streams.filter(adaptive=True).order_by('resolution').last().download()
    v.streams.filter(only_audio=True).asc().last().download(filename_prefix='audio_')
    video = v.streams.filter(adaptive=True).order_by('resolution').last().default_filename
    audio = f'audio_{v.streams.filter(only_audio=True).asc().last().default_filename}'
    combine_video(video, audio)


_playlist_base_url = 'https://www.youtube.com/playlist?list='
_video_base_url = 'https://www.youtube.com/watch?v='
_output_path = 'download/'


if __name__ == '__main__':
    answers = questionary.form(
        dl_type = questionary.select(
            'Download type',
            choices = ['playlist', 'video']
        ),
        dl_id = questionary.text('id')
    ).ask()

    dl_type, dl_id = answers['dl_type'], answers['dl_id']
    if dl_type == 'playlist':
        p = Playlist(f'{_playlist_base_url}{dl_id}')
        print(f'{p.title}: {p.length} videos')

        #is_getting_highest = questionary.confirm('Getting highest quality?').ask()
        is_getting_highest = None
        # required_word = questionary.text('keyword:').ask()
        required_word = None

        fetch_list = p.videos

        if required_word:
            print(f'keyword: {required_word}')
            fetch_list = [v for v in p.videos if required_word in v.title]
            for i in fetch_list:
                print(i.title)

        if is_getting_highest:
            for v in fetch_list:
                get_highest_quality(v)
        else:
            for v in fetch_list:
                # download highest progressive videos
                v.streams.get_highest_resolution().download(output_path=_output_path)
                transcript = YouTubeTranscriptApi.get_transcript(v.video_id, languages=['en', 'ja'])
                formatter = SRTFormatter()
                srt_formatted = formatter.format_transcript(transcript)
                with open(f'{_output_path}/{v.title}.srt', 'w', encoding='utf-8') as srt_file:
                    srt_file.write(srt_formatted)

    else:
        v = YouTube(f'{_video_base_url}{dl_id}')
        print(v.title)
        get_highest_quality(v)