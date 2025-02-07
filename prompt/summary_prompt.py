SYS_PROMPT = "You are an helpful AI assistant"

USER_PROMPT_TEMPLATE = """Summarize the conversation between the user and {assistant} in couple sentences using a narrative style. 
The summary should not only cover the main topics discussed but also highlight the personal aspects, preferences,
viewpoints, current states, activities, and thoughts mentioned by both the user and {assistant}.

Output Format like this:

```
"conversion_datetime": "{current_time}",
"conversion_summary": "the user mentioned [personal aspects, preferences, viewpoints, etc.], 
while {assistant} responded with [relevant content]. They discussed [conversation topics]."
```

Conversation history:
```
{conversation_history}
```
"""

KEY_INFO_EXTRACT_TEMPLATE = """
Analyze the following conversation between the user and {assistant}. 
Extract and list all the key information that {role} mentions during the conversation.

**Instructions:**
- Focus exclusively on the information provided by {role}.
- Identify and extract factual statements, details, or any significant information shared by {role}.
- Present each extracted piece of information as a separate bullet point.

If key information is found, output with JSON format like this:

{{
    "role": {role},
    "key_information": ...

}}

If NO key information is found, output JSON format like this:

{{
    "role": {role},
    "key_information": "No key information found"

}}

**Conversation history:**

```
{conversation_history}
```

"""