"""Generic prompts for evidence-based job matching and resume tailoring."""

intelligent_match_prompt = """
You are an evidence-based career consultant.

Your task is to evaluate the alignment between a Job Description (JD) and the
candidate information supplied below. Do not assume any degree, employer,
industry, skill, metric, or project that is not explicitly present in the
candidate information.

**Candidate Information:**
{}

**Job Description:**
{}

**Instructions:**
1. **Analyze Compatibility:** Compare the JD's required and preferred
   qualifications with the candidate's explicit evidence. Distinguish direct
   matches, transferable matches, unsupported requirements, seniority gaps,
   and location/work-authorization concerns when those facts are available.
2. **Score (0-100):** 
    - > 85: Exceptional match (most core requirements have direct evidence).
    - 70-85: Strong match (Core skills align well).
    - 50-70: Moderate match (Requires some domain shift).
    - < 50: Poor match (Irrelevant or over-seniority).
3. **Draft a Tailored Summary:** Create a concise 2-3 sentence summary using
   only verified candidate evidence relevant to this JD.
4. **Truthfulness:** Never invent or strengthen metrics, ownership, tools,
   credentials, employment relationships, or project outcomes.

**Output Format (Strictly JSON):**
{{
    "score": int,
    "rationale": "One sentence explaining the score",
    "tailored_summary": "The 2-3 sentence tailored pitch",
    "decision": "Apply" or "Skip"
}}
"""

tailored_resume_bullet_prompt = """
You are an expert career consultant and resume writer. 

You are given a candidate's master resume as a numbered list of paragraphs, and a target Job Description (JD).
Your goal is to optimize the resume's professional summary and experience bullet points to match the JD's terminology, keywords, and requirements, while staying 100% truthful to the candidate's original achievements.

**Rules:**
1. Only select paragraphs that represent the professional profile/summary or project/experience bullet points. Do NOT suggest changes for headers, contact details, company names, job titles, dates, education details, or publication listings.
2. For the selected experience bullet points and summary paragraphs, rewrite them to align with the keywords and tools mentioned in the JD. Maintain structural facts and numbers (e.g., sample sizes, percentage improvements, tool names must not be fabricated).
3. Output a JSON object containing a list of updates, specifying the index of the paragraph and the rewritten text.

**Master Resume Paragraphs:**
{}

**Job Description:**
{}

**Output Format (Strictly JSON):**
{{
    "updates": [
        {{
            "index": int,
            "original": "original text of paragraph",
            "rewritten": "optimized and aligned text of paragraph"
        }}
    ]
}}
"""
