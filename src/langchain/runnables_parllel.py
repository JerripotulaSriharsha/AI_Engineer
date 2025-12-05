from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
from langchain_core.runnables import RunnableParallel
load_dotenv()

# # Define the prompt
prompt_template = "Write a poem about {topic}"
prompt = ChatPromptTemplate.from_template(prompt_template)

# Define the model and parser
model = ChatOpenAI(temperature=0.7, model="gpt-4o-mini")
output_parser = StrOutputParser()

# Create the poem chain
poem_chain = prompt | model | output_parser

# # Test the chain
# result = poem_chain.invoke({"topic": "coffee"})
# print(result)


prompt_template = "write a short story about {topic}"
prompt = ChatPromptTemplate.from_template(prompt_template)

story_chain = prompt | model | output_parser

# result = story_chain.invoke("a robot learning to love")

# print(result)

comparison_template = """
Whcih of these literary pieces is of better quality?
A poem:
{poem}

A short story:
{story}
"""
comparison_prompt = ChatPromptTemplate.from_template(comparison_template)
comparison_chain = comparison_prompt | model | output_parser
composed_chain = (
    RunnableParallel({
        "poem": poem_chain,
        "story": story_chain
    })
    | comparison_chain
)
result = composed_chain.invoke({"topic": "coffee"})

print(result)   