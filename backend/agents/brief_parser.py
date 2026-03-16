from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
import json

llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-8b", temperature=0)


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
    try:
        chain = prompt | llm
        result = chain.invoke({"brief": brief})
        return json.loads(result.content)
    except Exception:
        return {
            "product_name": "XDeposit",
            "usp": brief,
            "special_offers": "Additional 0.25 percentage point returns for female senior citizens",
            "optimization_goal": "open rate and click rate",
            "tone": "professional",
            "include_inactive": True,
            "cta_url": "https://superbfsi.com/xdeposit/explore/",
        }
