from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
import json

llm = ChatGroq(model="llama3-8b-8192", temperature=0.7)


def generate_content(parsed_brief: dict, variant: str = "A") -> dict:
    tone_map = {"A": "professional and formal", "B": "friendly and conversational"}
    tone = tone_map.get(variant, "professional")

    prompt = ChatPromptTemplate.from_template("""
    Create an email campaign for variant {variant} with {tone} tone.

    Product: {product_name}
    USP: {usp}
    Special Offers: {special_offers}
    CTA URL: {cta_url}

    Generate:
    1. subject: A compelling email subject line (max 60 chars, no emoji)
    2. body: Email body in HTML-style text (use **bold** for emphasis, include relevant emojis, end with CTA link)

    Rules:
    - Body must be in English only
    - Include the CTA URL naturally in the body
    - Mention special offers prominently if any
    - Keep body under 200 words

    Return ONLY valid JSON with keys: subject, body
    """)

    chain = prompt | llm
    result = chain.invoke({
        "variant": variant,
        "tone": tone,
        "product_name": parsed_brief.get("product_name", "XDeposit"),
        "usp": parsed_brief.get("usp", "Better returns"),
        "special_offers": parsed_brief.get("special_offers", "None"),
        "cta_url": parsed_brief.get("cta_url", "https://superbfsi.com/xdeposit/explore/"),
    })

    try:
        return json.loads(result.content)
    except Exception:
        return {
            "subject": f"Introducing {parsed_brief.get('product_name', 'XDeposit')} - Better Returns Await You",
            "body": (
                f"Dear Customer,\n\n"
                f"We are excited to introduce {parsed_brief.get('product_name', 'XDeposit')}! "
                f"{parsed_brief.get('usp', '')}\n\n"
                f"{parsed_brief.get('special_offers', '')}\n\n"
                f"Explore now: {parsed_brief.get('cta_url', '')}\n\n"
                f"Best regards,\nSuperBFSI Team"
            ),
        }
