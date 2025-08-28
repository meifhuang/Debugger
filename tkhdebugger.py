import streamlit as st
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from openai import OpenAI

st.title("TKH Code Debugger")
st.text("Please enter your own API key to start debugging your code")
openai_api_key = st.text_input("Enter OpenAI API Key", type="password")
embeddings = OpenAIEmbeddings(api_key=openai_api_key)
solutions_db = Chroma(persist_directory="./solutions", embedding_function=embeddings)
solutions_retriever = solutions_db.as_retriever(search_kwargs={"k": 3})


client = OpenAI(api_key=openai_api_key)

def solution_proposer(student_bug: str) -> str:

    context = solutions_retriever.get_relevant_documents(student_bug)
    prompt = f"""
        Student Error Message: {student_bug} 
        You are a master instructor and an expert at the Python, SQL, and Pandas, coding languages.
        Please use the solution context to review the student’s code and point to the correct documentation to help them debug their code.
        Please do not provide the answer.
        Please be empathetic and encouraging, you know from experience that learning to code is difficult.
        Please provide the Phase, week, date and exact page of the documentation
        (P represents Phase, W represents week and D represents day)
        {context}
        """
    resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
        )
    return resp.choices[0].message.content
    

def solution_checker(student_bug: str, solution: str) -> str: 
    prompt = f"""
        Review this response and make sure the answer was not directly given to the student.
        If it does, please update it and remove any given solutions.
        You should point to one or more resource(s) and only guide student and give hints to the solution. Be sure that the phase, week and day is included if it was provided by the slides. 
        Follow this format:
        To guide you in resolving this issue, I recommend reviewing the materials from your fellowship. Specifically, you can check the following resources: 
        This is the student's error message: {student_bug}
        This is the response {solution}
        Direct this message to the student.
    """

    resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
        )
    return resp.choices[0].message.content

with st.form("my_form"):
    text = st.text_area(
        "How may I help you? You may also provide code blocks or error messages.",
    )
    submitted = st.form_submit_button("Submit")
    if not openai_api_key.startswith("sk-"):
        st.warning("Please enter your OpenAI API key!", icon="⚠")
    if submitted and openai_api_key.startswith("sk-"):
        with st.spinner("Loading..."):
            solution = solution_checker(text, solution_proposer(text))
            st.info(solution)

        