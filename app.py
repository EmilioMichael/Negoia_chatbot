
from openai import OpenAI
import streamlit as st
import os
from utils import *

with st.sidebar:
    os.environ["OPENAI_API_KEY"] = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")
    "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"
    # "[View the source code](https://github.com/streamlit/llm-examples/blob/main/Chatbot.py)"
    # "[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/streamlit/llm-examples?quickstart=1)"


st.title("Negotiation Practice AI Partner")

with st.expander("About me"):
    st.write("I am your negotiaton bot powered by AI. You need to tell me a little about your negotiation case first.\
     \n - If you want to ask for suggestions for your previous response, then pleaes type **SUGGESTIONS**.\
     \n - If you want to end the simulation, pleaes type **END**.\
     \n - If you want to restart the negotiation, please type **RESTART**.\
     \n - If you want to try a new scenario, please type **NEW SCENARIO**。\
     \n The conversation history will be deleted when the session get disconnected. If you want to save the conversation history, please click 'Download CSV' button.")

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

if 'clicked' not in st.session_state:
    st.session_state.clicked = False

def click_button():
    st.session_state.clicked = True

### TBD: add a button for the user to ask for suggestions.
# only refine the user's previous response based on the the negotiation skills they want to practice.
# st.button('suggestions', on_click=click_button)

prompt = st.chat_input("type here...")

### step_1: ask a sequence of questions to build the negotiation scenario info and the tactics the user wants to pratice with.
### step_2: inform the user that the simulation is about to start
### step_3: form prompts to instruct how chatgpt should response to the user's messages
### step_4: add an endding point or ending cue.



### collect negotiation scenario information from the user
preset_questions = ['1. What is the negotiation sceneario?',
                    '2. What role do you want me to play?',
                    '3. What negotiaton skills do you want to pratice?',
                    '4. How do you expect me to play this role?']

if 'negotiation_info' not in st.session_state:
   st.session_state['negotiation_info'] = []

# Initialize session state
if 'simulation_start' not in st.session_state:
   st.session_state['simulation_start'] = False

if 'index_Q_completed' not in st.session_state:
   st.session_state['index_Q_completed'] = 0

if 'index_Q_shown' not in st.session_state:
   st.session_state['index_Q_shown'] = 1

if "messages" not in st.session_state:
    # greeting from the bot
    st.session_state.messages = []
    st.session_state.messages.append({"role": "assistant", "content": 'Hello, I am Negoia, your negotiation practice partner. Please answer these the following questions first.'})
    st.session_state.messages.append({"role": "assistant", "content": preset_questions[st.session_state['index_Q_completed']]})

if 'negotiation' not in st.session_state:
    st.session_state.negotiation = []

if 'system_instruction' not in st.session_state:
    st.session_state['system_instruction'] = ''

if 'system_instruction_suggestion' not in st.session_state:
    st.session_state['system_instruction_suggestion'] = ''

if 'practice_skill_global_variable' not in st.session_state:
    st.session_state['practice_skill_global_variable'] = ''


