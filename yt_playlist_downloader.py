'''
	created by Lautaro Silbergleit on 2021
'''

import re
from pytube import Playlist, YouTube
from tqdm import tqdm
from os import makedirs, listdir, remove
from os.path import join, exists, isfile
import json
from time import sleep

SENSITIVE_CHARACTERS = ['%', ':']

def main():
	PLAYLIST_URL_PATH = 'playlist_urls.json'
	PLAYLIST_VIDEOS_URLS_PATH = '.playlist_videos_urls.json'
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

	# create file with all video's urls
	if not exists(PLAYLIST_VIDEOS_URLS_PATH):
		with open(PLAYLIST_VIDEOS_URLS_PATH, 'w') as f:
			json.dump({}, f)

	assert isinstance(playlist_urls, list)

	for playlist_url in playlist_urls: # for each playlist
		playlist = Playlist(playlist_url)
		playlist._video_regex = re.compile(r"\"url\":\"(/watch\?v=[\w-]*)")
		playlist_name = playlist.title
		print(f"\n Downloading playlist: '{playlist_name}'")

		# create playlist download directory
		path = join(PLAYLIST_DOWNLOAD_PATH, playlist.title)
		if not exists(path):
			makedirs(path)

		playlist_length = len(list(playlist.video_urls))
		with open(PLAYLIST_VIDEOS_URLS_PATH, 'r') as f:
			saved_urls = json.load(f)
		if not playlist_name in saved_urls:
			saved_urls[playlist_name] = []
		if len(saved_urls[playlist_name]) != playlist_length:
			saved_urls[playlist_name] = []
			print('Gathering video info...')
			for url in tqdm(list(playlist.video_urls)):
				youtube = YouTube(url)
				title = youtube.title
				for c in SENSITIVE_CHARACTERS:
					title = title.replace(c, '')
				saved_urls[playlist_name].append({'url':url, 'title': title})
			with open(PLAYLIST_VIDEOS_URLS_PATH, 'w') as f:
				json.dump(saved_urls, f)
			print('done')

		# check downloads
		all_files = [join(path, f) for f in listdir(path) if isfile(join(path, f))]
		all_videos = [v for v in all_files if v.endswith('.mp4')]
		if len(all_videos) == len(saved_urls[playlist_name]): # if target video count matches video count, return
			print('All files were allready downloaded')
			continue
		removed_last = False
		if all_videos: # if at least one video was downloaded, delete last
			for obj in reversed(saved_urls[playlist_name]):
				if removed_last: break
				title = obj['title']
				for f in all_videos:  # if any video matches the title, remove it since it was the last and download could not be complete
					if '78' in title and '78' in f:
						print('hi')
					if title in f:
						remove(f)
						removed_last = True
						print(f"Removed last incomplete download '{title}.mp4'")
						break

		# download videos that weren't already downloaded
		print('Downloading...')
		for obj in tqdm(saved_urls[playlist_name]):
			url = obj['url']
			title = obj['title']
			p = join(path, f'{title}.mp4')
			if not exists(p):
				youtube = YouTube(url)
				video = youtube.streams.get_highest_resolution()
				video.download(path)
			else:
				sleep(.1)
		print('done')



if __name__ == '__main__':
	main()
