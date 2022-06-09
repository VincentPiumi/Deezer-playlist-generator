from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from datetime import datetime, timedelta
import time
import requests
import json
import platform

class Export:      
    token = ""   
    user_id = "" 
    playlist_id = ""
    playlist_name = "Generated playlist"
    songs = []
    expiration = datetime.now()
    
    def connect(self) :
        if len(self.token) != 0 and datetime.now() < self.expiration :
            return self.token
            
        if platform.system() == 'Windows' :
            ser = Service(r".\drivers\chromedriver.exe")
        elif platform.system() == 'Darwin' :
            ser = Service(r".\drivers\mac-chromedriver")
        else :
            return ""
            
        instance = webdriver.Chrome(service=ser)
        instance.get('https://connect.deezer.com/oauth/auth.php?app_id=542842&redirect_uri=http://example.com&perms=manage_library,delete_library')

        url = instance.current_url
        code_url = "http://example.com/?code="
        while code_url not in url :
            time.sleep(2)
            url = instance.current_url

        _code = url[len(code_url):len(url):]
        req = requests.get(f'https://connect.deezer.com/oauth/access_token.php?app_id=542842&secret=f28ad2b4ca26de2c8c0130f1b4ca7a54&code={_code}&output=json'.format(_code))        
        try:
            access_token = req.json()['access_token']
            expires = req.json()['expires']
            self.expiration = datetime.now() + timedelta(seconds=expires)
        except requests.exceptions.JSONDecodeError :
            return ""
        return access_token
        
    def get_userid(self) :
        token = self.token
        req = requests.get(f'https://api.deezer.com/user/me?access_token={token}'.format(token))
        try:
            self.user_id = req.json()['id']
        except requests.exceptions.JSONDecodeError :
            return False
        return True
     
    def delete_playlist(self) :
        user_id = self.user_id
        token = self.token
        get_playlist = f'https://api.deezer.com/user/2712655982/playlists?output=jsonp&access_token={token}'.format(token)
        req = requests.get(get_playlist)
        format = json.loads(req.text[1:-1])
        for playlist in format['data'] :
            if playlist['title'] == "Generated playlist" :
                self.playlist_id = playlist['id']
                playlist_id = playlist['id']
                del_playlist = f'https://api.deezer.com/playlist/{playlist_id}?output=jsonp&request_method=DELETE&access_token={token}'.format(playlist_id, token)
                req = requests.get(del_playlist)
    
    def create_playlist(self) :
        self.delete_playlist()
        
        user_id = self.user_id
        token = self.token
        title = self.playlist_name
        create_playlist = f'https://api.deezer.com/user/{user_id}/playlists?output=jsonp&request_method=POST&access_token={token}&title={title}&output=jsonp'.format(user_id, token, title)
        req = requests.get(create_playlist)
        
        if req.status_code == 200 :
            format = json.loads(req.text[1:-1])
            self.playlist_id = format['id']
            return True
        return False
   
    def add_songs(self) :
        songs = ','.join(self.songs)
        playlist_id = self.playlist_id
        token = self.token
        add_song = f'https://api.deezer.com/playlist/{playlist_id}/tracks?output=jsonp&request_method=POST&access_token={token}&songs={songs}'.format(playlist_id, token, songs)
        req = requests.get(add_song)
        if req.status_code != 200 :
            return False
        return True

    def export_playlist(self) :
        if self.user_id == "" :
            if not self.get_userid() :
                return False
        if self.create_playlist() :
            return self.add_songs()
        return False
        
    def main_export(self, songs) :
        self.songs = songs
        self.token = self.connect()
        if len(self.token) == 0 :
            return False        
        return self.export_playlist()