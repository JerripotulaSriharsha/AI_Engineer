from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

load_dotenv()

# Define our function
def get_temperature(city):
    if city == "Paris":
        return 15
    if city == "London":
        return 10
    if city == "San Francisco":
        return 20
    return 25

def get_weather(city):
    if city == "Paris":
        return "cloudy"
    if city == "London":
        return "rainy"
    return "cloudy"

# Prompt template

prompt = ChatPromptTemplate.from_template(
    "What should I wear if the weather is {weather} and the temperature is {temperature} degrees Celsius?"
)

# Model
model = ChatOpenAI(temperature=0.7, model="gpt-4o-mini")

# Output parser
output_parser = StrOutputParser()

# ✅ Chain with RunnableLambda (not plain lambda)
chain = (prompt
    | model
    | output_parser)

composed_chain = (
    (lambda city: {
        "weather": get_weather(city),
        "temperature": get_temperature(city)
    })
    | chain
)
result = composed_chain.invoke("Paris")
print(result)

