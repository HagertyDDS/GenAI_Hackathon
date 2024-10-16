import warnings
from operator import itemgetter

warnings.filterwarnings("ignore")
import langchain_core
from pprint import pprint
from langchain.pydantic_v1 import BaseModel, Field
from langchain_core.output_parsers import JsonOutputParser

from langchain_community.document_loaders.generic import GenericLoader
from langchain_community.document_loaders.parsers import LanguageParser
from langchain_text_splitters import Language
from langchain_community.chat_models import ChatOllama
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.callbacks.manager import CallbackManager
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain.callbacks.streaming_stdout_final_only import FinalStreamingStdOutCallbackHandler, StreamingStdOutCallbackHandler
from langchain.schema.runnable.config import RunnableConfig

LOADER = GenericLoader.from_filesystem(
    "./auto_generated_code.py",
    glob="*",
    suffixes=[".py"],
    parser=LanguageParser(),
)

# Load in function by function
DOCS = LOADER.load()

# Only keep actual function definitions, no need for `simplified_code`
DOCS = [doc for doc in DOCS if doc.metadata["content_type"] == "functions_classes"]


CODE_CLEANUP_TEMPLATE = """
You will be given python functions here: ```{python_func}```

Additionally you will be given a set of other functions here: ```{other_funcs}```

Identify if the first function does the same thing as any of the other functions. If so, output `is_duplicate=True` and `func_name= <name of whichever function you think is better>`
{format_instructions}
"""

class DuplicateCodeFilter(BaseModel):
    is_duplicate: bool = Field(description="boolean indicating `True` if function is a duplicate of another, `False` if not")
    func_name: str = Field(description="If `is_duplicate=False`, output the name of the first python function given. If `is_duplicate=True`, output the name of whichever function is better implemented")
CODE_GEN_OUTPUT_PARSER = JsonOutputParser(pydantic_object=DuplicateCodeFilter)


# Convert to a prompt so we can use this in an LCEL compliant chain
CODE_GEN_PROMPT = PromptTemplate(
    template=CODE_CLEANUP_TEMPLATE,
    input_variables=["python_func", "other_funcs"],
    partial_variables={"format_instructions": CODE_GEN_OUTPUT_PARSER.get_format_instructions()},
)


# Set up our coding expert model
CODE_GEN_MODEL = ChatOllama(
    model="deepseek-coder-v2", 
    callback_manager=CallbackManager([FinalStreamingStdOutCallbackHandler()]),
    temperature = 0,
)

CODE_GEN_CHAIN = (
    {
        "python_func": itemgetter("python_func"), 
        "other_funcs": itemgetter("other_funcs")
    }
    | CODE_GEN_PROMPT
    | CODE_GEN_MODEL
    | CODE_GEN_OUTPUT_PARSER 
)

if __name__ == "__main__":
    outputs = []
    from copy import deepcopy
    for i in range(len(DOCS)):
        try:
            copy_of_docs = deepcopy(DOCS)
            del copy_of_docs[i]
            outputs.append(CODE_GEN_CHAIN.invoke({
                "python_func": DOCS[i],
                "other_funcs": copy_of_docs
            }))
        except langchain_core.exceptions.OutputParserException:
            pass

    from pprint import pprint
    pprint(outputs)
