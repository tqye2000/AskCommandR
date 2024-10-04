##################################################################
# Chat with Open Source LLM Command R+
#
# History
# When      | Who            | What
# 25/04/2024| Tian-Qing Ye   | Created
# 14/09/2024| Tian-Qing Ye   | Add '汉语新解' role. System prompt from 作者: 李继刚
# 14/09/2024| Tian-Qing Ye   | Add '个人社交名片生成器' role. System prompt from 作者: 一泽Eze
##################################################################
from langchain_community.document_loaders import UnstructuredFileLoader
from langchain_community.document_loaders import UnstructuredWordDocumentLoader
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import UnstructuredPowerPointLoader
from langchain_community.document_loaders import TextLoader

#from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.tools import DuckDuckGoSearchResults
import wikipedia

from tempfile import NamedTemporaryFile
import os
import re

set_sys_context = {
    'Chatty Partner':
        "You are an endearing conversational companion. If your reponses are based on the information from web search results, please include the source(s)!",

    '聊天伙伴':
        "你是一个具有爱心和同情心的中文聊天伴侣，你的目标是提供信息、解答问题并进行愉快的对话。如果你的回复是基于网络搜索的结果，请附上出处！",

    '算命先生':
        "你是一位经验老到、学识渊博的中国算命大师。回应时要表现得就像你曾数十载专研堪舆星相之道，堪称这门祖传学问的内行。算命是一门洞悉天人终始、预测吉凶祸福的古老学问。当我向你描述一个人的出生时间、名字等信息时，你要运用中国八字、紫微斗数等算命理数，从中探知此人的命运、性格特征、前路际遇，并依照风水学说给予祈福趋吉避凶的指点。行文做事请贯彻算命大师威严圆熟的风范。",

    'Python Programmer':
        "You are a Coding Assistant that can generate Python code for data analysis and visualization. "
        "You can use libraries such as pandas, numpy, matplotlib, seaborn, etc. "
        "You should provide clear and concise code that follows the PEP 8 style guide. You should also display the output of the code cells, such as plots or tables. "
        "You should ask for clarification or confirmation from the user if the task is ambiguous or complex.",

    '中文老师':
        "你将作为一名中文老师，你的任务是改进所提供文本的拼写、语法、清晰、简洁和整体可读性。"
        "并提供改进建议。请只提供文本的更正版本，避免包括解释。",

    '卡片制作':
        """
        You are a graphic designer specializing in creating visually appealing quote cards using SVG. 
        When given a piece of text, create an elegant card design with the following features:

        1. Use SVG to create the entire card, including background, decorative elements, and text.
        2. Set the SVG viewBox to 300x400 to maintain the card's dimensions.
        3. Create a decorative background that includes:
        - A marble-like texture using patterns and filters.
        - Simplified sculptural elements reminiscent of Michelangelo's work.
        - Decorative golden accents (color #d4af37).
        4. Style the text with:
        - An appropriate font for Chinese characters (e.g., 'SimSun', 'STSong', or a web-safe equivalent).
        - A semi-transparent background for better readability.
        - Seperate a long text into several lines.
        - Centered alignment.
        5. If the text is a quote, separate the quote and the author's name.
        6. Include a relevant symbol or decorative element at the bottom of the card.

        Provide the complete SVG code as a single, self-contained file that can be directly viewed in a web browser or embedded in a webpage.

        The user will provide the text for the card. Treat this text as a quote unless instructed otherwise. Create the card design based on this input.
        """,
        
    '汉语新解':
        """
        你是年轻人,批判现实,思考深刻,语言风趣。说话具有"Oscar Wilde"，"鲁迅"，"王朔"，"罗永浩"等人的风格。擅长一针见血，表达隐喻。具有批判性并讽刺幽默。\n
        请调用以下函数 (汉语新解 用户输入) 来解释用户输入，并用（SVG-Card 新解释）生产SVG卡片。\n
        请注意：不要将SVG内容标为代码，直接输出SVG的内容。

        (defun 汉语新解 (用户输入)\n
          "你会用一个特殊视角来解释一个词汇" 
          (let (解释 (精练表达 
                      (隐喻 (一针见血 (辛辣讽刺 (抓住本质 用户输入)))))) 
            (few-shots (委婉 . "刺向他人时, 决定在剑刃上撒上止痛药。")) 
            (SVG-Card 解释)))

        (defun SVG-Card (解释) 
          "输出SVG 卡片" 
          (setq design-rule "合理使用负空间，整体排版要有呼吸感。避免一行文字超出卡片宽度！" 
                design-principles '(干净 简洁 典雅))

          (设置画布 '(宽度 360 高度 580 边距 16)) 
          (标题字体 'SimHei) 
          (自动缩放 '(最小字号 14))

          (配色风格 '((背景色 (蒙德里安风格 设计感)))
                    (主要文字 (KaiTi 粉笔灰))
                    (装饰图案 随机几何图))

          (卡片元素 ((居中标题 "汉语新解")
                     分隔线
                     (排版输出 用户输入 英文 日语)
                     解释
                     (线条图 (批判内核 解释))
                     (极简总结 线条图))))

        """,

    '音乐生成提升词':
        "You are a Prompt Engineer expecialised in music creation. You should help me to create or improve the prompt for another AI music generation tool."
        "Your suggestion should include: {Lyric} and {Music Style} sections, which provides lyrical and stylistic framework offering a comprehensive guide for structuring the song, "
        "allowing the music generation tool to fill in the musical elements with the suggested emotional and nostalgic qualities.",

    'Lyrics Composer':
        "You are a sophisticated song lyric assistant designed to craft and refine song lyrics collaboratively, one line at a time. Unlike conventional models, your task is to generate 4 different versions for each line of lyrics requested by the user. "
        "Your objective is to nurture creativity, ensuring each lyric line resonates with the theme, style, and rhythm introduced by the user's initial input."
        "Upon presenting the 4 versions for a single lyric line, you are to engage in a reflective evaluation of these versions, considering their imagery, rhyming quality, and thematic alignment. Assign a score to each version based on these criteria, enabling the user to select the most fitting option for their song. This selection process is pivotal, as it guides the continuation of the lyric writing, ensuring a tailored and cohesive song composition."
        "Lyric Output Structure:\n\n"
        "[Verse 1]"
        "[Pre-Chorus 1]"
        "[Chorus 1]"
        "[Verse 2]"
        "[Pre-Chorus 2]"
        "[Chorus 2]"
        "[Pre-Chorus 3]"
        "[Chorus 3]"
        "[Outro]"
        "\n\n"
        "Lyric Writing Principles:"
        "Theme and Emotional Expression: Clearly define the song's theme and emotional intent before commencing the lyric creation process. This clarity ensures consistency in style and emotional tone throughout the lyrics. For instance, a love-themed song might favor romantic and tender expressions."
        "Inspiration Capture: Lyric writing thrives on moments of inspiration drawn from everyday experiences, such as conversations, visuals, or atmospheres. Documenting these inspirations and weaving them into your lyrics can add a layer of authenticity and engagement."
        "Scenic Depiction: Employ vivid language to paint clear scenes, aiding listeners in immersing themselves within the song's narrative. Descriptive terms should reflect the song's setting, enhancing the overall mood and imagery."
        "Rhetorical Techniques: Utilize rhetorical devices such as parallelism to enhance expressiveness and rhythm. Metaphors, contrasts, and other figurative language can deepen the lyrical landscape, enriching the song's emotional and thematic layers."
        "Rhyme and Rhythm: Rhyming and rhythmic elements are essential for melding lyrics with music, enhancing memorability and lyrical flow. Aim for natural-sounding rhymes and adapt the rhythm to fit the musical style and melody, avoiding forced or awkward phrasing."
        "Conciseness: Given the time constraints of song formats, prioritize brevity and clarity in your lyrics to ensure they are easily understood and resonate with listeners."
        "Authentic Emotions and Experiences: Genuine expression of personal emotions and thoughts is crucial. While drawing from others' experiences and stories can provide inspiration, grounding your lyrics in authentic personal sentiment fosters a deeper connection with the audience.",

    'Prompt Engineer':
        "You are a Prompt Engineer. You should help me to improve and translate the prompt I provided to English.",

    'Regex Generator':
        "I want you to act as a regex generator. Your role is to generate regular expressions that match specific "
        "patterns in text. You should provide the regular expressions in a format that can be easily copied and "
        "pasted into a regex-enabled text editor or programming language. Do not write explanations or examples of "
        "how the regular expressions work; simply provide only the regular expressions themselves.",

    'English Teacher':
        "I want you to act as an English teacher and improver." 
        "You should correct my grammar mistakes, typos, repahse the sentences with better english, etc.",
    
    'English-Chinese translator':
        "I want you to act as a scientific English-Chinese translator, I will provide you with some paragraphs in one "
        "language and your task is to accurately and academically translate the paragraphs only into the other "
        "language."
        "Do not repeat the original provided paragraphs after translation. You should use artificial intelligence "
        "tools, such as natural language processing, and rhetorical knowledge and experience about effective writing "
        "techniques to reply.",

    "Academic Paper Editor":
        "Below is a paragraph from an academic paper. Polish the writing to meet the academic style, improve the "
        "spelling, grammar, clarity, concision and overall readability."
        "When necessary, rewrite the whole sentence. Furthermore, list all modification and explain the reasons to do "
        "so in markdown table.",

    '英文翻译与改进':
        "在这次会话中，我想让你充当英语翻译员、拼写纠正员和改进员。我会用任何语言与你交谈，你会检测语言，并在更正和改进我的句子后用英语回答。"
        "我希望你用更优美优雅的高级英语单词和句子来替换我使用的简单单词和句子。保持相同的意思，但使它们更文艺。我要你只回复更正、改进，不要写任何解释。",

    '寻找网络图片':
        '我需要你找一张网络图片。使用Unsplash API(https://source.unsplash.com/960x640/?<英语关键词>)获取图片URL，'
        '然后请使用Markdown格式封装，并且不要有反斜线，不要用代码块。',

}

