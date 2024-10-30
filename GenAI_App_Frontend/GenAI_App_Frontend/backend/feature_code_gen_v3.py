from operator import itemgetter
import pandas as pd
from langchain.pydantic_v1 import BaseModel, Field
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout_final_only import FinalStreamingStdOutCallbackHandler
import os
from dotenv import load_dotenv
from openai import OpenAI  # Databricks API client setup

load_dotenv()

# Databricks token and endpoint
DATABRICKS_TOKEN = os.environ.get("DATABRICKS_TOKEN")
DATABRICKS_ENDPOINT = "https://dbc-bfc39191-ad8d.cloud.databricks.com/serving-endpoints"

# Initialize the Databricks OpenAI client
databricks_client = OpenAI(
    api_key=DATABRICKS_TOKEN,
    base_url=DATABRICKS_ENDPOINT
)

# Code generation template
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

Here is the documentation for the columns in the dataframe: 
{documentation}
"""

# Create a prompt using PromptTemplate
CODE_GEN_PROMPT = PromptTemplate(
    template=CODE_GEN_TEMPLATE,
    input_variables=["feature_name", "request", "documentation", "table_sample"],
)

# Define a function to make requests to Databricks' model endpoint
def call_databricks_model(prompt: str, model: str = "databricks-meta-llama-3-1-70b-instruct"):
    response = databricks_client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are an AI assistant"},
            {"role": "user", "content": prompt}
        ],
        model=model,
        max_tokens=256
    )
    return response.choices[0].message.content

# Define the chain with the Databricks call
class DatabricksCodeGenChain:
    def __init__(self, prompt_template, model="databricks-meta-llama-3-1-70b-instruct"):
        self.prompt_template = prompt_template
        self.model = model

    def invoke(self, inputs):
        prompt = self.prompt_template.format(**inputs)
        return call_databricks_model(prompt, self.model)

# Initialize the Databricks chain
CODE_GEN_CHAIN_V3 = DatabricksCodeGenChain(
    prompt_template=CODE_GEN_PROMPT,
    model="databricks-meta-llama-3-1-70b-instruct"
)

# Example of invoking the chain
# inputs = {
#     "feature_name": "example_feature",
#     "request": "Create a feature that calculates the age of a car from its year",
#     "documentation": "year: int, the year the car was manufactured",
#     "table_sample": "year\n2015\n2018\n2020\n2012\n2019"
# }

# Invoke the chain to generate code
# generated_code = CODE_GEN_CHAIN_V2.invoke(inputs)
# print("Generated code:\n", generated_code)
