# """
# Ultimate goal is end to end pipeline that:

# 1. Takes in what the user is asking for a function of
# 1a.  Augments with column information from the DB
# 2. Generates that with a dedicated coding model
# 3. Adds said code to the repo & provides OAS description for...
# 4. Function calling model is able to take inputs and create new features using said function
# """
# from operator import itemgetter
# import pandas as pd 

# from langchain.pydantic_v1 import BaseModel, Field
# from langchain.chat_models import ChatOllama
# from langchain.prompts import PromptTemplate
# from langchain_core.output_parsers import JsonOutputParser
# from langchain.callbacks.manager import CallbackManager
# from langchain_core.runnables import RunnableLambda
# from langchain.callbacks.streaming_stdout_final_only import FinalStreamingStdOutCallbackHandler

# # from postgres_load_data import get_all_table_comments

# # TODO: Refine inputs and outputs to be consistent
# # Set up our prompt for the code generation pipeline
# CODE_GEN_TEMPLATE = """
# Provide valid, expert-level, python code to perform the following user request:
# User Request: {request}

# Your code should follow these guidelines:
# 1. Be Performant
# 2. Handle Edge Cases Gracefully
# 3. Be Secure
# 4. Be fully documented as an OpenAPI Specification (OAS)

# The corresponding documentation for the columns included as part of this user request may be found here:
# Documentation: {documentation}

# Finally, your output should be valid JSON with two keys: `code` and `OAS`. The values of these should be the raw python code and the OpenAPI Specification of said code, respectively. Provide only these two things, no other commentary or text.
# {format_instructions}
# """

# # TODO: Look into other output parsers like the DF parser that may be able to automate calling for us
# # Set up output parsing so our model gives us both the code we need to execute and the OAS spec that our downstream model will need to call said functions
# class OutputCode(BaseModel):
#     code: str = Field(description="raw, executable, python code that accomplishes the user requested task")
#     OAS: str = Field(description="OpenAPI Specification of said function (e.g.) {\"type\": \"function\", \"function\": {\"name\": \"get_current_weather\", \"description\": \"Get the current weather\", \"parameters\": {\"type\": \"object\", \"properties\": {\"location\": {\"type\": \"string\", \"description\": \"The city and state, e.g. San Francisco, CA\"}, \"format\": {\"type\": \"string\", \"enum\": [\"celsius\", \"fahrenheit\"], \"description\": \"The temperature unit to use. Infer this from the users location.\"}}, \"required\": [\"location\", \"format\"]}}}")
# CODE_GEN_OUTPUT_PARSER = JsonOutputParser(pydantic_object=OutputCode)

# # Convert to a prompt so we can use this in an LCEL compliant chain
# CODE_GEN_PROMPT = PromptTemplate(
#     template=CODE_GEN_TEMPLATE,
#     input_variables=["request", "documentation"],
#     partial_variables={"format_instructions": CODE_GEN_OUTPUT_PARSER.get_format_instructions()},
# )


# # Set up our coding expert model
# CODE_GEN_MODEL = ChatOllama(
#     model="deepseek-coder-v2", 
#     callback_manager=CallbackManager([FinalStreamingStdOutCallbackHandler()]),
#     temperature = 0,
# )

# # Quick and dirty function to get column documentation from Postgres
# # ALL_DOCS = get_all_table_comments()
# ALL_DOCS = pd.read_csv('/Users/johannwest/Documents/Projects/GenAI_Hackathon/GenAI_App_Frontend/csvs/all_docs.csv')
# def _get_documentation(all_docs, column_name, table_name="car_sale_regression"):
#     # TODO: Make this work for multiple columns and tables
#     return all_docs[((all_docs["table_name"] == table_name) & (all_docs["column_name"] == column_name))].get("description").item()
# def get_documentation(_dict):
#     return _get_documentation(_dict["docs"], _dict["column_name"])

# # Pipeline it all together!
# # TODO: Currently hardcoded for column of interest
# CODE_GEN_CHAIN = (
#     {
#         "request": itemgetter("request"), 
#         "documentation": {
#             "docs": itemgetter("docs"), "column_name": itemgetter("col")
#             } | RunnableLambda(get_documentation)
#     }
#     | CODE_GEN_PROMPT
#     | CODE_GEN_MODEL
#     | CODE_GEN_OUTPUT_PARSER
# )



# print("FINSIHED ")








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
load_dotenv()

# Ensure you set your OpenAI API key in the environment variable
# or you can pass it directly into ChatOpenAI via the api_key parameter
# os.environ["OPENAI_API_KEY"] 


# Set up the prompt for the code generation pipeline
# CODE_GEN_TEMPLATE = """
# You will be creating a function that should generate a column of data for a feature set that will be used to train a machine learning model. 

# Based on the user request below describing a new feature, create a function that takes in the source data dataframe, performs the necessary operations, and outputs 
# a single column dataframe containing the value of the new feature for each row in the source data dataframe.
# Provide valid, expert-level, python code.

# User Request: {request}

# The function should strictly follow these format specifications:
# 1. The function should have a descriptive name.
# 2. There should a single input paramter called DF. DF is a Pandas Dataframe. This dataframe is the source data that your features will be created from. 
# 2. The output should be a single column dataframe, containing the value of the new feature for each row in the source data dataframe. 

# Your code should follow these guidelines:
# 1. Be Performant
# 2. Handle Edge Cases Gracefully
# 3. Be Secure
# 4. Be fully documented as an OpenAPI Specification (OAS)

# The corresponding documentation for the columns included as part of this user request may be found here:
# Documentation: {documentation}

