# libraries 
import streamlit as st 
from langchain.document_loaders import WebBaseLoader 
from langchain.text_splitter import RecursiveCharacterTextSplitter 
from langchain.embeddings import HuggingFaceInferenceAPIEmbeddings 
from langchain.vectorstores import Chroma 
from langchain.llms import HuggingFaceHub 
from langchain.chains import RetrievalQA 
from dotenv import load_dotenv
import os 

load_dotenv()

class Rag_Model():
    def __init__(self):
        self.vector_db=None 
        self.embeddings=None
        self.qa=None
        self.model=  HuggingFaceHub(repo_id = 'HuggingFaceH4/zephyr-7b-alpha',
                model_kwargs ={
                    'temperature':0.5,
                    'max_new_tokens':512,
                    'max_length' : 54
                })

    def create_vector_db(self,urls):
        with st.spinner("loading urls..."):
            URLS =urls
            data = WebBaseLoader(URLS)
            content = data.load()
        # print(content)

        # text spliting and chunking  
        with st.spinner("Text Spliting and chunking : ..."):
            text_spliter= RecursiveCharacterTextSplitter(
            #separators=['\n\n','\n','.',','],
            chunk_size = 256,
            chunk_overlap = 50
            )
            chunks = text_spliter.split_documents(content)
            # print(chunks)

        with st.spinner("Vectors creating using embedding ..."):
            hf_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
            self.embeddings = HuggingFaceInferenceAPIEmbeddings(api_key=hf_token ,
                                            model_name="BAAI/bge-base-en-v1.5")
        with st.spinner("creating vector database and uploading data into db folder ..."):
            vectorstore = Chroma.from_documents(chunks,self.embeddings,persist_directory='db')

    def prompting(self,query):
        prompt =f"""
            <|system|>>
            you are an AI assistant that follows instruction extremely well.
            please be truthfull and give direct answers.please tell 'I DON'T KNOW' if user query not in context
            </s>
            <|user|>
            {query}
            </s>
            <|assistant|>
            return only Helpfull Answer
        """
        return prompt
    
    def compute(self):
        with st.spinner("Vectors creating using embedding ..."):
            hf_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
            self.embeddings = HuggingFaceInferenceAPIEmbeddings(api_key=hf_token ,
                                            model_name="BAAI/bge-base-en-v1.5")
        with st.spinner("using vector database and downloading data from db folder ..."):
            self.vector_db= Chroma(persist_directory='db',embedding_function=self.embeddings)
        with st.spinner("creating retriver to retrive data  from vector database ..."):
            # next we need to do the we retrival 
            retriever = self.vector_db.as_retriever(search_type= 'mmr',search_kwargs ={"k" : 3})
            # query = "what is system_design ?"
            # docs_rel = retriever.get_relevant_documents(query)
            # print(docs_rel)
        self.qa = RetrievalQA.from_chain_type(llm= self.model,retriever = retriever,chain_type = 'stuff')
        
    def retrive_ans(self,query):
        response = self.qa(self.prompting(query))
        return response['result']
def main():
    rag= Rag_Model()
    with st.popover("Lanuch"):
        n= st.number_input("enter no.of url and press enter ",value=0, placeholder = "Type a number...")
        if n<0:
            n=0 
        elif n>5:
            n=5

        urls=[0]*n
        for i in range(n):
            urls[i]=st.text_input(f"Enter url {i+1} : ")
        if st.button("Load data", type="secondary"):
            rag.create_vector_db(urls)
            

    st.title("ChatGPT ChatBot With Streamlit and OpenAI")
    if 'user_input' not in st.session_state:
        st.session_state['user_input'] = []
    
    if 'openai_response' not in st.session_state:
        st.session_state['openai_response'] = []
    
    def get_text():
        input_text = st.text_input("write here", key="input")
        return input_text
    
    user_input = get_text()
    
    if user_input:
        rag.compute()
        output = rag.retrive_ans(user_input)
        #output = output.lstrip("\n")
        
        st.write(output)
        # Store the output
        st.session_state.openai_response.append(user_input)
        st.session_state.user_input.append(output)

if __name__ == "main":
    main()      
        