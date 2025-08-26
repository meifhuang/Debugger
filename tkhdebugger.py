import streamlit as st
from langchain_openai.chat_models import ChatOpenAI

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings


file_path = "data/"
loader = PyPDFDirectoryLoader(file_path)
docs = loader.load()
print(len(docs))
docs[144]

embeddings = OpenAIEmbeddings(api_key=api_key)

solutions_db = Chroma.from_documents(documents=docs, embedding=embeddings, persist_directory="./solutions")
solutions_db.persist()

st.title("TKH Code Debugger")
st.text("Please enter your own API key to start debugging your code")

openai_api_key = st.text_input("Enter OpenAI API Key", type="password")

def generate_response(input_text):
    model = ChatOpenAI(model="gpt-4o-mini", temperature=0.7, api_key=openai_api_key)
    st.info(model.invoke(input_text))

# def solution_proposer(student_bug: str) -> str:
#     context = solutions_retriever.get_relevant_documents(student_bug)
#     prompt = f"""
#         Student Error Message: {student_bug} 
#         You are a master expert at teaching, implementing code and debugging code for students at a data science fellowship.
#         Use the solutions context which contains class slides and PDF to point students to where they can refer to
#         to find the solution or topic to their question. If possible include phase, week and day and page number - extract this information from the title of the pdf and display it like Phase 1, Week 1, Day 1 (P represents Phase, W represents week and D represents day)
#         {context}
#         """

#     resp = client.chat.completions.create(
#             model="gpt-4o-mini",
#             messages=[{"role": "user", "content": prompt}],
#             temperature=0.1,
#         )
#     return resp.choices[0].message.content


with st.form("my_form"):
    text = st.text_area(
        "Please enter your code and your error message",
    )
    submitted = st.form_submit_button("Submit")
    if not openai_api_key.startswith("sk-"):
        st.warning("Please enter your OpenAI API key!", icon="⚠")
    if submitted and openai_api_key.startswith("sk-"):
        generate_response(text)