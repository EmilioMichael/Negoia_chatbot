
# from langchain_community.embeddings import SentenceTransformerEmbeddings
from sentence_transformers import SentenceTransformer
import pinecone
from pinecone import Pinecone
from openai import OpenAI
import streamlit as st
import os


model = SentenceTransformer('all-MiniLM-L6-v2')


def find_match(input):
    input_em = model.encode(input).tolist()
    result = index.query(vector=input_em, top_k=2, includeMetadata=True)
    if len(result['matches']) == 0:
        return ''
    else:
        return result['matches'][0]['metadata']['text']+"\n"+result['matches'][1]['metadata']['text']


def query_refiner(openai_client, conversation, query):
    response = openai_client.completions.create(
    model="gpt-3.5-turbo-instruct",
    prompt=f"Given the following user query and conversation log, formulate a question that would be the most relevant to provide the user with an answer from a knowledge base.\n\nCONVERSATION LOG: \n{conversation}\n\nQuery: {query}\n\nRefined Query:",
    temperature=0.7,
    max_tokens=256,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0
    )

    return response.choices[0].text


def get_conversation_string():
    conversation_string = ""
    for i in range(len(st.session_state['negotiation'])-1):
        m = st.session_state['negotiation'][i]
        conversation_string += m["role"] + ": " + m["content"] + "\n"
    return conversation_string


### OpenAI chunks
def get_negotiation_intention(openai_client, scenario, role):
    response = openai_client.completions.create(
    model="gpt-3.5-turbo-instruct",
    prompt="This is a negotiation scenario: {} \
            What is the negotiation goal of the role of: {} in this negotiation? Please rely me directly the goal in one sentence.".format(scenario, role),
    temperature=0.7,
    max_tokens=256,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0
    )

    return response.choices[0].text

def get_negotiation_batna(openai_client, scenario, role):
    response = openai_client.completions.create(
    model="gpt-3.5-turbo-instruct",
    prompt="This is a negotiation scenario: {} \
            What is the BATNA of the role of: {} in this negotiation? Please rely me directly the BATNA in one sentence.".format(scenario, role),
    temperature=0.7,
    max_tokens=256,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0
    )

    return response.choices[0].text


def get_negotiation_practice_skill(openai_client, skills):
    response = openai_client.completions.create(
    model="gpt-3.5-turbo-instruct",
    prompt="What are the most relevant skills that the user want to practice based on this sentense: {} \
            Please only return the words of the skills and seperate them with commas. It should be less than three words and neglect some general words like 'practice'.".format(skills),
    temperature=0.7,
    max_tokens=256,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0
    )
    return response.choices[0].text


def get_difficult_conversation_tactics(openai_client, tactics):
    response = openai_client.completions.create(
    model="gpt-3.5-turbo-instruct",
    prompt="The answer to 'What difficult tactics do you want me to play?' is {}. Based on this answer, return me 'Yes' or 'No' to indicate whether the there are specific tactics mentioned in the answer.".format(skills),
    temperature=0.7,
    max_tokens=256,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0
    )

    result = response.choices[0].text
    if result == 'Yes':
        return True
    else:
        return False
