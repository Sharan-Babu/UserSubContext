# Select only req context for the conversation (SubContext)
# DESC: A simple technique that uses user message to dynamically select only a subset of the current context window for the next turn based on previous user messages
# User messages can tell us a lot about what the conversation was and how it unfolded. And in most conversations, the length of
# The user's message is much smaller and concise compared to the chatbot's response
# This can be used to select only a subset of the current context for the next user message/query thereby reducing the token consumption
# Also a much better approach than naive rolling window based trimming of the context window

# Necessary Libraries
import openai
from openai import OpenAI
from dotenv import load_dotenv
import os
import ast

load_dotenv()
#openai.api_key = '###### your-api-key-here #####'
openai.api_key = os.getenv("OPENAI_API_KEY")

# Connect LLM API
client = OpenAI()
system_message = "You are a helpful chat assistant"
conversation_history = [{"role": "system", "content": system_message}]
user_msgs_array = []

## SUBCONTEXT TECHNIQUE
def subcontext(msg, num_user_msgs=30):

	global user_msgs_array
	conversation_history.append({"role":"user", "content":msg})
	user_msgs_array.append(msg)

	# To not run subcontext if the conversation just begun
	if len(conversation_history) < 5:
		return conversation_history

	# Core Logic
	user_msgs_string = []
	start = 1
	for x in range(len(user_msgs_array)):
		user_msgs_string.append(f"{start}. {user_msgs_array[x]}")
		start += 2

	print(f"Debug:{user_msgs_string}")
	user_msgs_string = "\n".join(user_msgs_string[:-1])

	subcontext_prompt = [{"role": "system", "content": f"Given below a list of user msgs and current user query from a conversation with a chatbot. The user messages are enough to let us know what the chatbot must have responded with. Select the previous messages whose context is required for answering current user query. You can select multiple. Return corresponding 'list of indices' (ex: [0,3,7]).\n\nUser Msg List:\n{user_msgs_string}\n\nUser query:\n{msg} "}]
	result = chatgpt(subcontext_prompt)

	# Parse Array
	list_obj = ast.literal_eval(result)
	print(f"\n!!!{user_msgs_string}, {msg}\nchatgpt result:{result}\nParsed array: {list_obj}\n\n")
	subcontext_array =[conversation_history[0]]
	for y in list_obj:
		print(f"Y is {y}---{type(y)}, {list_obj}")
		subcontext_array.append(conversation_history[y])
		subcontext_array.append(conversation_history[y+1])
	
	subcontext_array.append(conversation_history[-1])
	print(f"\n\nLook at array:{subcontext_array}\n\n")


	# Trim subcontext window if specified length exceeded
	if len(user_msgs_array) > num_user_msgs:
		print("Trimming User messages")

		# LLM call to trim exisitng user messages array
		trim_prompt = [{"role": "system", "content": f"Given below a list of user msgs from a conversation with a chatbot. We want to trim it so have a look at them, determine which ones are worth retaining based on what the conversation is progressing towards and return only corresponding 'list of indices' (ex: [0,2,3]).\n\nUser Msg List:\n{user_msgs_string}"}]
		trim_result = chatgpt(trim_prompt)
		trim_list = ast.literal_eval(trim_result)
		new_list = []
		new_convo = [conversation_history[0]]
		for z in trim_list:
			new_list.append(user_msgs_array[z])
			new_convo.append(conversation_history[z])
			new_convo.append(conversation_history[z+1])
		user_msgs_array = new_list	
		conversation_history = new_convo
	
	# return array
	return subcontext_array


## LLM CALL 
def chatgpt(messages_array):
	response = client.chat.completions.create(
	  model="gpt-4-turbo-preview",
	  messages=messages_array,
	  temperature=0,
	  max_tokens=750,
	  top_p=1,
	  frequency_penalty=0,
	  presence_penalty=0
	)

	assistant_reply = response.choices[0].message.content
	return assistant_reply

print("Try out Subcontext technique (Enter 'quit' to exit):")

## TERMINAL -- INTERACTIVE
while True:
	user_msg = input("\n\nEnter your msg: ")
	if user_msg == 'quit':
		break
	reply = chatgpt(subcontext(user_msg))
	conversation_history.append({"role":"assistant", "content":reply})
	print(reply)
print("-- Program has ended --")
