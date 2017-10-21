import config
import socket
import time
import re

# Connect to Twitch IRC server
s = socket.socket()
s.connect((config.SERVER, config.PORT))
s.send("PASS {}\r\n".format(config.PASSWORD).encode("utf-8"))
s.send("NICK {}\r\n".format(config.NICKNAME).encode("utf-8"))
s.send("JOIN {}\r\n".format(config.CHANNEL).encode("utf-8"))


CHAT_MSG = re.compile(r"^:\w+!\w+@\w+\.tmi\.twitch\.tv PRIVMSG #\w+ :")

def chat(sock, msg):
    """
    Send a chat message to the server.
    Keyword arguments:
    sock -- the socket over which to send the message
    msg -- the mesage to be sent
    """
    sock.send("PRIVMSG {} :{}\r\n".format(config.CHANNEL, msg).encode("utf-8"))
    
def ban(sock, user):
    """
    Ban a user from the current channel.
    Keyword arguments:
    sock -- the socket over which to send the ban command
    user -- the user to be banned
    """
    chat(sock, ".ban {}".format(user))
    print(user + " is now banned.")

def timeout(sock, user, secs = 600):
    """
    Time out a user for a set period of time.
    Keyword arguments:
    sock -- the socket over which to send the timeout command
    user -- the user to be timed out
    secs -- the length of the timeout in seconds (default 600)
    """
    chat(sock, ".timeout {}".format(user, secs))


while True:
    response = s.recv(1024).decode("utf-8")
    
    # Required to stay connected to Twitch IRC server
    if response == "PING :tmi.twitch.tv\r\n":
        s.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
        print("PONG")
    else:
        # Extract chat user and message
        username = re.search(r"\w+", response).group(0)
        message = CHAT_MSG.sub("", response)
        print(username + ": " + message)
        for pattern in config.PATTERN:
            if re.match(pattern, message):
                ban(s, username)
                break
        time.sleep(1 / config.RATE)
