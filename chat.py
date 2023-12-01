from openai import OpenAI
import streamlit as st

st.title("Imagination Captain")
st.markdown("#### Let your imagination be the captain of your journey!")
col1, col2, col3 = st.columns(3)
with col1:
    st.write("")
with col2:
    st.image("ic3.png", width=200)
with col3:
    st.write("")

# st.markdown("#### Describe the story you want to hear and then we will begin.")
system_prompt = """
You are an AI designed for engaging elementary school children in 
storytelling, now guides them through 'choose your own adventure' stories 
that conclude after approximately 10 interactive questions. This structure 
ensures a manageable and satisfying story length, 
suitable for young attention spans. 
Each part of the story you generate should be 3 to 4 sentences long.  You should only generate 1 part of the story at a time.
Uses simple language to weave adventure 
action tales, offering choices that shape the narrative.  Each story should end allow 
the child a choice of 3 and one additional choice of 'Or do you want to do something else?". The choices should be numbered like below.

1. first choice
2. second choice 
3. third choice 

Or do you want to do something else?

each choice should be on a line by itself.  Make sure the line "Or do you want to do something else?" is on a line by itself.
The choices should be a prompt of what to do next, with some examples but a person can pick what 
they want to do.  It can be from the examples or something completely different.  
Each story should have a happy ending """

with st.sidebar:
    st.image("ic3.png", width=300)
    st.markdown("### Settings")
    st.session_state["openai_model"] = st.selectbox(
        "OpenAI Model",
        [
            "gpt-3.5-turbo",
            "gpt-4-1106-preview",
        ],
    )
    st.markdown("### OpenAI API Key")
    st.session_state["openai_key"] = st.text_input(
        "API Key", type="password", key="OPENAI_API_KEY"
    )

client = OpenAI(api_key=st.session_state["openai_key"])
# client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"
    # st.session_state["openai_model"] = "gpt-4-1106-preview"

if "started" not in st.session_state:
    st.session_state["started"] = True
    chat_prompt = "What kind of story do you want to hear?"
else:
    chat_prompt = "What happens next?"

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"], unsafe_allow_html=True)

if prompt := st.chat_input("User Input"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        messages = [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages
        ]
        messages.insert(0, {"role": "assistant", "content": system_prompt})
        for response in client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=messages,
            stream=True,
        ):
            full_response += response.choices[0].delta.content or ""
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)

    # audio
    st.session_state.messages.append({"role": "assistant", "content": full_response})
    response = client.audio.speech.create(
        model="tts-1",
        voice="fable",
        input=full_response,
    )
    response.stream_to_file("output.mp3")
    st.audio("output.mp3")

    # image
    image_prompt = f"""Create an image of the story.  Make sure the image is appropriate for children.
    The image should be 1024x1024.  The image should be a PNG file.  The image should be a drawing of the story.  
    Do not include any text in the image.
    Here is the story:  {full_response}"""

    response = client.images.generate(
        model="dall-e-3",
        prompt=image_prompt,
        size="1024x1024",
        quality="standard",
        n=1,
    )

    image_url = response.data[0].url
    if image_url:
        image_tag = f'<image src="{image_url}" width="800"/>'
        st.markdown(image_tag, unsafe_allow_html=True)
        st.session_state.messages.append({"role": "assistant", "content": image_tag})
