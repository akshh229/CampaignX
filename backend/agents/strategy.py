from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-8b", temperature=0.2)


def generate_strategy(parsed_brief: dict) -> str:
    prompt = ChatPromptTemplate.from_template("""
    Given this campaign brief data, generate a short campaign strategy (3-4 sentences):
    Product: {product_name}
    USP: {usp}
    Special Offers: {special_offers}
    Goal: {optimization_goal}

    Return a concise strategy paragraph.
    """)
    try:
        chain = prompt | llm
        result = chain.invoke({
            "product_name": parsed_brief.get("product_name", "XDeposit"),
            "usp": parsed_brief.get("usp", "Better returns"),
            "special_offers": parsed_brief.get("special_offers", "None"),
            "optimization_goal": parsed_brief.get("optimization_goal", "open rate and click rate"),
        })
        return result.content
    except Exception:
        return (
            f"Split the live cohort into A/B segments for {parsed_brief.get('product_name', 'XDeposit')} "
            "and test professional versus friendly messaging. Prioritize stronger click-through while "
            "preserving open rate, highlight the core return advantage, and emphasize any eligible bonus offer. "
            "Schedule the first run for the next available slot and use report outcomes to regenerate the weaker variant."
        )
