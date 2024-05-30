import os
import ffmpeg
from pytube import Playlist, YouTube
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
_video_base_url = 'http://www.youtube.com/watch?v='


if __name__ == '__main__':
    answers = questionary.form(
        dl_type = questionary.rawselect(
            'Download type',
            choices = ['playlist', 'video'
        ]),
        id = questionary.text('id')
    ).ask()

    id = answers['id']
    if answers['dl_type'] == 'playlist':
        p = Playlist(f'{_playlist_base_url}{id}')
        print(f'{p.title}: {p.length} videos')

        is_getting_highest = questionary.confirm('Getting highest quality?').ask()
        required_word = questionary.text('Included word:').ask()
        fetch_list = p.videos
        if required_word:
            print(f'including word: {required_word}')
            fetch_list = [v for v in p.videos if required_word in v.title]
            for i in fetch_list:
                print(i.title)

        if is_getting_highest:
            for v in fetch_list:
                get_highest_quality(v)
        else:
            for v in fetch_list:
                # download highest progressive videos
                v.streams.get_highest_resolution().download()

    else:
        v = YouTube(f'{_video_base_url}{id}')
        print(v.title)
        get_highest_quality(v)