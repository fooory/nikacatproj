import streamlit as st
from dotenv import load_dotenv
import os
import time
from openai import OpenAI
from helpers import tools, get_breed_code, get_cat_image_url, get_outputs_for_tool_call
import json

#load environment variables, API keys
load_dotenv() 

#initialise openai client
client = OpenAI()

assistantid = os.environ.get("assistant_id")

st.title("An Assistant for Cat Lovers!")

#initialise chat history to make for a scrollable interactive chat window
if "messages" not in st.session_state:
    st.session_state.messages = []

#display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Ask me all about cats. What do you wanna know?"):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        res_box = st.empty() #make a container to continuously update the stream
        report = [] #holder for openai stream to stream into streamlit
        stream = client.beta.threads.create_and_run(
            assistant_id = assistantid,
            thread = { #list of messages to start the thread with#
                "messages": [
                     {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
                ]
            },
            tools = tools, #function under helpers.py
            stream = True
        )

        

        for event in stream:
            if event.event == "thread.created": #as per API ref, id will be thread_id for first stream event
                thread_id = event.data.id
                print(thread_id)
            if event.event == "thread.message.delta": ##check job is outputting text
                for content in event.data.delta.content:
                    if content.type == 'text':
                        #print value field from text deltas
                        report.append(content.text.value)
                        result = "".join(report).strip()
                        res_box.write(result) #'stream' into the container
            
            if event.event == "thread.run.requires_action":
         
                testrun = event.data #this is a run object

                #on requires action, id will be run id as per API ref
                run_id = event.data.id
                print(run_id)

                
                #Get the tool calls from the initial run as input into get_outputs_for_tool_call
                tool_calls = testrun.required_action.submit_tool_outputs.tool_calls
                tool_outputs = map(get_outputs_for_tool_call, tool_calls) #map if more than one function call
                tool_outputs = list(tool_outputs) #convert into list for appropriate formatting into submit_tool_outputs
                print(tool_outputs)

                #run OpenAI API call for the second time with tool outputs 
                run = client.beta.threads.runs.submit_tool_outputs( 
                    thread_id = thread_id, #from first event stream
                    run_id = run_id, #from last event stream
                    tool_outputs = tool_outputs
                )
                
                #allow time to process request
                time.sleep(3) 

                #check request
                run = client.beta.threads.runs.retrieve( 
                    thread_id = thread_id,
                    run_id = run_id
                )
                
                #output into a message to get the relevant value
                functionmessage = client.beta.threads.messages.list(
                    thread_id = thread_id
                )

                #assign output to result
                print(functionmessage.data[0].content[0].text.value)
                result = functionmessage.data[0].content[0].text.value
                res_box.write(result)


        #append to streamlit session state to update chat 
        st.session_state.messages.append({"role": "assistant", "content": result})
        
            
      