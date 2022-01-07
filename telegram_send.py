import telebot
from telethon.sync import TelegramClient
from telethon.tl.types import InputPeerUser, InputPeerChannel
from telethon import TelegramClient, sync, events

# get your api_id, api_hash, token 
# from telegram as described above 
api_id = '1373816463' #'1220006940'
api_hash = 'AAHRZYqllHIEC9uGE2cgiVWn_xForz6tIUg' #'AAEJHVszllVGn3IhbH40590M7YKJ9owLVCY'

# your phone number 
phone = '+393494906948'
# creating a telegram session and assigning 
# it to a variable client 
client = TelegramClient('session', api_id)
# connecting and building the session 
client.connect()
# in case of script ran first time it will 
# ask either to input token or otp sent to 
# number or sent or your telegram id  
if not client.is_user_authorized():
    client.send_code_request(phone)
    # signing in the client 
    client.sign_in(phone, input('Enter the code: '))

try:
    # receiver user_id and access_hash, use 
    # my user_id and access_hash for reference 
    receiver = InputPeerUser('user_id', 'user_hash')
    # sending message using telegram client 
    client.send_message(receiver, 'ciao', parse_mode='html')
except Exception as e:
    # there may be many error coming in while like peer 
    # error, wwrong access_hash, flood_error, etc 
    print(e)
# disconnecting the telegram session  
client.disconnect()