# Finally, your output should be valid JSON with two keys: `code` and `OAS`. The values of these should be the raw python code and the OpenAPI Specification of said code, respectively. Provide only these two things, no other commentary or text.
# {format_instructions}
# """



# CODE_GEN_TEMPLATE = """
# You will be creating a function that should generate a column of data for a feature set that will be used to train a machine learning model. 

# Based on the user request below describing a new feature, create a function that takes in the source data dataframe, performs the necessary operations, and outputs 
# a single column dataframe containing the value of the new feature for each row in the source data dataframe.
# Provide valid, expert-level, python code.

# User Request: {request}

# The function should strictly follow these format specifications:
# 1. The function should have a descriptive name.
# 2. There should be a single input parameter called DF. DF is a Pandas Dataframe. This dataframe is the source data that your features will be created from. 
# 3. The output should be a single column dataframe, containing the value of the new feature for each row in the source data dataframe. 

# Your code should follow these guidelines:
# 1. Be Performant
# 2. Handle Edge Cases Gracefully
# 3. Be Secure
# 4. Be fully documented as an OpenAPI Specification (OAS)

# **The corresponding documentation for the columns included as part of this user request may be found here:**
# Documentation: {documentation}

# Finally, your output should be valid JSON with two keys: `code` and `OAS`. The values of these should be the raw python code and the OpenAPI Specification of said code, respectively. **Provide only these two things, no other commentary, no markdown, and no text explanations.**
# {format_instructions}
# """


CODE_GEN_TEMPLATE = """
You will be creating a function that should generate a column of data for a feature set that will be used to train a machine learning model. 

Based on the user request below describing a new feature, create a function that takes in the source data dataframe, performs the necessary operations, and outputs 
a single column dataframe containing the value of the new feature for each row in the source data dataframe.
Provide valid, expert-level, python code.

----

You will be creating a python function to generate a new feature, based on existing features in a pandas dataframe.

To help you create this function, you will be provided with the following: 
- The first 10 rows of the dataframe, to give you context on what each column contains. 
- The documentation of all the columns in the dataframe in the form.

Based on the user request below describing the new feature, generate the function. 

User Request: {request}

The function should strictly follow these format specifications:
1. The function should be named {column_name}.
2. There should be a single input parameter called DF. DF is a Pandas Dataframe. This dataframe is the source data that your features will be created from. 
3. The output should be a single column dataframe, containing the value of the new feature for each row in the source data dataframe. 

Your code should follow these guidelines:
1. Be Performant
2. Handle Edge Cases Gracefully
3. Be Secure
4. Be fully documented as an OpenAPI Specification (OAS)

**The corresponding documentation for the columns included as part of this user request may be found here:**
Documentation: {documentation}

Finally, your output should be valid JSON with two keys: `code` and `OAS`. The values of these should be the raw python code and the OpenAPI Specification of said code, respectively. **Provide only these two things, no other commentary, no markdown, and no text explanations.**
{format_instructions}
"""


# Define output parsing structure
class OutputCode(BaseModel):
    code: str = Field(description="raw, executable, python code that accomplishes the user requested task")
    OAS: str = Field(description="OpenAPI Specification of said function (e.g.) {\"type\": \"function\", \"function\": {\"name\": \"get_current_weather\", \"description\": \"Get the current weather\", \"parameters\": {\"type\": \"object\", \"properties\": {\"location\": {\"type\": \"string\", \"description\": \"The city and state, e.g. San Francisco, CA\"}, \"format\": {\"type\": \"string\", \"enum\": [\"celsius\", \"fahrenheit\"], \"description\": \"The temperature unit to use. Infer this from the users location.\"}}, \"required\": [\"location\", \"format\"]}}}")
CODE_GEN_OUTPUT_PARSER = JsonOutputParser(pydantic_object=OutputCode)

# Create a prompt using PromptTemplate
CODE_GEN_PROMPT = PromptTemplate(
    template=CODE_GEN_TEMPLATE,
    input_variables=["request", "documentation"],
    partial_variables={"format_instructions": CODE_GEN_OUTPUT_PARSER.get_format_instructions()},
)

# Set up the coding expert model using OpenAI API
CODE_GEN_MODEL = ChatOpenAI(
    model="gpt-4",  # Specify the OpenAI model, e.g., "gpt-4" or "gpt-3.5-turbo"
    callback_manager=CallbackManager([FinalStreamingStdOutCallbackHandler()]),
    temperature=0,
)

# Load documentation CSV (hardcoded path in this example)
#ALL_DOCS = pd.read_csv('/Users/johannwest/Documents/Projects/GenAI_Hackathon/GenAI_App_Frontend/csvs/all_docs.csv')

# ALL_DOCS = pd.read_csv('train_docs_text.txt')

#Helper function to get column documentation from a DataFrame
def _get_documentation(all_docs, column_name, table_name="car_sale_regression"):
    # TODO: Make this work for multiple columns and tables
    return all_docs[((all_docs["table_name"] == table_name) & (all_docs["column_name"] == column_name))].get("description").item()

def get_documentation(_dict):
    return _get_documentation(_dict["docs"], _dict["column_name"])


# Define the pipeline using the LangChain chain operators
CODE_GEN_CHAIN = (
    {
        "request": itemgetter("request"), 
        "documentation": {
            "docs": itemgetter("docs"), "column_name": itemgetter("col")
            } | RunnableLambda(get_documentation)
    }
    | CODE_GEN_PROMPT
    | CODE_GEN_MODEL
    | CODE_GEN_OUTPUT_PARSER
)

print("FINSIHED")
