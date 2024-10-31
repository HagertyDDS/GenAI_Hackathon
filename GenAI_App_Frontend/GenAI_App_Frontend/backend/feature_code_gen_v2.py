from operator import itemgetter
import pandas as pd
from langchain.pydantic_v1 import BaseModel, Field
from langchain.chat_models import ChatOpenAI  # Changed from ChatOllama to ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain.callbacks.manager import CallbackManager
from langchain_core.runnables import RunnableLambda
from langchain.callbacks.streaming_stdout_final_only import FinalStreamingStdOutCallbackHandler
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()




CODE_GEN_TEMPLATE = """

You will be creating a python function to generate a new feature, based on existing columns in a pandas dataframe.

To help you create this function, you will also be provided with the following: 
- The first 10 rows of the dataframe, to give you context on what each column contains. 
- The documentation of all the columns in the dataframe. This will provide you with the data type and description for each column. 

Based on the user request below describing the new feature, generate the function. 

User Request: {request}

The function should strictly follow these format specifications:
1. The function should be named {feature_name}.
2. The function should have 1 input parameter called DF. DF is a Pandas Dataframe. This is the dataframe you will use to create the new feature. 
3. The function should return a 1 column dataframe, containing the value of the new feature for each row in the source data dataframe. 
4. Only output raw, executable python code. Do not output any other leading or trailing text. 

Your code should follow these guidelines:
1. Be Performant
2. Handle Edge Cases Gracefully
3. Be robust 

Here are the first 10 rows of the dataframe: 
{table_sample}

Here is the documnetation for the columns in the dataframe: 
{documentation}
"""



# Create a prompt using PromptTemplate
CODE_GEN_PROMPT = PromptTemplate(
    template=CODE_GEN_TEMPLATE,
    input_variables=["feature_name", "request", "documentation", "table_sample"],
)

# Set up the coding expert model using OpenAI API
CODE_GEN_MODEL = ChatOpenAI(
    model="gpt-4o-mini",  # Specify the OpenAI model, e.g., "gpt-4" or "gpt-3.5-turbo"
    callback_manager=CallbackManager([FinalStreamingStdOutCallbackHandler()]),
    temperature=0,
)




CODE_GEN_CHAIN_V2 = (
    {
        "feature_name": itemgetter("feature_name"),
        "request": itemgetter("request"), 
        "documentation": itemgetter("documentation"),
        "table_sample": itemgetter("table_sample"),
    }
    | CODE_GEN_PROMPT
    | CODE_GEN_MODEL
)


# print("FINSIHED")