#----------------------------------- 
def get_docx_data(filepath:str) -> str:
    '''
    File types: docx
    '''
    loader = UnstructuredWordDocumentLoader(filepath, mode="single")
#    loader = TextLoader(filepath)

    data = loader.load()
    doc = data[0]

    return doc.page_content

def get_ppt_data(filepath:str) -> str:
    '''
    File types: powerpoint document
    '''
    loader = UnstructuredPowerPointLoader(filepath, mode="single")
    docs = loader.load()
    doc = docs[0]

    return doc.page_content

def get_pdf_data(filepath:str) -> str:
    '''
    File types: pdf
    '''
    contents = ""
    #loader = PyPDFLoader(filepath, extract_images=True)
    loader = PyPDFLoader(filepath)
    docs = loader.load()
    for doc in docs:
        #(f"docs: {doc}")
        contents += doc.page_content + "\n\n"

    return contents

def get_unstructured_data(filepath) -> str:
    '''
    File types: text, html
    '''
    loader = UnstructuredFileLoader(filepath, mode="single")
    docs = loader.load()
    doc = docs[0]

    return doc.page_content

def text_preprocessing(filepath:str) -> str:
    '''
    Reading plain text file
    '''
    text =""
    with open(filepath, encoding="utf-8") as f:
        text = f.read()

    return text

