# shortener.py
#   Windows tray URL shortener
#   Luke Jones, 2016
# ------

import sys
import requests
import pyperclip
import pytotray
import wwparser
# --------

# Set the configuration file name
CONFIG = wwparser.parse('./resources/shortener.ini')

CON_INFO = CONFIG['server']
API_KEY = CON_INFO['API_KEY']
DOMAIN = CON_INFO['DOMAIN']

# --------
def shortener_api_request(url):
    """
    ----
    Handles the URL shortener API call.
    --
    :: var url (str) - The full-length URL to be shortened
    --
    :: Returns ( status code (int), response (str) ) from request object
    ----
    """
    
    req = 'https://shortener.godaddy.com/v1/?apikey={key}&domain={domain}&url={url}'
    req = req.format(key=API_KEY, domain=DOMAIN, url=url)
    
    # API closed the connection. For GoDaddy's URL shortening API, this means the request failed.
    # For all APIs, this COULD mean that the user isn't connected to the internet or DNS
    # is being DNS.
    try:
        r = requests.get(req)
        return r.status_code, r.text
        
    except requests.exceptions.ConnectionError:
        return 422, ''
    
# -----
def _shorten(handle):
    """
    ----
    Function called when either the shorten option is selected or the tray icon is clicked
    --
    :: var handle (SysTrayIcon object)
    --
    :: Returns None
    ----
    """
    
    # pytotray throws a permissions error when trying to get the URL from the
    # clipboard; it still works, so there's no reason to clutter the console with it.
    try:
        to_shrink = pyperclip.paste()
    except pyperclip.exceptions.PyperclipWindowsException:
        pass
        
    status_code, response = shortener_api_request(to_shrink)

    # Handle request response
    if status_code == 200:
        pyperclip.copy(response)
        sys.stdout.write('Success!\n')
        
    elif status_code == 422:
        if len(to_shrink) < 200:
            sys.stdout.write(':( - Invalid URL \'{}\'\n'.format(to_shrink))
        else:
            sys.stdout.write(':( - Invalid URL')

    else:
        # Avoid flooding the console with a massive amount of text
        if len(to_shrink) < 200:
            sys.stdout.write(':( - Unknown error shortening \'{}\'\n'.format(to_shrink))
        else:
            sys.stdout.write(':( - Unknown error shortening URL\n')
        
# -----
def _run_gui():
    # GUI handler
    # ---
    
    icon = './resources/shortener.ico'  # Path to tray icon
    hover_text = 'WinterWing URL Shortener'  # Label that appears on hover

    # ---
    # Tuple of (label, function) that correspond to menu items.
    # 
    # NOTE:
    #           A quit option is automatically injected by pytotray, as the cleanup
    #           calls are on the win32api handles contained within pytotray. I have
    #           put several hours into tweaking the code, and I highly recommend
    #           not bothering to tweak it further, as it's quirky but mostly works.
    
    menu = ( ('Upload', _shorten), )
    # ---
    
    # Yaaaaay, more cleanup code... fsck the Faildows API
    try:
        tray = pytotray.SysTrayIcon(icon, hover_text, menu)
    except KeyboardInterrupt:
        tray.destroy()


# --------
if __name__ == '__main__':
    _run_gui()

