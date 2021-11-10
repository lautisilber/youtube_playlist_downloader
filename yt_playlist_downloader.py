'''
	created by Lautaro Silbergleit on 2021
'''

import re
from pytube import Playlist, YouTube
import sys
from tqdm import tqdm
from os import makedirs
from os.path import join, exists
import json
from time import sleep


def main():
	PLAYLIST_URL_PATH = 'playlist_urls.json'
	PLAYLIST_DOWNLOAD_PATH = 'playlists'

	if not exists(PLAYLIST_URL_PATH):
		create = input(f"There's no file named {PLAYLIST_URL_PATH} in this directory\nDo you want to create one [y/n]")
		create = True if create in ['y', 'Y', 'yes', 'Yes'] else False
		if create:
			with open(PLAYLIST_URL_PATH, 'w') as f:
				json.dump(['playlist_url_1', 'playlist_url_2', 'playlist_url_3', '...'], f)
		return

	with open(PLAYLIST_URL_PATH, 'r') as f:
		playlist_urls = json.load(f)

	assert isinstance(playlist_urls, list)

	for playlist_url in playlist_urls:
		playlist = Playlist(playlist_url)
		playlist._video_regex = re.compile(r"\"url\":\"(/watch\?v=[\w-]*)")
		print(f"\n downloading playlist: '{playlist.title}")

		path = join(PLAYLIST_DOWNLOAD_PATH, playlist.title)
		if not exists(path):
			makedirs(path)

		video_urls = list(playlist.video_urls)
		for video_url in tqdm(video_urls):
			youtube = YouTube(video_url)
			if not exists(join(path, youtube.title)):
				video = youtube.streams.get_highest_resolution()
				video.download(path)
			else:
				sleep(.05)
		print('done')



if __name__ == '__main__':
	main()
