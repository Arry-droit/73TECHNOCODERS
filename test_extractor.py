# test_extractor.py

from keyword_extract import extract_keywords

query = "How is the Indian stock market reacting to the recent global interest rate changes?"
keywords = extract_keywords(query)

print("Extracted Keywords:")
for kw in keywords:
    print("-", kw)