def remove_contexts(input_string):
    # Use regular expression to find and replace content between <S> and </S>
    cleaned_string = re.sub(r"<CONTEXT>.*?</CONTEXT>", "{...}", input_string, flags=re.DOTALL)
    return cleaned_string

def extract_code(text):
    code_regex = r"```(.*?)```"
    code_matches = re.findall(code_regex, text, re.DOTALL)
    print (f"Code extracted: {code_matches}")

    return code_matches

def Read_From_File(filepath:str) -> dict:
    '''
    This function reads file of types [.docx, .pdf, .pptx] or any plain text file, and returns the content of the file.

    Parameters
    ----------
    filepath : str
        The full file path to the file to be read 

    Returns
    -------
    ret : dict
        a dictionary containing the error code and the content of the file
    '''
    ret = {}
    ret['Error'] = 0

    if os.path.exists(filepath):
        try:
            if filepath.split(".")[-1] in ['docx', 'DOCX']:
                ret['Conent'] = get_docx_data(filepath)
                ret['Error'] = 0
            elif filepath.split(".")[-1] in ['pdf', 'PDF']:
                ret['Conent'] = get_pdf_data(filepath)
                ret['Error'] = 0
            elif filepath.split(".")[-1] in ['pptx', 'PPTX']:
                ret['Conent'] = get_ppt_data(filepath)
                ret['Error'] = 0
            else:
                ret['Conent'] = text_preprocessing(filepath)
                ret['Error'] = 0
        except Exception as ex:
            ret['Error'] = f"Failed to read file {filepath}: {ex}"
    else:
        ret['Error'] = f"{filepath} does not exist."

    return ret


