import os
import time
import re
from slackclient import SlackClient

# instantiate Slack client
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
# starterbot's user ID in Slack: value is assigned after the bot starts up
starterbot_id = None

# constants
RTM_READ_DELAY = 1 # 1 second delay between reading from RTM
EXAMPLE_COMMAND = "where:"
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"

#Determines if cmds are dirrected at bot by taking events given from Slack
#Therefore gives message with some text
def parse_bot_commands(slack_events):
	"""Parses a list of events coming from RTM to find bot commands
	   If a bot cmd is found, returns a tuple of cmd and chanel. Otherwise, None
	   to both.
	"""
	for event in slack_events:
		if event["type"] == "message" and not "subtype" in event:
			user_id, message = parse_direct_mention(event["text"])
			if user_id == starterbot_id:
				return message, event["channel"]
	return None, None

#Checks if the message starts with a mention of bot. Comapre the user id to stored earlier for starter bot	
def parse_direct_mention(message_text):
	"""
		Finds a direct mention in message text and returns the user id which was mentioned.
		If no direct mention, retun None
	"""
	matches = re.search(MENTION_REGEX,message_text)
	 # the first group contains the username, the second group contains the remaining message
	return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

def handle_command(command, channel):
	"""executes bot command if the command is recognized"""
	#Defualt response is help text for the user
	default_response = "Not sure what you mean. Try *{}*.".format(EXAMPLE_COMMAND)

	#Finds and executes given cmd. Filling response
	response = None
	#This is where we add more cmds
	if command.startswith(EXAMPLE_COMMAND):
		response = "They're right over there."
	if command.startswith("where:Microwaves"):
		response = "Just rub your hands against the container really fast"

	#Sends response back to channel
	slack_client.api_call(
		"chat.postMessage",
		channel=channel,
		text=response or default_response
		)

if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        print("Starter Bot connected and running!")
        # Read bot's user ID by calling Web API method `auth.test`
        starterbot_id = slack_client.api_call("auth.test")["user_id"]
        while True:
            command, channel = parse_bot_commands(slack_client.rtm_read())
            if command:
                handle_command(command, channel)
            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")