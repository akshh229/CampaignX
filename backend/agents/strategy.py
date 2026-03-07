from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate

llm = ChatGroq(model="llama3-8b-8192", temperature=0.2)


def generate_strategy(parsed_brief: dict) -> str:
    prompt = ChatPromptTemplate.from_template("""
    Given this campaign brief data, generate a short campaign strategy (3-4 sentences):
    Product: {product_name}
    USP: {usp}
    Special Offers: {special_offers}
    Goal: {optimization_goal}

    Return a concise strategy paragraph.
    """)
    chain = prompt | llm
    result = chain.invoke({
        "product_name": parsed_brief.get("product_name", "XDeposit"),
        "usp": parsed_brief.get("usp", "Better returns"),
        "special_offers": parsed_brief.get("special_offers", "None"),
        "optimization_goal": parsed_brief.get("optimization_goal", "open rate and click rate"),
    })
    return result.content
