"""
Ultimate goal is end to end pipeline that:

1. Takes in what the user is asking for a function of
1a.  Augments with column information from the DB
2. Generates that with a dedicated coding model
3. Adds said code to the repo & provides OAS description for...
4. Function calling model is able to take inputs and create new features using said function
"""
from operator import itemgetter

from langchain.pydantic_v1 import BaseModel, Field
from langchain.chat_models import ChatOllama
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain.callbacks.manager import CallbackManager
from langchain_core.runnables import RunnableLambda
from langchain.callbacks.streaming_stdout_final_only import FinalStreamingStdOutCallbackHandler

from postgres_load_data import get_all_table_comments

# TODO: Refine inputs and outputs to be consistent
# Set up our prompt for the code generation pipeline
CODE_GEN_TEMPLATE = """
Provide valid, expert-level, python code to perform the following user request:
User Request: {request}

Your code should follow these guidelines:
1. Be Performant
2. Handle Edge Cases Gracefully
3. Be Secure
4. Be fully documented as an OpenAPI Specification (OAS)

The corresponding documentation for the columns included as part of this user request may be found here:
Documentation: {documentation}

Finally, your output should be valid JSON with two keys: `code` and `OAS`. The values of these should be the raw python code and the OpenAPI Specification of said code, respectively. Provide only these two things, no other commentary or text.
{format_instructions}
"""

# TODO: Look into other output parsers like the DF parser that may be able to automate calling for us
# Set up output parsing so our model gives us both the code we need to execute and the OAS spec that our downstream model will need to call said functions
class OutputCode(BaseModel):
    code: str = Field(description="raw, executable, python code that accomplishes the user requested task")
    OAS: str = Field(description="OpenAPI Specification of said function (e.g.) {\"type\": \"function\", \"function\": {\"name\": \"get_current_weather\", \"description\": \"Get the current weather\", \"parameters\": {\"type\": \"object\", \"properties\": {\"location\": {\"type\": \"string\", \"description\": \"The city and state, e.g. San Francisco, CA\"}, \"format\": {\"type\": \"string\", \"enum\": [\"celsius\", \"fahrenheit\"], \"description\": \"The temperature unit to use. Infer this from the users location.\"}}, \"required\": [\"location\", \"format\"]}}}")
CODE_GEN_OUTPUT_PARSER = JsonOutputParser(pydantic_object=OutputCode)

# Convert to a prompt so we can use this in an LCEL compliant chain
CODE_GEN_PROMPT = PromptTemplate(
    template=CODE_GEN_TEMPLATE,
    input_variables=["request", "documentation"],
    partial_variables={"format_instructions": CODE_GEN_OUTPUT_PARSER.get_format_instructions()},
)


# Set up our coding expert model
CODE_GEN_MODEL = ChatOllama(
    model="deepseek-coder-v2", 
    callback_manager=CallbackManager([FinalStreamingStdOutCallbackHandler()]),
    temperature = 0,
)

# Quick and dirty function to get column documentation from Postgres
ALL_DOCS = get_all_table_comments()
def _get_documentation(all_docs, column_name, table_name="car_sale_regression"):
    # TODO: Make this work for multiple columns and tables
    return all_docs[((all_docs["table_name"] == table_name) & (all_docs["column_name"] == column_name))].get("description").item()
def get_documentation(_dict):
    return _get_documentation(_dict["docs"], _dict["column_name"])

# Pipeline it all together!
# TODO: Currently hardcoded for column of interst
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

if __name__ == "__main__":
    from pprint import pprint

    # Record oriented set of columns and requests
    requests = [
        ("clean_title", "Give me a function that takes the `clean_title` column from my dataframe and transforms it into a boolean"),
        ("engine", """Give me a function that takes the `engine` column and outputs the following new columns: `horsepower`, `displacement`, `num_cylinders`. If you can't identify a value for each column, output a null. The expected values for our columns in this example are as follows: `horsepower` = `172`, `displacement` = `1.6`, `num_cylinders` = `4`""")
    ]
    for col, req in requests:
        output = CODE_GEN_CHAIN.invoke({
            "docs": ALL_DOCS,
            "col": col, 
            "request": req
        })
        pprint(output)

        # TODO: Append code output var to some file `auto_generated_functions.py`
        if "code" in output:
            with open("./auto_generated_code.py", "a") as f:
                f.write("\n")
                f.write(output["code"])
            print("wrote output")

    # TODO: Setup pipeline using NEMO to call functions
    # https://docs.mistral.ai/capabilities/function_calling/

