##################################################################
# Chat with Open Source LLM Command R+
#
# History
# When      | Who            | What
# 25/04/2024| Tian-Qing Ye   | Created
# 26/04/2024| Tian-Qing Ye   | Bug fixing
# 14/05/2024| Tian-Qing Ye   | Allow controlling temperature
# 19/08/2024| Tian-Qing Ye   | Further updated
##################################################################
import streamlit as st
from streamlit_javascript import st_javascript
import cohere

import yaml
from yaml.loader import SafeLoader
from io import BytesIO
from gtts import gTTS, gTTSError

from langdetect import detect
import os
import sys
from datetime import datetime
from typing import List
import random, string
from random import randint
import argparse
import requests
import json

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

import libs

API_KEY = st.secrets["API_KEY"]

sendmail = True

SYS_MSG = "You are a helpful assistant who can answer or handle all my queries! If your reponses are based on the information from web search results, please include the source(s)!"
EN_BASE_PROMPT = [{"role": "SYSTEM", "message": SYS_MSG}]

class Locale:    
    ai_role_options: List[str]
    ai_role_prefix: str
    ai_role_postfix: str
    role_tab_label: str
    title: str
    choose_language: str
    language: str
    lang_code: str
    chat_tab_label: str
    chat_messages: str
    chat_placeholder: str
    chat_run_btn: str
    chat_clear_btn: str
    clear_doc_btn: str
    enable_search_label: str
    chat_clear_note: str
    file_upload_label: str
    temperature_label: str
    login_prompt: str
    logout_prompt: str
    username_prompt: str
    password_prompt: str
    choose_llm_prompt: str
    support_message: str
    select_placeholder1: str
    select_placeholder2: str
    stt_placeholder: str
    
    def __init__(self, 
                ai_role_options, 
                ai_role_prefix,
                ai_role_postfix,
                role_tab_label,
                title,
                choose_language,
                language,
                lang_code,
                chat_tab_label,
                chat_messages,
                chat_placeholder,
                chat_run_btn,
                chat_clear_btn,
                clear_doc_btn,
                enable_search_label,
                chat_clear_note,
                file_upload_label,
                temperature_label,
                login_prompt,
                logout_prompt,
                username_prompt,
                password_prompt,
                choose_llm_prompt,
                support_message,
                select_placeholder1,
                select_placeholder2,
                stt_placeholder,
                ):
        self.ai_role_options = ai_role_options, 
        self.ai_role_prefix= ai_role_prefix,
        self.ai_role_postfix= ai_role_postfix,
        self.role_tab_label = role_tab_label,
        self.title= title,
        self.choose_language = choose_language,
        self.language= language,
        self.lang_code= lang_code,
        self.chat_tab_label= chat_tab_label,
        self.chat_placeholder= chat_placeholder,
        self.chat_messages = chat_messages,
        self.chat_run_btn= chat_run_btn,
        self.chat_clear_btn= chat_clear_btn,
        self.clear_doc_btn = clear_doc_btn,
        self.enable_search_label = enable_search_label,
        self.chat_clear_note= chat_clear_note,
        self.file_upload_label = file_upload_label,
        self.temperature_label = temperature_label,
        self.login_prompt= login_prompt,
        self.logout_prompt= logout_prompt,
        self.username_prompt= username_prompt,
        self.password_prompt= password_prompt,
        self.choose_llm_prompt = choose_llm_prompt,
        self.support_message = support_message,
        self.select_placeholder1= select_placeholder1,
        self.select_placeholder2= select_placeholder2,
        self.stt_placeholder = stt_placeholder,


AI_ROLE_OPTIONS_EN = [
    "helpful assistant",
    "code assistant",
    "code reviewer",
    "text improver",
]

AI_ROLE_OPTIONS_ZW = [
    "helpful assistant",
    "code assistant",
    "code reviewer",
    "text improver",
]

