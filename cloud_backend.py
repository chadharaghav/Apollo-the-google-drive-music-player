from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from googleapiclient.http import MediaIoBaseDownload

import io
import os
import shutil


cloudSongList = []     # THIS IS A LIST WHICH STORES THE NAME OF THE SONGS
cloudList = {}        # THIS IS A DICT WHICH STORES KEY(NAME OF SONG) AND VALUE(FILE ID ON THE CLOUD)


SERVICE_ACCOUNT_FILE = 'data/sensitive/credentials.json'
SCOPES = ['https://www.googleapis.com/auth/drive']

try:
	credentials = service_account.Credentials.from_service_account_file(
		        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
except:
	print("credentials.json not found")

def credentialsFound():
	if os.path.isfile(SERVICE_ACCOUNT_FILE):
		return True
	else:
		return False


def updateCloudList():
	from apiclient.discovery import build

	service = build('drive', 'v3', credentials=credentials)

	# Call the Drive v3 API
	results = service.files().list(
	    pageSize=20, fields="nextPageToken, files(id, name)").execute()
	items = results.get('files', [])

	if not items:
	    print('No files found.')
	else:
	    for item in items:
	    	cloudList[item['name']] = item['id']
	    	cloudSongList.append(item['name'])

	cloudSongList.pop(0)
	cloudSongList.pop(0)
	del cloudList['apollo']
	del cloudList['music']




def downloadFile(file_id, file_name):
	service = build('drive', 'v3', credentials=credentials)
	request = service.files().get_media(fileId=file_id)
	fh = io.BytesIO()
	downloader = MediaIoBaseDownload(fh, request)
	done = False
	while done is False:
		status, done = downloader.next_chunk()

	# SAVING THE STREAMED FILE FROM DRIVE
	SAVE_PATH = f'data/online/{file_name}'

	fh.seek(0)
	with open(SAVE_PATH, 'wb') as f:
		shutil.copyfileobj(fh, f)

	return True