### display the questions in sequence
if st.session_state['simulation_start'] == False:
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state['negotiation_info'].append(prompt)
        st.session_state['index_Q_completed'] += 1

        # display the next question
        if st.session_state['index_Q_completed'] < 4:
            st.session_state.messages.append({"role": "assistant", "content": preset_questions[st.session_state['index_Q_completed']]})
            st.session_state['index_Q_shown'] += 1

        else:
            ## find relevant contexts in the pinecone negotiation knowledge base
            negotiation_skill_context = find_match('what are these skills:' + st.session_state['negotiation_info'][2] + '?')
            difficult_tactics_context = find_match('what are these difficult conversation skills:' + st.session_state['negotiation_info'][3] + '?')
            role_intention = get_negotiation_intention(client, st.session_state['negotiation_info'][0], st.session_state['negotiation_info'][1])
            role_batna = get_negotiation_batna(client, st.session_state['negotiation_info'][0], st.session_state['negotiation_info'][1])
            practice_skills = get_negotiation_practice_skill(client, st.session_state['negotiation_info'][2]).replace("\\r\\n", "")
            st.session_state['practice_skill_global_variable'] = practice_skills
            # st.session_state.messages.append({"role": "assistant", "content": "The goal of Negoia in this negotiation is: " + role_intention})
            # st.session_state.messages.append({"role": "assistant", "content": "The BATNA of Negoia in this negotiation is: " + role_batna})
            # st.session_state.messages.append({"role": "assistant", "content": "The key tactics the user want to pratice is: " + practice_skills})


            st.session_state['system_instruction'] = "\
                                  The user will have a simulated negotiation face-to-face conversation with you and you need to response like you are having a real oral conversation with the user. Your feeling can be hurted and you can be angry. Your words should reflect your emotion and mood. \
                                  Here is the user's negotiation case: '{}'. \
                                  You will play the role of '{}' in this case and should talk in the manner as {}. \
                                  The intention of your role in this negotiation is: {}. You will try your best to get the goal and you shouldn't easily yield to the user. \
                                  This is how the user wants you to play the role: '{}'. Try you best to follow this instruction. \
                                  The user want to particularly practice these negotiation skills: '{}'. \
                                  Now, the negotiation is on. From now on, you are {} and please response as if engaging in a face-to-face conversation. \
                                  ".format(st.session_state['negotiation_info'][0],
                                            st.session_state['negotiation_info'][1],
                                            st.session_state['negotiation_info'][1],
                                            role_intention,
                                            st.session_state['negotiation_info'][3],
                                            practice_skills,
                                            st.session_state['negotiation_info'][1] ,
                                            st.session_state['negotiation_info'][1])


            st.session_state['system_instruction_suggestion'] = "\
                                              You are a negotiation expert. \
                                              Here is the negotiation senario: '{}'. \
                                              The user want to particularly practice these negotiation skills: '{}'. \
                                              Now, you will help the user to improve how they should negotiate. \
                                              ".format(st.session_state['negotiation_info'][0],  st.session_state['negotiation_info'][2])

            ### get started
            # st.write(st.session_state['system_instruction'])
            st.session_state.messages.append({"role": "assistant", "content": "Thank you for your patience! Let's get started!"})
            st.session_state.messages.append({"role": "assistant", "content": "How are you?"})
            st.session_state.negotiation.append({"role": "assistant", "content": "How are you?"})

            st.session_state['simulation_start'] = True

