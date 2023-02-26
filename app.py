import operations as op
import textwrap
# from dotenv import load_dotenv
import streamlit as st
import os
import nltk
from nltk.tokenize import sent_tokenize
import openai
nltk.download('punkt')


openai.organization = os.environ['org']
openai.api_key = os.environ['api_key']


st.title("Ekatra QnA")
st.write("AI Powered Smart Search System")

st.markdown('_Welcome to Question Answering System 🧠 🤖_')

top_match_sentences = []


@st.cache(allow_output_mutation=True)
def process_pdf_data(uploaded_files):
    """
    The function accepts an uploaded PDF file as input and then proceeds to extract, preprocess, and vectorize the text. It ultimately returns a list of filtered sentences and their respective embeddings.

    Parameters: 
    uploaded_files (list): List of uploaded files

    Returns: 
    filt1_list (list): List of filtered sentences
    embeddings (list): List of embeddings of the sentences

    """
    filt1_list = []
    embeddings = []

    text_ext = []
    for i in uploaded_files:
        if i.type == "application/pdf":
            # Reading the pdf file and extracting the text
            text_ext += op.read_pdf(i)

    # Applying sent_tokenize to the text and storing the result in a list
    sent_toks = []
    for i in text_ext:
        sent_toks.append(sent_tokenize(i))

    concat_list = [j for i in sent_toks for j in i]

    # Removing the new line characters from the list
    for i in concat_list:
        a = (i.replace('\n', ' '))
        filt1_list.append(a)

    # Creating embeddings for the sentences
    embeddings = op.create_content_embeddings(filt1_list)
    return filt1_list, embeddings


# Streamlit code to upload files
uploaded_files = st.file_uploader(
    "Upload files - ", accept_multiple_files=True, type=['pdf'])

if st.button("Process!"):
    if len(uploaded_files) != 0:
        # Calling the function process_pdf_data to process the uploaded files
        filt1_list, embeddings = process_pdf_data(uploaded_files)
        st.write("Process Completed")

    else:
        st.warning("Please upload a PDF file.")

# Streamlit code to take user input after vectorization of the documents
query = st.text_input('Ask me anything!', placeholder='Type.....')
try:
    if st.button("Confirm!"):

        cached_data = process_pdf_data(uploaded_files)
        filt1_list = cached_data[0]
        embeddings = cached_data[1]

        # Creating embeddings for the query
        query_embedding = op.create_query_embeddings(query)

        # Calculating cosine similarity between the query and the sentences
        cosine_lis = op.calculate_cosine(
            query_embedding, embeddings, filt1_list)

        # Fetching the top 15 sentences with the highest cosine similarity
        indexes_final = op.fetch_top_rank_ans(cosine_lis, 15)

        # Fetching the most relevant sentence from the top 15 sentences, and providing it as the context to the GPT-3 model
        most_relevant = op.fetch_most_relevant(
            indexes_final, filt1_list, cosine_lis, query)

        # Calling the GPT-3 model to generate the answer
        COMPLETIONS_API_PARAMS = {
            "temperature": 0.0,
            "max_tokens": 300,
            "model": "text-davinci-003",
        }

        response = openai.Completion.create(
            prompt=most_relevant,
            **COMPLETIONS_API_PARAMS
        )
        # print("\n\n", textwrap.fill(
        #     response["choices"][0]["text"].strip(" \n")))

        # Displaying the answer to the user
        st.write(textwrap.fill(response["choices"][0]["text"].strip(" \n")))
except:
    st.warning("Something went wrong. Please try again.")
