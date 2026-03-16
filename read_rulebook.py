import pdfplumber
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with pdfplumber.open('f:\\CampaignX_RuleBook.pdf') as pdf:
    for page_num in range(3, len(pdf.pages)):
        print(f'\n{"="*70}')
        print(f'PAGE {page_num + 1}')
        print(f'{"="*70}\n')
        text = pdf.pages[page_num].extract_text()
        print(text)
        print()
