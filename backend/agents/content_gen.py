from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
import json

llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-8b", temperature=0.7)


def generate_content(parsed_brief: dict, variant: str = "A", feedback: str = None) -> dict:
    tone_map = {"A": "professional and formal", "B": "friendly and conversational"}
    tone = tone_map.get(variant, "professional")
    
    feedback_str = f"PREVIOUS FEEDBACK TO INCORPORATE: {feedback}" if feedback else ""

    prompt = ChatPromptTemplate.from_template("""
    Create an email campaign for variant {variant} with {tone} tone.

    Product: {product_name}
    USP: {usp}
    Special Offers: {special_offers}
    CTA URL: {cta_url}
    
    {feedback_str}

    Generate:
    1. subject: A compelling email subject line (max 60 chars, no emoji)        
    2. body: Email body in HTML-style text (use **bold** for emphasis, include relevant emojis, end with CTA link)

    Rules:
    - Body must be in English only
    - Include the CTA URL naturally in the body
    - Mention special offers prominently if any
    - Keep body under 200 words
    - If PREVIOUS FEEDBACK is provided, heavily adapt your generation to address those complaints.

    Return ONLY valid JSON with keys: subject, body
    """)

    try:
        chain = prompt | llm
        result = chain.invoke({
            "variant": variant,
            "tone": tone,
            "product_name": parsed_brief.get("product_name", "XDeposit"),
            "usp": parsed_brief.get("usp", "Better returns"),
            "special_offers": parsed_brief.get("special_offers", "None"),
            "cta_url": parsed_brief.get("cta_url", "https://superbfsi.com/xdeposit/explore/"),
            "feedback_str": feedback_str
        })
        return json.loads(result.content)
    except Exception:
        tone_descriptor = "Professional" if variant == "A" else "Friendly"
        return {
            "subject": f"[{tone_descriptor}] Introducing {parsed_brief.get('product_name', 'XDeposit')} - Better Returns Await You",
            "body": (
                f"Dear Customer,\n\n"
                f"We are excited to introduce {parsed_brief.get('product_name', 'XDeposit')}! "
                f"{parsed_brief.get('usp', '')}\n\n"
                f"{parsed_brief.get('special_offers', '')}\n\n"
                f"This message was generated using a {tone_descriptor.lower()} tone to suit your preferences.\n\n"
                f"Explore now: {parsed_brief.get('cta_url', '')}\n\n"
                f"Best regards,\nSuperBFSI Team"
            ),
        }
