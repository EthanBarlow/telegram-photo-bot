import json 
import requests
import time
import urllib
import picamera
import os

TOKEN = "<your telegram bot token here>"
URL = "https://api.telegram.org/bot{}/".format(TOKEN)
HELPMESSAGE = "The following commands and functions are currently available:\n/photo takes a picture with a raspberry pi camera and sends it back to you.\n/about displays information about the idea behind this bot and the creator's contact information if you found any bugs.\n/help displays this message.\n/video5 will record a 5 second video and send that to the user.\n/video15 will record a 15 second video and send that to the user.\n/video30 will record a 30 second video and send that to the user."
ABOUTMESSAGE = "piBot was created by Ethan Barlow, a student at Bloomsburg University. The idea behind the project was to send a command to a telegram bot, have a raspberry pi take a picture and then send that picture back to the user. Any unrecognizable commands are merely echoed back to the sender. If you have any issues or suggestions, please contact the developer by finding him in the software lab of Ben Franklin Hall."

#goes to the url that is passed in and returns the content
def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content

#uses the get_url function to get the content, then returns the json part of the content
def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js

#uses the get_json_from_url function to get the json information and returns it, but also waits 10000000 seconds before checking for a new update
def get_updates(offset=None):
    url = URL + "getUpdates?timeout=10000000"
    if offset:
        url+="&offset={}".format(offset)
    js = get_json_from_url(url)
    return js

#uses an array to hold all the updates that have been made, 
#and returns the most recent update so that the same operation is not performed multiple times.
def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)

#takes in the "updates" parameter and uses it to get the last update
#then "updates" is used to get the text from the last message
#additionally, "updates" is used to get the chat_id from the last message
#finally "text" and "chat_id" are returned
def get_last_chat_id_and_text(updates):
    num_updates = len(updates["result"])
    last_update = num_updates - 1
    text = updates["result"][last_update]["message"]["text"]
    chat_id = updates["result"][last_update]["message"]["chat"]["id"]
    return (text, chat_id)

#send_message takes in the "text" and "chat_id" parameters
#text is parsed so that no formatting is messed up and then reassigned to itself
#the url is made up with the global URL and the sendMessage function from Telegram's api, and the "text" and "chat_id" are used in the url
def send_message(text, chat_id):
    text=urllib.parse.quote_plus(text)
    url = URL + "sendMessage?text={}&chat_id={}".format(text, chat_id)
    get_url(url)

#send_info is used to process the /help and /about commands from a user
#the process used here is the same as in the send_message function above,
#except "in_text" will either refer to the global ABOUTMESSAGE or HELPMESSAGE
def send_info(in_text,chat_id):
    text= in_text
    url = URL + "sendMessage?text={}&chat_id={}".format(text, chat_id)
    get_url(url)

#send_image takes in a file_path and a chat_id
#the file_path is a path to a picture that will be sent to a user
#then the file_path file is opened, the url is composed, and an HTTP post request is made using the url
def send_image(file_path, chat_id):
    files = {'photo': open(file_path, 'rb')}
    url = URL+"sendPhoto?chat_id={}".format(chat_id)
    r= requests.post(url, files=files)
    print(r.status_code, r.reason, r.content)
    
#send_video takes in a file_path and a chat_id
#the file_path is a path to a video that will be sent to a user
#then the file_path file is opened, the url is composed, and an HTTP post request is made using the url    
def send_video(file_path, chat_id):
    files = {'video': open(file_path, 'rb')}
    url = URL+"sendVideo?chat_id={}".format(chat_id)
    r= requests.post(url, files=files)
    print(r.status_code, r.reason, r.content)

#echo_all takes in the "updates" parameter and cycles through all the updates found from the HTTP pull request
#the function tries to get the text and chat_id from the "update" array
#then the message text, "text" is compared to a list of available commands
#if there is a match, the respective functions are called    
#otherwise, the message is simply repeated back to the user
def echo_all(updates):
    for update in updates["result"]:
        try:
            text=update["message"]["text"]
            chat = update["message"]["chat"]["id"]
            #print(text) --- testing purposes
            if(text=="/photo"):
                #print("Send picture here")
                img_path=take_picture()
                #print(img_path)
                send_image(img_path,chat)
            elif(text=="/help"):
                #print("help message")
                send_info(HELPMESSAGE,chat)
            elif(text=="/about"):
                #print("about message")
                send_info(ABOUTMESSAGE,chat)
            elif(text=="/video5"):
                print("Record 5 second video")
                vid_path=take_video(5)
                send_video(vid_path, chat)
                print(vid_path)
            elif(text=="/video15"):
                print("record 15 second video")
                vid_path=take_video(15)
                send_video(vid_path, chat)
            elif(text=="/video30"):
                print("record 30 second video")
                vid_path=take_video(30)
                send_video(vid_path, chat)
            else:
                send_message(text, chat)
        except Exception as e:
            print (e)
			
#take_picture utilizes the camera connected to the raspberry pi that this script runs on
#the path is set to the current working directory/wherever this script is saved		
#the picture is then taken and stored as "<your specified directory>/image.jpg"
#this path is then returned so that the path can be used to send a picture
def take_picture():
	with picamera.PiCamera() as camera:
		path="<your specified directory>"
		#starts up the camera
		camera.start_preview()
		#waits 3 seconds so that the camera can adjust for lighting and focus
		time.sleep(3)
		camera.capture(path+"/image.jpg")
		camera.stop_preview()
		camera.close()
		print (path)
		return (path+"/image.jpg")
		
#take_video utilizes the camera connected to the raspberry pi that this script runs on
#the "length" parameter determines how long a recording will last - the final video may be off by a second or two 
#the path is set to the current working directory/wherever this script is saved		
#the video is then taken and stored as "<your specified directory>/image.jpg"
#this path is then returned so that the path can be used to send a video		
def take_video(length):
     with picamera.PiCamera() as camera:
         path="<your specified directory>"
         #the raspberry pi camera natively records in raw h264 format, but the telegram api only works with mp4 files - hence the next several lines
         og_path=path+"/video.h264"
         new_path=path+"/video.mp4"
         #delete the old files and record a new video so that there is no issue with appending instead of overwriting
         os.remove(og_path)
         os.remove(new_path)
         camera.start_recording(og_path)
         camera.wait_recording(length)
         camera.stop_recording()
         camera.close()
         #the next line acts as if it starts up a linux terminal instance and then uses MP4Box to convert the file type
         #MP4Box is not natively installed as a part of raspbian, so first run the following command in your terminal: sudo apt-get install gpac 
         os.system('MP4Box -add /home/pi/Projects/telegramProjs/video.h264 /home/pi/Projects/telegramProjs/video.mp4')
         return (new_path)

#the main function runs a while True loop so that the function/python script will run indefinitely - or until it is interupted in the terminal by ctrl+C
def main():
	last_update_id = None
	while True:
		updates=get_updates(last_update_id)
		if len(updates["result"])>0:
			last_update_id=get_last_update_id(updates)+1
			echo_all(updates)
		time.sleep(0.5)
		print("getting updates")
		
		
if __name__ == '__main__':
	main()

#end file