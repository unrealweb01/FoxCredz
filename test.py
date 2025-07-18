import main
from main import Extract
if __name__=="__main__":
      firefox=Extract(browser="firefox")
      for hostname,username,password in firefox.password():
          print(f"🔒HostName:{hostname}\n👤Username:{username}\n🔑Password:{password}")
