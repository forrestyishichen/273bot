import os
import time
import os.path
import sys
import json
from slackclient import SlackClient

try:
    import apiai
except ImportError:
    sys.path.append(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
    )
    import apiai

# CLIENT_ACCESS_TOKEN = 'bf07033af7d646a5b53a15322981d586'
CLIENT_ACCESS_TOKEN = '91131189cd5c4f91aebf6aebf981af78'
ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN)

BOT_NAME = 'fantasic-bot'
slack_client = SlackClient('xoxb-281807896613-SW5udIHa3odIKa7IjBUyR1dp')
BOT_ID = 'U89PRSCJ1';

AT_BOT = "<@" + BOT_ID + ">"


def get_bot_id():
    api_call = slack_client.api_call("users.list")
    if api_call.get('ok'):
        # retrieve all users so we can find our bot
        users = api_call.get('members')
        for user in users:
            if 'name' in user and user.get('name') == BOT_NAME:
                BOT_ID = user.get('id')
                AT_BOT = "<@" + BOT_ID + ">"
    else:
        print("could not find bot user with the name " + BOT_NAME)

def handle_command(command, channel, user_id):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    # print("command " + command)
    message = ''
    request = ai.text_request()
    request.lang = 'en'  # optional, default value equal 'en'
    request.session_id = user_id
    print(request.session_id)
    request.query = command

    response = request.getresponse().read().decode("utf-8")
    result = json.loads(response)
    if result["status"]["code"] == 200:
        for m in result["result"]["fulfillment"]["messages"]:
            message = m['speech']

    slack_client.api_call("chat.postMessage", channel=channel, text=message, as_user=True)

def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                # print(output['user'])
                # print(output['text'])
                return output['text'].split(AT_BOT)[1].strip().lower(), output['channel'], output['user']
    return None, None, None


if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("bot connected and running!")
        get_bot_id()
        while True:
            command, channel, user_id = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                # print('handle command ' + command)
                handle_command(command, channel, user_id)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
