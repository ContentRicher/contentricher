import instaloader
from os.path import exists
from pathlib import Path

import os
from dotenv import load_dotenv

# Assuming the .env file is two levels up from the current script
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
load_dotenv(dotenv_path)

username=os.getenv("INSTA_USERNAME")
pw=os.getenv("INSTA_PASSWORD") 
 
def create_sessionfile_dir(username=username):
  ## Save the sessionfile to the following directory. 
  session_directory = "../instaloader/"
  
  ## Create session directory, if it does not exists yet
  Path(session_directory).mkdir(parents=True, exist_ok=True)
  filename = "{}session-{}".format(session_directory, username)
  sessionfile = Path(filename)
  return sessionfile

sessionfile = create_sessionfile_dir(username)

## Get instance
L2 = instaloader.Instaloader(compress_json=False)

## If sessionfile exists, load session, else log in interactively
def load_sessionfile(sessionfile, username=username, pw=pw):
  if exists(sessionfile):
    L2.load_session_from_file(username, sessionfile) 
    return True
  else:
    #L2.interactive_login(username)
    L2.login(username, pw)
    L2.save_session_to_file(sessionfile)
    return True

if __name__ == "__main__":
    load_sessionfile(sessionfile)
    #pass