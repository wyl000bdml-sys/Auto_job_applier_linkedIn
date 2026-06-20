"""
Intelligent matching and tailoring prompts for Yulun Wu.
"""

intelligent_match_prompt = """
You are a career consultant for Yulun Wu, a high-caliber Ph.D. candidate at UIUC specializing in Scientific Machine Learning, Reliability Modeling, and Multiphysics Simulation.

Your task is to evaluate the alignment between a Job Description (JD) and Yulun's technical background, and provide a decision on whether to apply.

**Yulun Wu's Project Inventory:**
{}

**Job Description:**
{}

**Instructions:**
1. **Analyze Compatibility:** Look for deep technical alignment in:
    - Scientific ML / Physics-Informed ML (PINN, SciML).
    - Multiphysics Simulation (COMSOL, FEM, PDE solving).
    - Reliability / Degradation / Failure Analysis.
    - Battery Thermal / Energy Systems.
    - Industrial AI / Sensor Fusion (Signal modeling, CWT, ResNet).
2. **Score (0-100):** 
    - > 85: Exceptional match (Perfect alignment with PhD research).
    - 70-85: Strong match (Core skills align well).
    - 50-70: Moderate match (Requires some domain shift).
    - < 50: Poor match (Irrelevant or over-seniority).
3. **Draft a Tailored Summary:** Create a 2-3 sentence "About the candidate" summary specifically highlighting the 1-2 projects from the inventory that are most relevant to this JD.

**Output Format (Strictly JSON):**
{{
    "score": int,
    "rationale": "One sentence explaining the score",
    "tailored_summary": "The 2-3 sentence tailored pitch",
    "decision": "Apply" or "Skip"
}}
"""

tailored_resume_bullet_prompt = """
Based on the following Job Description, select the 3 most relevant projects from Yulun's inventory and rewrite 1-2 bullet points for each to mirror the JD's terminology while staying truthful.

**Inventory:**
{}

**Job Description:**
{}

**Output Format (Strictly JSON):**
{{
    "selected_projects": [
        {{
            "title": "Project Title",
            "bullets": ["Bullet 1", "Bullet 2"]
        }}
    ]
}}
"""
