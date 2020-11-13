# Apollo-google-drive-music-player
This application lets the user play music files which are stored on their google drive as well as locally on the computer.
<em> currently this application supports mp3, OGG, and WAV files. </em> <br>
Apollo can also be used as a standalone music player.
<br>
<br>
## SET UP INSTRUCTIONS
### Prerequisites
Make sure you have python 2.7.x or above installed on your machine. <br>
<br>
### Adding songs to google drive
create a folder named 'apollo' in the root directory of your google drive. <br>
Inside the 'apollo' folder, create a folder called 'music' and add your music files in this folder.
<br>
### Setting up google drive API and getting credentials.json
1. visit https://console.cloud.google.com and sign in with your google account. <br>
2. create a new project named 'apollo' by going to the google cloud resource manager. (https://console.cloud.google.com/cloud-resource-manager) <br>
3. Enable the google drive API by expanding the navigation menu > APIs & services > Library. Search for the google drive API and then enable it. (https://developers.google.com/drive/api/v3/enable-drive-api) <br>
4. Expand the navigation menu > APIs & services > Credentials. <br>
5. Click on 'Create Credentials' and choose 'Service account'.
6. Name the service account anything and choose 'owner' as the role of the service account. Visit https://cloud.google.com/iam/docs/creating-managing-service-accounts for more information on creating and managing service accounts.
7. Download the private key in JSON format and save it as 'credentials.json' inside data > sensitive folder of wherever you downloaded this repository. <br>
8. open the 'credentials.json' file in any text editor and locate the client email address under 'client_email'. It should be something like 'sample@project.iam.gserviceaccount.com'. <br>
9. Copy this email address and share the apollo folder on your google drive with this email address.


### Installation
Install all the dependencies using the 'requirements.txt' file inside a virtual environment.
```bash
pip install -r requirements.txt
```
Compile the 'main.py' file.
```bash
python main.py
```
If everything was set up correctly your application should now be working.

### Adding songs to the library
You can add your local songs to the data > local folder of the app manually or from inside the app by clicking file > Add Songs To Library. <br>
<br>
<strong><em> Your local songs will be displayed under the 'library' tab and songs stored on the google drive will appear under the 'online' tab. </em></strong> 
<br>

### Screenshots
![screenshot_one](https://user-images.githubusercontent.com/58216025/99058351-1bc9ea00-25c3-11eb-9761-355b9c5d7164.JPG)
<br>
<br>
![screenshot_two](https://user-images.githubusercontent.com/58216025/99058395-2b493300-25c3-11eb-9e98-d190660a7b58.JPG)
<br>
<br>
![screenshot_three](https://user-images.githubusercontent.com/58216025/99058430-37cd8b80-25c3-11eb-8e1b-41dee128f90f.JPG)
<br>
<br>
![screenshot_four](https://user-images.githubusercontent.com/58216025/99058461-42882080-25c3-11eb-87bc-3c84e838abd9.JPG)
<br>
<br>
<br>
<em> App Icon made by <a href="https://www.flaticon.com/authors/iconixar" title="iconixar">iconixar</a> from <a href="https://www.flaticon.com/" title="Flaticon"> www.flaticon.com</a> </em>
<br>
<em> Royalty free sample music included with the app downloaded from <a href="https://www.bensound.com/royalty-free-music/" title="bensound">www.bensound.com</a></em>
