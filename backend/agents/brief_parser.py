from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
import json

llm = ChatGroq(model="llama3-8b-8192", temperature=0)


def parse_brief(brief: str) -> dict:
    prompt = ChatPromptTemplate.from_template("""
    Extract the following from this marketing campaign brief as JSON:
    - product_name: name of the product
    - usp: unique selling proposition
    - special_offers: any special offers (e.g., for female senior citizens)
    - optimization_goal: what to optimize (open rate, click rate)
    - include_inactive: boolean, whether to include inactive customers
    - cta_url: call to action URL if mentioned
    - tone: suggested email tone (professional/friendly/urgent)

    Brief: {brief}

    Return ONLY valid JSON, nothing else.
    """)
    chain = prompt | llm
    result = chain.invoke({"brief": brief})
    try:
        return json.loads(result.content)
    except Exception:
        return {
            "product_name": "XDeposit",
            "usp": brief,
            "tone": "professional",
            "include_inactive": True,
            "cta_url": "https://superbfsi.com/xdeposit/explore/",
        }