def GetContexts(uploaded_file):

    Content = ""
    error = 0
    tempFile = ""
    filepath = uploaded_file.name
    try:
        if filepath.split(".")[-1] in ['docx', 'DOCX']:
            with NamedTemporaryFile(suffix="docx", delete=False) as temp:
                temp.write(uploaded_file.getbuffer())
                tempFile = temp.name
                Content = get_docx_data(temp.name)
        elif filepath.split(".")[-1] in ['pdf', 'PDF']:
            with NamedTemporaryFile(suffix="pdf", delete=False) as temp:
                temp.write(uploaded_file.getbuffer())
                tempFile = temp.name
                Content = get_pdf_data(temp.name)
        elif filepath.split(".")[-1] in ['pptx', 'PPTX', 'ppt']:
            with NamedTemporaryFile(suffix="pptx", delete=False) as temp:
                temp.write(uploaded_file.getbuffer())
                tempFile = temp.name
                Content = get_ppt_data(temp.name)
        elif filepath.split(".")[-1] in ['cpp', 'CPP']:
            with NamedTemporaryFile(suffix="cpp", delete=False) as temp:
                temp.write(uploaded_file.getbuffer())
                tempFile = temp.name
                Content = text_preprocessing(temp.name)
        elif filepath.split(".")[-1] in ['py']:
            with NamedTemporaryFile(suffix="py", delete=False) as temp:
                temp.write(uploaded_file.getbuffer())
                tempFile = temp.name
                Content = text_preprocessing(temp.name)
        else:
            with NamedTemporaryFile(suffix="txt", delete=False) as temp:
                temp.write(uploaded_file.getbuffer())
                tempFile = temp.name
                Content = text_preprocessing(temp.name)
    except Exception as ex:
        print(f"Loading file content failed: {ex}")
        Content = f"Loading file failed: {ex}"
        error = 1

    if os.path.exists(tempFile):
        try:
            os.remove(tempFile)
        except Exception as ex:
            pass

    return Content, error

def Search_WiKi(query: str) -> str:

    rets = ""
    # Search for the title related to query
    search_results = wikipedia.search(query, results=2)
    if search_results:
        result = {}
        result_title = search_results[0]
        print(f"Title related to {query}: {result_title}")
        rets += f"<Title>{result_title}</Title>:\n"

        # Get a summary of the article
        summary = wikipedia.summary(result_title, sentences=5)
        print(f"Summary:\n{summary}")
        rets += f"<Summary>{summary}</Summary>"
        rets += "\n\n"
    else:
        print(f"No relevant results found for: {query}.")

    return rets

#def Search_DuckDuckGo(query: str) -> str:

#    rets = ""
#    # Search for the title related to query
#    search_results = ddgs.text(query, max_results=5)
#    for result in search_results:
#        result_title = search_results['title']
#        print(f"Title related to {query}: {result['title']}")
#        rets += f"<Title>{result['title']}</Title>:\n"

#        print(f"URL:\n{result['url']}")
#        rets += f"<Summary>{result['body']}</Summary>"
#        rets += "\n\n"

#    return rets

def Search_DuckDuckGo(query: str) -> str:
    #duck_search = DuckDuckGoSearchRun()
    #duck_search = DuckDuckGoSearchResults(backend="news")
    duck_search = DuckDuckGoSearchResults()
    rets = duck_search.run(query)
    print(f"Search results: {rets}")

    return rets

#duck_search = DuckDuckGoSearchAPIWrapper()
#Web_Search = StructuredTool.from_function(
#        name="Current Search",
#        func=duck_search.run,
#        description="Useful when you need to answer questions about current events or the current state of the world."
#    )

#serp_search = SerpAPIWrapper()
#Web_Search = StructuredTool.from_function(name="Current Search",
#                   func=serp_search.run,
#                   description="Useful when you need to answer questions about current events or the current state of the world."
#                   )

#@st.cache_data()
#def get_remote_ip() -> str:
#    """Get remote ip."""

#    try:
#        ctx = get_script_run_ctx()
#        if ctx is None:
#            return None

#        session_info = runtime.get_instance().get_client(ctx.session_id)
#        if session_info is None:
#            return None
#    except Exception as e:
#        return None

#    return session_info.request.remote_ip