en = Locale(
    ai_role_options=AI_ROLE_OPTIONS_EN,
    ai_role_prefix="You are an assistant",
    ai_role_postfix="Answer as concisely as possible.",
    role_tab_label="🤖 Sys Role",
    title="Ask Command R+",
    choose_language="选择界面语言",
    language="English",
    lang_code='en',
    chat_tab_label="💬 Chat",
    chat_placeholder="Your Request:",
    chat_messages="Messages:",
    chat_run_btn="✔️ Submit",
    chat_clear_btn=":cl: New Topic",
    clear_doc_btn=":x: Clear Doc",
    enable_search_label="Enable Web Search",
    chat_clear_note="Note: \nIf the upcoming topic does not relate to the previous conversation, please select the 'New Topic' button. This ensures that the new topic remains unaffected by any prior content!",
    file_upload_label="You can chat with an uploaded file (your file will never be saved anywhere)",
    temperature_label="Model Temperature",
    login_prompt="Login",
    logout_prompt="Logout",
    username_prompt="Username/password is incorrect",
    password_prompt="Please enter your username and password",
    choose_llm_prompt="Choose Your LLM",
    support_message="Please report any issues or suggestions to tqye@yahoo.com\n If you like this App please buy me a :coffee:🌝 https://buymeacoffee.com/tqye2006<p> To use other models：<br> OpenAI GPT-4 https://gptecho.streamlit.app <br> Claude https://claudeecho.streamlit.app<br><p>Other Tools：<br>Image Magic https://imagicapp.streamlit.app",
    select_placeholder1="Select Model",
    select_placeholder2="Select Role",
    stt_placeholder="Play Audio",
)

zw = Locale(
    ai_role_options=AI_ROLE_OPTIONS_ZW,
    ai_role_prefix="You are an assistant",
    ai_role_postfix="Answer as concisely as possible.",
    role_tab_label="🤖 AI角色",
    title="Ask Command R+",
    choose_language="Choose UI Language",
    language="中文·",
    lang_code='zh-CN',
    chat_tab_label="💬 会话",
    chat_placeholder="请输入你的问题或提示:",
    chat_messages="聊天内容:",
    chat_run_btn="✔️ 提交",
    chat_clear_btn=":cl: 新话题",
    clear_doc_btn="❌ 清空文件",
    enable_search_label="开通搜索",
    chat_clear_note="注意：\n若接下来的话题与之前的不相关，请点击“新话题”按钮，以确保新话题不会受之前内容的影响，同时也有助于节省字符传输量。谢谢！",
    file_upload_label="你可以询问一个上传的文件（文件内容只在内存，不会被保留）",
    temperature_label="模型温度",
    login_prompt="登陆：",
    logout_prompt="退出",
    username_prompt="用户名/密码错误",
    password_prompt="请输入用户名和密码",
    choose_llm_prompt="请选择您想使用的AI模型",
    support_message="如遇什么问题或有什么建议，反馈，请电 tqye@yahoo.com<\n 另外别忘了请我喝杯咖啡:coffee:🌝 https://buymeacoffee.com/tqye2006<p> 使用其它模型：<br>OpenAI GPT-4 href=https://gptecho.streamlit.app<br>Claude https://claudeecho.streamlit.app<p> 其它小工具：<br><a href=https://imagicapp.streamlit.app/>照片增强，去背景等</a>",
    select_placeholder1="选择AI模型",
    select_placeholder2="选择AI的角色",
    stt_placeholder="播放",
)

st.set_page_config(page_title="Ask Command R+", 
                   initial_sidebar_state="expanded", 
                   layout='wide',
                   menu_items={
                    'Report a bug': "mailto:tqye2006@gmail.com",
                    'About': "# For Experiment Only.April-2024"}
    )

st.markdown(
    """
        <style>
                .appview-container .main .block-container {{
                    padding-top: {padding_top}rem;
                    padding-bottom: {padding_bottom}rem;
                    }}

                .sidebar .sidebar-content {{
                    width: 36px;
                }}

        </style>""".format(padding_top=0, padding_bottom=1),
        unsafe_allow_html=True,
)

# maximum messages remembered
MAX_MESSAGES = 20

current_user = "**new_chat**"

if "user" not in st.session_state:
    st.session_state.user = ""

# system messages and/or context
set_context_all = {"General Assistant": ""}
set_context_all.update(libs.set_sys_context)

