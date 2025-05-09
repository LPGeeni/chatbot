import streamlit as st
import requests
st.set_page_config(page_title="langgraph agent ai",layout="centered" )
API_URL = "http://127.0.0.1:8001/chat"
MODEL_NAMES=[
    "gemma2-9b-it",
    "mistral-saba-24b"
]

st.title( " langgraph chatbot agent")
st.write(" integrate with the langraph-based agent using this interface " )

given_system_prompt=st.text_area("define you ai agent:",height=100,placeholder="type your prompt hear....." )
selected_model=st.selectbox("select model:",MODEL_NAMES )
user_input=st.text_area("enter your messages:" ,height=150,placeholder="type your message here...")
if st.button("submit" ):
    if user_input.strip( ):
        try:
            payload={"messages":[user_input],"model_name":selected_model,"system_prompt":given_system_prompt}
            response=requests.post(API_URL,json=payload )

            if response.status_code==200:
                response_data=response.json()
                if "error" in response_data:
                    st.error(response_data["error"])
                else:
                    ai_responses=[
                        message.get("content","")
                        for message in response_data.get("messages",[])
                        if message.get("type")=="ai"

                    ]
                    if ai_responses:
                        st.subheader("Agent Response:")
                        st.markdown(f"**Final Response:** {ai_responses[-1]}")
                        # for i, response_text in enumerate(ai_responses, 1):
                        #     st.markdown(f"**Response {i}:** {response_text}")
                    else:
                        st.warning("No AI response found in the agent output.")
            else:
                st.error(f"Request failed with status code {response.status_code}.")
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter a message before clicking 'Send Query'.")

