import json
import re
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv(Path(__file__).resolve().parents[1] / ".env", override=False)


def _get_llm() -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(model="gemini-1.5-flash-8b", temperature=0.7)


def _parse_json_payload(content: str) -> dict:
    content = (content or "").strip()
    if not content:
        raise ValueError("Empty model response")

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        pass

    fenced_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", content, re.DOTALL)
    if fenced_match:
        return json.loads(fenced_match.group(1))

    object_match = re.search(r"(\{.*\})", content, re.DOTALL)
    if object_match:
        return json.loads(object_match.group(1))

    raise ValueError("No valid JSON object found in model response")


def _fallback_content(parsed_brief: dict, variant: str, feedback: str = None) -> dict:
    product_name = parsed_brief.get("product_name", "XDeposit")
    usp = parsed_brief.get("usp", "Better returns")
    special_offers = parsed_brief.get("special_offers", "")
    cta_url = parsed_brief.get("cta_url", "https://superbfsi.com/xdeposit/explore/")
    feedback_line = f"\n\nWe also revised this version to address: {feedback}" if feedback else ""

    if variant == "A":
        return {
            "subject": f"Secure Higher Returns With {product_name}",
            "body": (
                f"Dear Customer,\n\n"
                f"{product_name} is designed for customers seeking dependable growth with clear value. "
                f"It {usp}.\n\n"
                f"Key benefit: {special_offers or 'Competitive term-deposit returns tailored to your goals.'}\n\n"
                f"If you are reviewing deposit options, this is a strong opportunity to lock in higher returns with a trusted institution."
                f"{feedback_line}\n\n"
                f"Explore the product and next steps here: {cta_url}\n\n"
                f"Regards,\nSuperBFSI Team"
            ),
        }

    return {
        "subject": f"Meet {product_name}: Better Returns, Less Guesswork",
        "body": (
            f"Hi there,\n\n"
            f"Looking for a smarter place to grow your savings? {product_name} is here to help. "
            f"It {usp}.\n\n"
            f"And there is more: {special_offers or 'You get a simple, high-value way to make your money work harder.'}\n\n"
            f"We kept this version simple so you can quickly see the upside and decide if it fits your plans."
            f"{feedback_line}\n\n"
            f"Take a look here: {cta_url}\n\n"
            f"Cheers,\nSuperBFSI Team"
        ),
    }


def generate_content(parsed_brief: dict, variant: str = "A", feedback: str = None) -> dict:
    tone_map = {"A": "professional and formal", "B": "friendly and conversational"}
    tone = tone_map.get(variant, "professional")
    
    feedback_str = f"PREVIOUS FEEDBACK TO INCORPORATE: {feedback}" if feedback else ""

    prompt = ChatPromptTemplate.from_template("""
    Create an email campaign for variant {variant} with {tone} tone.

    Variant-specific requirements:
    - Variant A: sound polished, authoritative, and benefit-led for a risk-aware banking customer.
    - Variant B: sound warm, approachable, and easy to skim for a casual retail customer.
    - The two variants must not reuse the same opening sentence or CTA sentence.

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
        chain = prompt | _get_llm()
        result = chain.invoke({
            "variant": variant,
            "tone": tone,
            "product_name": parsed_brief.get("product_name", "XDeposit"),
            "usp": parsed_brief.get("usp", "Better returns"),
            "special_offers": parsed_brief.get("special_offers", "None"),
            "cta_url": parsed_brief.get("cta_url", "https://superbfsi.com/xdeposit/explore/"),
            "feedback_str": feedback_str
        })
        payload = _parse_json_payload(result.content)
        subject = str(payload.get("subject", "")).strip()
        body = str(payload.get("body", "")).strip()
        if not subject or not body:
            raise ValueError("Model response missing subject or body")
        return {"subject": subject, "body": body}
    except Exception:
        return _fallback_content(parsed_brief, variant, feedback)
