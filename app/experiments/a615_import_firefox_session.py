from argparse import ArgumentParser
from glob import glob
from os.path import expanduser, exists
from platform import system
from sqlite3 import OperationalError, connect

import os
from dotenv import load_dotenv

#load_dotenv()
# Assuming the .env file is one level up from the current script
#dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
load_dotenv(dotenv_path)

username=os.getenv("INSTA_USERNAME")

try:
    from instaloader import ConnectionException, Instaloader
except ModuleNotFoundError:
    raise SystemExit("Instaloader not found.\n  pip install [--user] instaloader")


def get_cookiefile():
    default_cookiefile = {
        "Windows": "~/AppData/Roaming/Mozilla/Firefox/Profiles/*/cookies.sqlite",
        "Darwin": "~/Library/Application Support/Firefox/Profiles/*/cookies.sqlite",
    }.get(system(), "~/.mozilla/firefox/*/cookies.sqlite")
    cookiefiles = glob(expanduser(default_cookiefile))
    if not cookiefiles:
        raise SystemExit("No Firefox cookies.sqlite file found. Use -c COOKIEFILE.")
    return cookiefiles[0]


def delete_file(sessionfile_path):
    if exists(sessionfile_path):
        os.remove(sessionfile_path)


def import_session(cookiefile, sessionfile):
    print("Using cookies from {}.".format(cookiefile))
    conn = connect(f"file:{cookiefile}?immutable=1", uri=True)
    try:
        cookie_data = conn.execute(
            "SELECT name, value FROM moz_cookies WHERE baseDomain='instagram.com'"
        )
    except OperationalError:
        cookie_data = conn.execute(
            "SELECT name, value FROM moz_cookies WHERE host LIKE '%instagram.com'"
        )
    instaloader = Instaloader(max_connection_attempts=1)
    instaloader.context._session.cookies.update(cookie_data)
    username = instaloader.test_login()
    if not username:
        raise SystemExit("Not logged in. Are you logged in successfully in Firefox?")
    print("Imported session cookie for {}.".format(username))
    instaloader.context.username = username
    instaloader.save_session_to_file(sessionfile)

def import_session_from_firefox(cookiefile=None, sessionfile=None, username=None):

    session_directory = "../instaloader/"
    username = username 
    filename = "{}session-{}".format(session_directory, username)
    #sessionfile=f"../instaloader/{filename}"
    sessionfile=f"{filename}"

    # If no arguments are provided, attempt to parse them from the command line
    if cookiefile is None and sessionfile is None:
        p = ArgumentParser()
        p.add_argument("-c", "--cookiefile")
        p.add_argument("-f", "--sessionfile")
        args = p.parse_args()
        cookiefile = args.cookiefile
        sessionfile = args.sessionfile

    # Use provided arguments or defaults from command line
    cookiefile_path = cookiefile or get_cookiefile()
    sessionfile_path = sessionfile  # Assumes you have a default or mandatory requirement for sessionfile

    try:
        print('deleting file: '+sessionfile_path)
        delete_file(sessionfile_path)
        print('deleted file')
        #import_session(args.cookiefile or get_cookiefile(), args.sessionfile)
        import_session(cookiefile_path, sessionfile_path)
        return True
    except (ConnectionException, OperationalError) as e:
        raise SystemExit("Cookie import failed: {}".format(e))
        #return False

if __name__ == "__main__":

    session_directory = "../instaloader/"
    username = username#'email@email.com'
    filename = "{}session-{}".format(session_directory, username)
    import_session_from_firefox(cookiefile=None, sessionfile=f"../instaloader/{filename}", username=username)
