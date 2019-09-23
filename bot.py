# bot.py
import socket
import time
import cfg
import re
import random

# define useful helper functions

def chat(sock, msg):
    """
    Send a chat message to the server.
    Keyword arguments:
    sock -- the socket over which to send the message
    msg  -- the message to be sent
    """
    message = "PRIVMSG {} :{}\r\n".format(cfg.CHAN, msg)
    #print("Sending: "+message)
    sock.send(message.encode("utf-8"))

def ban(sock, user):
    """
    Ban a user from the current channel.
    Keyword arguments:
    sock -- the socket over which to send the ban command
    user -- the user to be banned
    """
    chat(sock, "/ban {}".format(user))

def timeout(sock, user, secs=1, message="Please only post soapstone-friendly messages. You can find a generator at http://zoomboingding.com/funtime/soapstonegen.html "):
    """
    Time out a user for a set period of time.
    Keyword arguments:
    sock -- the socket over which to send the timeout command
    user -- the user to be timed out
    secs -- the length of the timeout in seconds (default 1)
    """
    chat(sock, "/timeout {} {} {}".format(user, secs, message))
    
def whisper(sock, user, msg):
    """
    Whisper a message to a specific user
    Keyword arguments:
    sock -- the socket over which to send the whisper command
    user -- the user to send the whisper to
    msg -- the message to whisper to the user
    """
    chat(sock, "/w {} {}".format(user, msg))
    
def lautrec(sock):
    lMessage = random.choice(cfg.LAUTREC)
    #print("I should be sending "+lMessage+" now")
    chat(sock, lMessage)
    
def strip_punctuation(s):
    return ''.join(c for c in s if c not in cfg.PUNCTUATION)
    
def matchesSoapstone(message):
    for conj in cfg.CONJUNCTIONS:
        if conj in message:
            return lineMatches(message.split(conj,1)[0].strip()) and lineMatches(message.split(conj,1)[1].strip())
    
    return lineMatches(message) 
    
def lineMatches(message):
    for template in cfg.TEMPLATES:
        templateBegin = template.split("****",1)[0].strip()
        templateEnd = template.split("****",1)[1].strip()
        if(message.startswith(templateBegin) and message.endswith(templateEnd)): 
            #matches a template, or we've reached the wildcard
            if(len(templateEnd) is not 0):
                keyword = message[len(templateBegin):-1*len(templateEnd)].strip()
            else:
                keyword = message[len(templateBegin):].strip()
            if(keyword in cfg.NOUNS):
                return True
    return False

# network functions go here
s = socket.socket()
s.connect((cfg.HOST, cfg.PORT))
s.send("PASS {}\r\n".format(cfg.PASS).encode("utf-8"))
s.send("NICK {}\r\n".format(cfg.NICK).encode("utf-8"))
s.send("JOIN {}\r\n".format(cfg.CHAN).encode("utf-8"))

CHAT_MSG=re.compile(r"^:\w+!\w+@\w+\.tmi\.twitch\.tv PRIVMSG #\w+ :")

#chat(s, "Hello!")
loop = 0

while True:
    response = s.recv(1024).decode("utf-8")
    if response == "PING :tmi.twitch.tv\r\n":
        s.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
    else:
        username = re.search(r"\w+", response).group(0) # return the entire match
        message = CHAT_MSG.sub("", response).strip()
        
        if(message == "!lautrec"):
             lautrec(s)
        else:
            message = strip_punctuation(message)
            message = message.lower();
          
            print(username + ": " + message)
            
            if(message == "try tongue but hole"):
                timeout(s, username, 600, "That one isn't even valid. 'But' isn't a conjunction in the tool.");
            else if not matchesSoapstone(message):
                timeout(s, username)
                #print(message + " doesn't match soapstone")
            #else:
                #print(message + " matches soapstone")
                
    if(loop % cfg.NUM_MESSAGES == 0):
        lautrec(s)
    loop = loop + 1