# if st.session_state['simulation_start'] == True:
else:
    if prompt:
      if prompt == 'SUGGESTIONS':
        st.session_state.messages.append({"role": "user", "content": 'SUGGESTIONS'})

        use_response = st.session_state.negotiation[-2]["content"]
        bot_response = st.session_state.negotiation[-3]["content"]

        ### print out the prompt
        # with st.chat_message("user"):
        #     st.markdown(use_response)

        # with st.chat_message("assistant"):
        #     st.markdown(bot_response)

        suggestion_prompt = "Now, you are thinking in my shoes. How to response for this paragraph: {}. \
                            My response is: {}. \
                            But please improve this response on behalf of me possiblly with these skills: {}. \
                            Just return the revised response text directly and the summarize how this revised response is better in terms of the skills mentioned above.".format(st.session_state['negotiation_info'][1], bot_response, use_response, st.session_state['practice_skill_global_variable'])

        ## add chat history to the prompt
        negotiation_knowledge = st.session_state['negotiation_info'][2]
        ## find relevant contexts in the pinecone negotiation knowledge base
        context = find_match(negotiation_knowledge)

        stream = client.chat.completions.create(
                model=st.session_state["openai_model"],
                messages=[
                    {"role": "system", "content": st.session_state['system_instruction_suggestion']}]
                    + [
                    {"role": "user", "content": suggestion_prompt}
                    ],
                stream=False,
            )
        response = stream.choices[0].message.content
        suggestions = " \
                      For this response: {}  \n \
                      A better way to say it with {} is: {}.  \n \
                      Now, you can directly retype your response to the previous Negoia's reply and the conversation will continue.".format(use_response, st.session_state['practice_skill_global_variable'], response)

        st.session_state.messages.append({"role": "assistant", "content": suggestions})


      elif prompt == 'NEW SCENARIO':

        st.session_state.messages.append({"role": "user", "content": 'NEW SCENARIO'})

        st.session_state['index_Q_completed'] = 0
        st.session_state['index_Q_shown'] = 1

        st.session_state.negotiation_info = []
        st.session_state['simulation_start'] = False

        st.session_state.messages.append({"role": "assistant", "content": 'I need to gather new information about the new scenario. Please answer the four questions again.'})
        st.session_state.messages.append({"role": "assistant", "content": preset_questions[st.session_state['index_Q_completed']]})


      elif prompt == 'END':
        st.session_state.messages.append({"role": "user", "content": 'END'})

        ### TBD: end the negotiation process and ask the user whether to export the chat history and restart the negotiation process
        #
        st.session_state.messages.append({"role": "assistant", "content": 'I hope this negotiation simulation was useful and wish you have a successful negotiation process.'})

        # download the chat history
        negotiation_history = ""
        for i in range(len(st.session_state['negotiation'])):
            m = st.session_state['negotiation'][i]
            negotiation_history += m["role"] + ": " + m["content"] + "\n"

        st.download_button('Download CSV', negotiation_history, '')
        # with open('myfile.csv') as f:
        #     st.download_button('Download CSV', f)  # Defaults to 'text/plain'


      elif prompt == 'RESTART':
        st.session_state.messages.append({"role": "user", "content": 'RESTART'})

        # empty the negotiation message basket
        st.session_state.negotiation = []

        # restart by saying:
        st.session_state.messages.append({"role": "assistant", "content": "Let's tried one more time!"})
        st.session_state.negotiation.append({"role": "assistant", "content": "How are you?"})
        st.session_state.messages.append({"role": "assistant", "content": "How are you?"})

      else:
        ### print out the prompt
        with st.chat_message("user"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.session_state.negotiation.append({"role": "user", "content": prompt})

        ### negotiation simulation
        with st.chat_message("assistant"):
            ## add chat history to the prompt
            conversation_string = get_conversation_string()
            ## refine the chat completion prompt
            refined_query = query_refiner(conversation_string, prompt)
            ## find relevant contexts in the pinecone negotiation knowledge base
            context = find_match(refined_query)

            # st.subheader("Refined Query:")
            # st.write(refined_query)

            ### feed the refined prompt to openai
            stream = client.chat.completions.create(
                model=st.session_state["openai_model"],
                messages=[
                    {"role": "system", "content": st.session_state['system_instruction']}]
                    + [
                    {"role": m["role"], "content": m["content"]}
                    # for m in st.session_state.messages[2+len(preset_questions)*2+1:-1]]
                    for m in st.session_state.negotiation[:-1]]
                    + [
                    {"role": "user", "content": prompt}
                    ],
                stream=False,
            )

            ### answer negotiation questions
            # stream = client.chat.completions.create(
            #     model=st.session_state["openai_model"],
            #     messages=[
            #         {"role": "assistant", "content": role_instruction_prompt}]
            #         + [
            #         {"role": m["role"], "content": m["content"]}
            #         for m in st.session_state.messages[:-1]]
            #         + [
            #         {"role": "assistant", "content": "You know that: {}".format(context)},
            #         {"role": "user", "content": prompt}
            #         ],
            #     stream=True,
            # )

            ### original
            # stream = client.chat.completions.create(
            #     model=st.session_state["openai_model"],
            #     messages=[
            #         {"role": m["role"], "content": m["content"]}
            #         for m in st.session_state.messages
            #     ],
            #     stream=True,
            # )

            # response = st.write_stream(stream)
            # response = st.write(stream)
            response = stream.choices[0].message.content

            st.session_state.messages.append({"role": "assistant", "content": response})
            st.session_state.negotiation.append({"role": "assistant", "content": response})


### suggestion button
# if st.session_state.clicked:
#     # The message and nested widget will remain on the page
#     bot_response = st.session_state.messages[-2]["content"]
#     use_response = st.session_state.messages[-1]["content"]
#     suggestion_prompt = "This is a negotiation process. How to response for this paragraph: {}. \
#                          Please improve this response: {}. \
#                          But please response with these skills: {}".format(bot_response, use_response, preset_questions[2])

#     stream = client.chat.completions.create(
#             model=st.session_state["openai_model"],
#             messages=[
#                 {"role": "assistant", "content": st.session_state['system_instruction']}]
#                 + [
#                 {"role": "assistant", "content": "You know that: {}".format(context)},
#                 {"role": "user", "content": suggestion_prompt}
#                 ],
#             stream=False,
#         )
#     # response = st.write(suggestions)
#     response = stream.choices[0].message.content
#     suggestions = "For this response: ".format(use_response) + ". You could try to say this:" + response

#     # st.session_state.messages.append({"role": "assistant", "content": suggestions}
#     st.session_state.clicked = False


### display all the chat
for message in st.session_state.messages:
  with st.chat_message(message["role"]):
      st.markdown(message["content"])
