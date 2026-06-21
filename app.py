from openai import OpenAI
import streamlit as st
from streamlit_js_eval import streamlit_js_eval

st.set_page_config(page_title="streamlit chatbot", page_icon=":robot_face:")

if "setup_complete" not in st.session_state:
    st.session_state.setup_complete = False
if "user_message_count" not in st.session_state:
    st.session_state.user_message_count = 0
if "feedback_shown" not in st.session_state:
    st.session_state.feedback_shown = False
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_completed" not in st.session_state:
    st.session_state.chat_completed = False

def complete_setup():
    st.session_state.setup_complete = True

def show_feedback():
    st.session_state.feedback_shown = True
    st.session_state.chat_completed = True

if not st.session_state.setup_complete:

    st.subheader("Personal Information", divider="rainbow")

    if "name" not in st.session_state:
        st.session_state.name = ""
    if "experience" not in st.session_state:
        st.session_state.experience = ""
    if "skills" not in st.session_state:
        st.session_state.skills = ""

    st.session_state.name = st.text_input(label="Name", placeholder="Enter your name"
                        , max_chars=40)

    st.session_state.experience = st.text_area(label="Experience"
                            , placeholder="Enter your experience"
                            , max_chars=200
                            , height=None)
    st.session_state.skills = st.text_area(label="Skills"
                            , placeholder="Enter your skills"
                            , max_chars=200
                            , height=None)


    st.subheader("Company and Position", divider="rainbow")

    if "level" not in st.session_state:
        st.session_state.level = "" 
    if "position" not in st.session_state:
        st.session_state.position = ""
    if "company" not in st.session_state:
        st.session_state.company = ""

    col1, col2 = st.columns(2)

    with col1:
        st.session_state.level = st.radio(
            "Choose your level",
            key="visibility",
            options=["Junior", "Mid-level", "Senior"],
        )

    with col2:
        st.session_state.position = st.selectbox(
            "Choose a Position", 
                                ["Data Scientist", "Data Engineer", "Machine Learning Engineer", "BI Analyst"
                                ,"Financial Analyst", "Senior QA Automation Architect"])

    st.session_state.company = st.selectbox(
        "Choose a Company", 
                            ["Google", "Microsoft", "Amazon", "Facebook", "Apple", "Netflix"])                              

    if st.button("Complete Setup", on_click=complete_setup):
        st.success("Setup Complete! You can now start chatting with the assistant.")

if st.session_state.setup_complete and not st.session_state.chat_completed and not st.session_state.feedback_shown:
    st.subheader("Chat with the Assistant", divider="rainbow")

    st.info(f"""
            start introducing yourself to the assistant, and it will start the interview process for the position {st.session_state.level} {st.session_state.position} 
            at the company {st.session_state.company}.
            """, icon="ℹ️")

    client= OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    if "openai_model" not in st.session_state:
        st.session_state.openai_model = "gpt-5-nano"

    if "messages" not in st.session_state:
        st.session_state.messages = [{
                "role":"system",
                "content":
                f"""
                You are an HR executive that interviews an interviwee
                called {st.session_state.name} with expereince {st.session_state.experience} and skills
                you should interview them for the position {st.session_state.level} {st.session_state.position}
                at the company {st.session_state.company}.
                """
            }]    

    for m in st.session_state.messages:
        print(f"{m["role"]} and {m["content"]}")
        if m["role"] != "system": 
            with st.chat_message(m["role"]):
                st.markdown(m["content"])

    if st.session_state.user_message_count < 2 and not st.session_state.feedback_shown:
   
        if prompt := st.chat_input("Your answer,", max_chars=1000):
            st.session_state.messages.append({"role": "user",
            "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            if st.session_state.user_message_count < 2:
                with st.chat_message("assistant"):
                    stream = client.chat.completions.create(
                        model=st.session_state.openai_model,
                        messages=[
                            {"role": m["role"], "content": m["content"]}
                            for m in st.session_state.messages
                        ],
                        stream=True
                    )
                    response = st.write_stream(stream)
                st.session_state.messages.append({"role": "assistant", "content": response})
            st.session_state.user_message_count += 1

    if st.session_state.user_message_count >= 2:
        st.session_state.chat_completed = True
        

if st.session_state.chat_completed and not st.session_state.feedback_shown:
    if st.button("Submit Feedback", on_click=show_feedback):
        st.write("Fetching feedback!")

if st.session_state.feedback_shown:
    
    st.subheader("Feedback", divider="rainbow")
    st.info("Thank you for completing the interview! Here is your feedback.", icon="ℹ️")

    conversation_history = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
    print(conversation_history)

    client= OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    feedback_prompt = client.chat.completions.create(
        messages= [{"role": "system", "content": """You are a helpful tool that provides feedback on an interviewee performance.
             Before the Feedback give a score of 1 to 10.
             Follow this format:
             Overal Score: //Your score
             Feedback: //Here you put your feedback
             Give only the feedback do not ask any additional questins.
              """},
              {"role": "user", "content": f"""This is the interview you need to evaluate. 
               Keep in mind that you are only a tool. 
               And you shouldn't engage in any converstation: {conversation_history}"""}],
              model=st.session_state.openai_model
    )

    print(feedback_prompt)

    st.write(feedback_prompt.choices[0].message.content)

    if st.button("Restart Interview", types="primary"):
        streamlit_js_eval(js_expressions="parent.window.location.reload()")




    