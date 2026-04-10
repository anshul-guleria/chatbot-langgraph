import streamlit as st
from chatbot_backend import chatbot, retrieve_all_threads
from langchain_core.messages import HumanMessage
import uuid

#utility function
def generate_thread_id():
    return uuid.uuid4()

def reset_chat():
    thread_id=generate_thread_id()
    st.session_state['thread_id']=thread_id
    add_thread(st.session_state['thread_id'])
    st.session_state['message_history']=[]

def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)

def load_conversation(thread_id):
    # print()
    return chatbot.get_state(config={'configurable':{'thread_id': thread_id}}).values.get('messages',[])

# message_history = []

# sqlite database


#session state
if 'message_history' not in st.session_state:
    st.session_state['message_history']=[]

if 'thread_id' not in st.session_state:
    st.session_state['thread_id']=generate_thread_id()

if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads']=retrieve_all_threads()

add_thread(st.session_state['thread_id'])

# CONFIG={'configurable':{'thread_id': st.session_state['thread_id']}}
CONFIG={
    'configurable':{'thread_id': st.session_state['thread_id']},
    'metadata': {
        'thread_id':st.session_state['thread_id']
    },
    'run_name': 'chat_turn'
}

# Sidebar UI
st.sidebar.title("LangGraph Chatbot")

if st.sidebar.button("New Chat"):
    reset_chat()

st.sidebar.header("My conversations")

for thread_id in st.session_state['chat_threads']:
    if st.sidebar.button(str(thread_id)):

        st.session_state['thread_id']=thread_id

        messages=load_conversation(thread_id=thread_id)

        temp_messages=[]

        if messages:
            for message in messages:
                if isinstance(message, HumanMessage):
                    role='user'
                else:
                    role='assistant'
                
                temp_messages.append({'role':role, 'content': message.content})

        st.session_state['message_history']=temp_messages


    

#loading the conversation historu
for messages in st.session_state['message_history']:
    with st.chat_message(messages['role']):
        st.text(messages['content'])

user_input=st.chat_input("Type here...")

if user_input:

    #first add the user messsage to message history
    st.session_state['message_history'].append({
        'role': 'user',
        'content': user_input
    })
    with st.chat_message('user'):
        st.text(user_input)
    
    with st.chat_message('assistant'):
        stream=chatbot.stream(
            {"messages": [HumanMessage(content=user_input)]}, 
            config=CONFIG,
            stream_mode='messages')
        
        ai_message=st.write_stream(message_chunk.content for message_chunk, metadata in stream)

        st.session_state['message_history'].append({
            'role': 'assistant',
            'content': ai_message
        })
    