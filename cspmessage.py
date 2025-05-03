from flask import Flask, request, Response, redirect, url_for
from collections import defaultdict

app = Flask(__name__)

# Store messages and user names
messages = []
user_names = {}

# Helper function to output XML responses
def outputXML(xmlContent):
    return Response(xmlContent, mimetype="text/xml")

@app.route("/", methods=["GET"])
def root_redirect():
    return redirect(url_for("chatroom"))

@app.route("/chatroom", methods=["GET", "POST"])
def chatroom():
    # Handle message sending when form is submitted (POST request)
    if request.method == "POST":
        message = request.form.get("msg", "")
        if message:
            # Get user's name or default to 'Guest'
            user_name = user_names.get(request.remote_addr, "Guest")
            # Append message to the chat
            messages.append((user_name, message))

    # Display chatroom with message history and input field
    return render_chatroom()

def render_chatroom():
    # Get the last 10 messages
    recent_msgs = messages[-10:]
    
    # Format the chat history to fit better in a limited space (for Cisco IP Phone)
    chat_history = "\n".join([f"{user}: {m}" for user, m in recent_msgs])
    
    # Build the XML response for the chatroom page
    return outputXML(f"""<?xml version="1.0" encoding="UTF-8"?>
<CiscoIPPhoneMenu>
  <Title>CSP Messaging</Title>
  <Prompt>Messages</Prompt>
  <Text>{chat_history}</Text>
  <MenuItem>
    <Name>Send Message</Name>
    <URL>{request.url_root}sendmessage</URL>
  </MenuItem>
  <MenuItem>
    <Name>View All Messages</Name>
    <URL>{request.url_root}viewmessages</URL>
  </MenuItem>
  <MenuItem>
    <Name>Set Your Name</Name>
    <URL>{request.url_root}setname</URL>
  </MenuItem>
</CiscoIPPhoneMenu>""")

@app.route("/sendmessage", methods=["GET"])
def send_message():
    # Display a form for alphanumeric text input
    return outputXML(f"""<?xml version="1.0" encoding="UTF-8"?>
<CiscoIPPhoneInput>
  <Title>Send a Message</Title>
  <Prompt>Enter your message</Prompt>
  <URL>{request.url_root}postmessage</URL>
  <InputItem>
    <DisplayName>Message</DisplayName>
    <QueryStringParam>msg</QueryStringParam>
    <InputFlags>A</InputFlags> <!-- 'A' for alphanumeric input -->
  </InputItem>
</CiscoIPPhoneInput>""")

@app.route("/postmessage", methods=["GET"])
def post_message():
    # Get the message input from the user
    message = request.args.get("msg", "")
    if message:
        # Get user's name or default to 'Guest'
        user_name = user_names.get(request.remote_addr, "Guest")
        # Append the message to the chat history
        messages.append((user_name, message))

    return render_chatroom()

@app.route("/viewmessages", methods=["GET"])
def view_messages():
    # Get all messages
    all_msgs = "\n".join([f"{user}: {m}" for user, m in messages])
    
    # Build XML for viewing all messages
    return outputXML(f"""<?xml version="1.0" encoding="UTF-8"?>
<CiscoIPPhoneText>
  <Title>All Messages</Title>
  <Prompt>Here are all the messages</Prompt>
  <Text>{all_msgs}</Text>
  <MenuItem>
    <Name>Back to CSP Chatroom</Name>
    <URL>{request.url_root}chatroom</URL>
  </MenuItem>
</CiscoIPPhoneText>""")

@app.route("/setname", methods=["GET"])
def set_name():
    # Display a form to set the user's name
    return outputXML(f"""<?xml version="1.0" encoding="UTF-8"?>
<CiscoIPPhoneInput>
  <Title>Set Your Name</Title>
  <Prompt>Enter your name</Prompt>
  <URL>{request.url_root}setnameaction</URL>
  <InputItem>
    <DisplayName>Name</DisplayName>
    <QueryStringParam>name</QueryStringParam>
    <InputFlags>A</InputFlags> <!-- 'A' for alphanumeric input -->
  </InputItem>
</CiscoIPPhoneInput>""")

@app.route("/setnameaction", methods=["GET"])
def set_name_action():
    # Set the user's name and redirect to chatroom
    name = request.args.get("name", "Guest")
    user_names[request.remote_addr] = name
    return redirect(url_for("chatroom"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9999)