def randomword(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

@st.cache_data()
def parse_args(args):
    parser = argparse.ArgumentParser('AskLLM')
    parser.add_argument('--local', required=False)
    parser.add_argument('--seed', help='Seed for random generator', default=37, required=False)
    return parser.parse_args(args)

def callback_fun(arg):
    try:
        st.session_state[arg + current_user + "value"] = st.session_state[arg + current_user]

        sys_msg = ""
        for ctx in [
            set_context_all[st.session_state["context_select" + current_user]],
            st.session_state["context_input" + current_user],
        ]:
            if ctx != "":
                sys_msg += ctx + '\n'
    except Exception as ex:
        sys_msg = ""


    if len(sys_msg.strip()) > 10:
        SYS_PROMPT = [{"role": "SYSTEM", "message": sys_msg}]
    else:
        if st.session_state.locale is zw:
            SYS_PROMPT = [{"role": "SYSTEM", "message": SYS_MSG + "\nPlease reply in Chinese where possible!"}]
        else:
            SYS_PROMPT =  [{"role": "SYSTEM", "message": SYS_MSG}]

    st.session_state.messages = SYS_PROMPT

@st.cache_data()
def get_app_folder():
    app_folder = os.path.dirname(__file__)

    return app_folder

@st.cache_resource()
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    f.close()


@st.cache_data()
def get_geolocation(ip_address):
    '''
    Get location of an IP address
    '''
    url =f'https://ipapi.co/{ip_address}/json/'

    try:
        # Make the GET requests
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        location = {
            "city" : data.get("city)"),
            "region" : data.get("region"),
            "country" : data.get("country_name"),
            }
        return location
    except requests.RequestException as ex:
        print(f"An error: {ex}")
        return None

def get_client_ip():
    '''
    workaround solution, via 'https://api.ipify.org?format=json' for get client ip
    
    example:
    ip_address = client_ip()  # now you have it in the host...
    st.write(ip_address)  # so you can log it, etc.    
    '''
    url = 'https://api.ipify.org?format=json'

    script = (f'await fetch("{url}").then('
                'function(response) {'
                    'return response.json();'
                '})')

    ip_address = ""
    try:
        result = st_javascript(script)
        # print(f"ip_result: {result}")
        if isinstance(result, dict) and 'ip' in result:
            ip_address = result['ip']
        else:
            ip_address = "unknown_ip"
    except:
        pass

    return ip_address

@st.cache_resource()
def get_email_info():
    sender_email = st.secrets["gmail_user"]
    password = st.secrets["gmail_passwd"]

    return sender_email, password

@st.cache_data(show_spinner=False)
def save_log(query, res, total_tokens):
    '''
    Log an event or error
    '''
    now = datetime.now() # current date and time
    date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
    app_folder = get_app_folder()
    f = open(app_folder + "/LLM.log", "a", encoding='utf-8',)
    f.write(f'[{date_time}] {st.session_state.user}:():\n')
    f.write(f'[You]: {query}\n')
    f.write(f'[CommandR]: {res}\n')
    f.write(f'[Tokens]: {total_tokens}\n')
    f.write(f"User ip: {st.session_state.user_ip}")
    f.write(f"User Geo: {st.session_state.user_location}")
    f.write(100 * '-' + '\n\n') 

    try:
        if sendmail == True:
            send_mail(query, res, total_tokens)
    except Exception as ex:
        f.write(f'Sending mail failed {ex}\n')
        pass

    f.close()

    print(f'[{date_time}]: {st.session_state.user}\n')
    print(res+'\n')


@st.cache_data(show_spinner=False)
def send_mail(query, res, total_tokens):
    '''
    '''
    now = datetime.now() # current date and time
    date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
    message = f'[{date_time}] {st.session_state.user}:({st.session_state.user_ip}: {st.session_state.user_location}):\n'
    message += f'[You]: {query}\n'
    message += f'[CommandR]: {res}\n'
    message += f'[Tokens]: {total_tokens}\n'

    # Set up the SMTP server and log into your account
    smtp_server = "smtp.gmail.com"
    port = 587

    sender_email, password = get_email_info()

    server = smtplib.SMTP(smtp_server, port)
    server.starttls()
    server.login(sender_email, password)

    # Create the MIMEMultipart message object and load it with appropriate headers for From, To, and Subject fields
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = st.secrets["receive_mail"]
    msg['Subject'] = f"Chat from {st.session_state.user}"

    # Add your message body
    body = message
    msg.attach(MIMEText(body, 'plain'))

    try:
        filename, file_extension = os.path.splitext(res)
        if file_extension == ".png":
            # Open the image file in binary mode
            with open(res, 'rb') as fp:
                # Create a MIMEImage object with the image data
                img = MIMEImage(fp.read())

            # Attach the image to the MIMEMultipart object
            msg.attach(img)
    except Exception as e:
        print(f"Error: {str(e)}", 0)

    # Send the message using the SMTP server object
    server.send_message(msg)
    server.quit()


@st.cache_resource()
def Main_Title(text: str) -> None:

    st.markdown(f'<p style="background-color:#ffffff;color:#049ca4;font-weight:bold;font-size:24px;border-radius:2%;">{text}</p>', unsafe_allow_html=True)

def Show_Audio_Player(ai_content: str) -> None:
    sound_file = BytesIO()
    try:
        lang = detect(ai_content)
        print("Language:", lang)
        if lang in ['zh', 'zh-cn', 'en', 'de', 'fr'] :
            tts = gTTS(text=ai_content, lang=lang)
            tts.write_to_fp(sound_file)
            st.write(st.session_state.locale.stt_placeholder)
            st.audio(sound_file)
    except gTTSError as err:
        save_log("Error", str(err), 0)
    except Exception as ex:
        save_log("Error", str(ex), 0)


def Clear_Chat() -> None:
    st.session_state.messages = []        
    st.session_state.user_text = ""
    st.session_state.loaded_content = ""

    st.session_state["context_select" + current_user + "value"] = 'General Assistant'
    st.session_state["context_input" + current_user + "value"] = ""

    st.session_state.key += "1"     # HACK use the following two lines to reset update the file_uploader key
    st.rerun()

def Show_Messages():

    messages_str = []
    for _ in st.session_state["messages"][1:]:
        if(_['role'] == 'USER'):
            role = '**You**'
        elif (_['role'] == 'CHATBOT'):
            role = '**AI**'
        else:
            role = _['role']

        text = f"{_['message']}"
        if role == '**You**':
            print("Orignal text:", text)
            text_s = libs.remove_contexts(text)
            print("New text:", text_s)
            messages_str.append(f"{role}: {text_s}")
        else:
            messages_str.append(f"{role}: {text}")
    
    msg = str("\n\n".join(messages_str))
    #st.markdown(msg, unsafe_allow_html=True)
    st.write(msg, unsafe_allow_html=True)
    

@st.cache_resource()
def Create_Model():

    co = cohere.Client(api_key=API_KEY)

    return co

def Chat_Completion(query: str, chat_history: list):
    '''
    Chat with the model
    params: query: str, chat_history: list
    return: str
    '''

    if(len(chat_history) > MAX_MESSAGES+1):
        chat_history.pop(1)
        chat_history.pop(1)

    #print("=============== FOR DEBUG ==============================")
    #print(f"History: {chat_history}")
    #print(f"Query: {query}")
    #print("================ END DEBUG =============================")

    co = Create_Model()
    if st.session_state.enable_search:
        print("Search Web Enabled!")
        response = co.chat(
            chat_history=chat_history,
            message=query,
            model="command-r-plus",
            temperature=st.session_state.temperature,
            max_tokens=3800,
            prompt_truncation='AUTO',
            #chat_history=[
            #    {"role": "USER", "message": "Who discovered gravity?"},
            #    {
            #        "role": "CHATBOT",
            #        "message": "The man who is widely credited with discovering gravity is Sir Isaac Newton",
            #    },
            #],
            #message="What year was he born?",

            # perform web search before answering the question. You can also use your own custom connector.
            connectors=[{"id": "web-search"}],
        )
    else:
        response = co.chat(
            chat_history=chat_history,
            message=query,
            model="command-r-plus",
            temperature=st.session_state.temperature,
            max_tokens=3800,
            prompt_truncation='AUTO',
        )

    print(f"Outputs from the Model: {response}")

    ret_context = response.text
    
    return ret_context

##############################################
################ MAIN ########################
##############################################
def main(argv):

    args = parse_args(sys.argv[1:])
    st.session_state.is_local = args.local
    
    Main_Title(st.session_state.locale.title[0] + " (v0.0.3)")
    st.session_state.user_ip = get_client_ip()
    st.session_state.user_location = get_geolocation(st.session_state.user_ip)

    ## ----- AI Role  --------
    st.session_state.role_placeholder = st.empty()        # showing system role selected
    st.session_state.role_placeholder = st.info(st.session_state.locale.role_tab_label[0] + ": **" + st.session_state["context_select" + current_user + "value"] + "**")

    tab_chat, tab_context = st.tabs([st.session_state.locale.chat_tab_label[0], st.session_state.locale.role_tab_label[0]])

    with tab_context:
        set_context_list = list(set_context_all.keys())
        context_select_index = set_context_list.index(
            st.session_state["context_select" + current_user + "value"]
        )
        st.selectbox(
            label="Role Setting",
            options=set_context_list,
            key="context_select" + current_user,
            index=context_select_index,
            on_change=callback_fun,
            args=("context_select",),
        )
        st.caption(set_context_all[st.session_state["context_select" + current_user]])

        st.text_area(
            label="Add or Pre-define Role Message：",
            key="context_input" + current_user,
            value=st.session_state["context_input" + current_user + "value"],
            on_change=callback_fun,
            args=("context_input",),
        )

    ## ----- Chat Tab  --------
    with tab_chat:
        msg_placeholder = st.empty()

        ## ----- Show Previous Chats if Any --------
        with msg_placeholder:
            Show_Messages()

        st.session_state.gtts_placeholder = st.empty()

        st.session_state.uploading_file_placeholder = st.empty()
        st.session_state.uploaded_filename_placeholder = st.empty()
        st.session_state.buttons_placeholder = st.empty()
        st.session_state.input_placeholder = st.empty()

        with st.session_state.uploading_file_placeholder:
            uploaded_file = st.file_uploader(label=st.session_state.locale.file_upload_label[0], type=['docx', 'txt', 'pdf', 'csv'],key=st.session_state.key, accept_multiple_files=False,)
            if uploaded_file is not None:
                #bytes_data = uploaded_file.read()
                st.session_state.loaded_content, ierror = libs.GetContexts(uploaded_file)
                if ierror != 0:
                    print(f"Loading document failed:  {ierror}")
                    st.session_state.uploaded_filename_placeholder.warning(st.session_state.loaded_content)
                else:
                    doc_size=len(st.session_state.loaded_content)
                    print(f"The size of the document:  {doc_size}")
                    st.session_state.uploaded_filename_placeholder.write(f"{uploaded_file.name} [{doc_size}]")
                    st.session_state.enable_search = False

        with st.session_state.buttons_placeholder:
            c1, c2 = st.columns(2)
            with c1:
                st.session_state.new_topic_button = st.button(label=st.session_state.locale.chat_clear_btn[0], key="newTopic", on_click=Clear_Chat)
            with c2:
                st.session_state.enable_search = st.checkbox(label=st.session_state.locale.enable_search_label[0], value=st.session_state.enable_search)
        with st.session_state.input_placeholder.form(key="my_form", clear_on_submit = True):
            user_input = st.text_area(label=st.session_state.locale.chat_placeholder[0], value=st.session_state.user_text, max_chars=6600)
            send_button = st.form_submit_button(label=st.session_state.locale.chat_run_btn[0])

        if send_button :
            print(f"{st.session_state.user}: {user_input}")
            user_input = user_input.strip()
            if(user_input != ''):
                #if st.session_state.enable_search:
                #    #st.session_state.loaded_content = libs.Search_WiKi(user_input)
                #    st.session_state.loaded_content = libs.Search_DuckDuckGo(user_input)
                #    print(f"Results found: {len(st.session_state.loaded_content)}")
                if st.session_state.loaded_content != "":
                    prompt = f"<CONTEXT>{st.session_state.loaded_content}</CONTEXT>\n\n {user_input}"
                else:
                    prompt = user_input
                                    
                with st.spinner('Wait ...'):
                    st.session_state.model_response = Chat_Completion(prompt, st.session_state.messages)
                generated_text = st.session_state.model_response + '\n'
                st.session_state.messages += [{"role": "USER", "message": prompt}]
                st.session_state.messages += [{"role": "CHATBOT", "message": generated_text}]

				# counting the number of messages
                st.session_state.message_count += 1
                #st.session_state.total_tokens += tokens
                with msg_placeholder:
                    Show_Messages()
                with st.session_state.gtts_placeholder:
                    Show_Audio_Player(generated_text)

                save_log(user_input, generated_text, st.session_state.total_tokens)

##############################
if __name__ == "__main__":

    # Initiaiise session_state elements
    if "locale" not in st.session_state:
        st.session_state.locale = en

    if "lang_index" not in st.session_state:
        st.session_state.lang_index = 0
        
    if "user_ip" not in st.session_state:
        st.session_state.user_ip = get_client_ip()

    if "user_loacation" not in st.session_state:
        st.session_state.user_location = {}

    if "is_local" not in st.session_state:
        st.session_state.is_local = False

    if "loaded_content" not in st.session_state:
        st.session_state.loaded_content = ""

    if "enable_search" not in st.session_state:
        st.session_state.enable_search = False

    if "model_response" not in st.session_state:
        st.session_state.model_response = ""

    if "message_count" not in st.session_state:
        st.session_state.message_count = 0

    if "user_text" not in st.session_state:
        st.session_state.user_text = ""

    if 'max_new_tokens' not in st.session_state:
        st.session_state.max_new_tokens = 1024

    if 'total_tokens' not in st.session_state:
        st.session_state.total_tokens = 0

    if 'key' not in st.session_state:
        st.session_state.key = str(randint(1000, 10000000))    

    if "messages" not in st.session_state:
        st.session_state.messages = EN_BASE_PROMPT
    
    st.markdown(
            """
                <style>
                    .appview-container .block-container {{
                        padding-top: {padding_top}rem;
                        padding-bottom: {padding_bottom}rem;
                    }}
                    .sidebar .sidebar-content {{
                        width: 200px;
                    }}
                    .st-emotion-cache-fis6aj {{
                        display: none;
                    }}
                    .st-emotion-cache-9ycgxx {{
                        display: none;
                    }}
                    button {{
                        /*    height: auto; */
                        width: 120px;
                        height: 32px;
                        padding-top: 10px !important;
                        padding-bottom: 10px !important;
                    }}
                </style>""".format(padding_top=2, padding_bottom=10),
            unsafe_allow_html=True,
    )

    #local_css("style.css")

    language = st.sidebar.selectbox(st.session_state.locale.choose_language[0], ("English", "中文"), index=st.session_state.lang_index)
    if language == "English":
        st.session_state.locale = en
        st.session_state.lang_index = 0
    else:
        st.session_state.locale = zw
        st.session_state.lang_index = 1
        
    st.session_state.temperature = st.sidebar.slider(label=st.session_state.locale.temperature_label[0], min_value=0.1, max_value=2.0, value=0.5, step=0.05)
    st.sidebar.markdown(st.session_state.locale.chat_clear_note[0])
    st.sidebar.markdown(st.session_state.locale.support_message[0], unsafe_allow_html=True)
    
    #st.session_state.user, st.session_state.authentication_status, st.session_state.user_id = Login()
    #if st.session_state.user != None and st.session_state.user != "" and st.session_state.user != "invalid":
    #    current_user = st.session_state.user_id

    #    if "context_select" + current_user + "value" not in st.session_state:
    #        st.session_state["context_select" + current_user + "value"] = 'General Assistant'

    #    if "context_input" + current_user + "value" not in st.session_state:
    #        st.session_state["context_input" + current_user + "value"] = ""

    current_user = st.session_state.user
    if "context_select" + current_user + "value" not in st.session_state:
        st.session_state["context_select" + current_user + "value"] = 'General Assistant'    
    if "context_input" + current_user + "value" not in st.session_state:
        st.session_state["context_input" + current_user + "value"] = ""
    
    main(sys.argv)


    
