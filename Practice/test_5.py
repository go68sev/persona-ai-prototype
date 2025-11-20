"""
=== Exercise: Prompt Engineering with Extraction ===

Purpose:
  Learn how to extract structured information from unstructured text using LLM.

Techniques covered:
  1. Basic Extraction - Extract simple information
  2. Structured Extraction - Extract into JSON format
  3. Multi-field Extraction - Extract multiple pieces of information
  4. Conditional Extraction - Extract based on conditions

How to experiment:
  - Modify extraction prompts to get different fields
  - Change output formats (JSON, list, table)
  - Add more complex text samples
  - Test edge cases and incomplete information
  - Combine extraction with role assignment
"""

from openai import OpenAI

client = OpenAI()


# ============================================================================
# Technique 1: Basic Extraction
# ============================================================================
print("1. BASIC EXTRACTION - Extract simple information\n")

sample_text_1 = """
John Smith is a 28-year-old software engineer living in San Francisco.
He works at Google and has been there for 3 years.
His email is john.smith@email.com and phone is 555-1234.
"""

print("Text to extract from:")
print(sample_text_1)
print("-" * 50)

completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {
            "role": "system",
            "content": "Extract key information from the text. Be concise."
        },
        {
            "role": "user",
            "content": f"Extract name, age, job title, and company from this text:\n\n{sample_text_1}"
        }
    ]
)

print(completion.choices[0].message.content)
print("\n")

# ============================================================================
# Technique 2: Structured Extraction (JSON Format)
# ============================================================================
print("2. STRUCTURED EXTRACTION - Extract into JSON format\n")

sample_text_2 = """
Emma Johnson is a 35-year-old marketing manager at Apple Inc.
She has worked there for 5 years. Her contact details are
emma.johnson@apple.com and +1-555-9876. She specializes in digital marketing.
"""

print("Text to extract from:")
print(sample_text_2)
print("-" * 50)

completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {
            "role": "system",
            "content": "You are a JSON extraction assistant. Always respond with valid JSON only."
        },
        {
            "role": "user",
            "content": "Extract name, age, company, years_of_experience, email, phone, and specialization. Respond in JSON format."
        },
        {
            "role": "assistant",
            "content": '{"name": "Emma Johnson", "age": 35, "company": "Apple Inc", "years_of_experience": 5, "email": "emma.johnson@apple.com", "phone": "+1-555-9876", "specialization": "digital marketing"}'
        },
        {
            "role": "user",
            "content": f"Extract from this text:\n\n{sample_text_2}"
        }
    ]
)

print(completion.choices[0].message.content)
print("\n")

# ============================================================================
# Technique 3: Multi-field Extraction from Complex Text
# ============================================================================
print("3. MULTI-FIELD EXTRACTION - Extract multiple pieces from longer text\n")

sample_text_3 = """
Product Review: Samsung Galaxy S24

Rating: 4.5 out of 5 stars
Price: $999
Release Date: January 29, 2024
Screen Size: 6.2 inches
Storage: 256GB
Camera: 50MP main sensor
Battery: 4000mAh
Operating System: Android 14

Review Summary: This flagship phone delivers excellent performance and
a stunning display. Battery life is solid, though slightly below expectations.
Camera quality is outstanding for both day and night photography.
Highly recommended for users seeking a premium Android experience.
"""

print("Text to extract from:")
print(sample_text_3)
print("-" * 50)

completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {
            "role": "system",
            "content": "You are a product information extractor. Extract all technical specifications and return as JSON."
        },
        {
            "role": "user",
            "content": f"Extract product name, rating, price, release_date, screen_size, storage, camera, battery, os, and key_pros from this review:\n\n{sample_text_3}"
        }
    ]
)

print(completion.choices[0].message.content)
print("\n")

# ============================================================================
# Technique 4: Conditional Extraction
# ============================================================================
print("4. CONDITIONAL EXTRACTION - Extract based on specific conditions\n")

sample_text_4 = """
Meeting Notes - Q4 Planning Session
Date: November 15, 2024
Attendees: Sarah (CEO), Mike (CTO), Lisa (CFO), David (VP Sales)

Topics Discussed:
1. Q4 Revenue Target: $5M
2. New Product Launch: AI Assistant (January 2025)
3. Team Expansion: Hiring 20 engineers
4. Budget Cuts: Reduce marketing spend by 15%
5. Customer Retention: Improve support response time to 2 hours

Decisions Made:
- Approved AI Assistant project
- Approved engineering hiring plan
- Deferred budget cuts until Q1 2025
"""

print("Text to extract from:")
print(sample_text_4)
print("-" * 50)

completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {
            "role": "system",
            "content": "You are a meeting notes extractor. Extract only approved decisions and financial targets."
        },
        {
            "role": "user",
            "content": f"Extract all approved decisions and financial/revenue targets from these meeting notes:\n\n{sample_text_4}"
        }
    ]
)

print(completion.choices[0].message.content)
print("\n")

# ============================================================================
# Technique 5: List-based Extraction
# ============================================================================
print("5. LIST-BASED EXTRACTION - Extract into structured lists\n")

sample_text_5 = """
Company: TechCorp Inc
Founded: 2015
Employees: 500
Offices: New York, San Francisco, London, Tokyo
Services: Cloud Solutions, AI Tools, Data Analytics, Consulting
Recent Clients: Google, Amazon, Microsoft, Netflix, Spotify
Awards: Best AI Company 2023, Innovation Leader 2024
"""

print("Text to extract from:")
print(sample_text_5)
print("-" * 50)

completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {
            "role": "system",
            "content": "You are a company information extractor. Return extracted data in clear, organized lists."
        },
        {
            "role": "user",
            "content": f"Extract company name, founding year, employee count, all office locations, all services, all recent clients, and all awards:\n\n{sample_text_5}"
        }
    ]
)

print(completion.choices[0].message.content)
print("\n")
