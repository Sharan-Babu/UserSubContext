# UserSubContext

**Aim**: 
A simple technique that uses _'current user message/query'_ to dynamically select only a subset of the current context window for the next turn based on previous user messages.

User messages can tell us a lot about what the conversation was and how it unfolded. And in most conversations, the length of the user's message is much smaller and concise compared to the chatbot's response.

This can be used to select only a subset of the current context for the next user message/query thereby reducing the token consumption.

Also a much better approach than naive rolling window-based trimming of the context window.

**Code** in `subcontext.py` file and **sample output/demo** in `sample_output.txt` file
