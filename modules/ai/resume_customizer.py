import os
import re
import shutil
import sys
from pathlib import Path
from docx import Document
from modules.helpers import print_lg, critical_error_log

def extract_paragraphs_from_docx(docx_path: str) -> list[str]:
    """Reads all paragraphs from a DOCX file and returns their text content."""
    try:
        doc = Document(docx_path)
        return [p.text for p in doc.paragraphs]
    except Exception as e:
        critical_error_log(f"Failed to read paragraphs from docx: {docx_path}", e)
        return []

def safe_replace_paragraph_text(paragraph, new_text):
    """Updates the paragraph text while preserving its formatting runs."""
    if not paragraph.runs:
        paragraph.add_run(new_text)
    else:
        # Keep formatting of the first run, update its text
        paragraph.runs[0].text = new_text
        # Remove any other runs to clear old text
        p_element = paragraph._p
        for run in paragraph.runs[1:]:
            p_element.remove(run._r)

def apply_docx_updates(input_path: str, output_path: str, updates: list[dict]) -> None:
    """Copies input DOCX to output path and applies paragraph replacements in-place."""
    try:
        shutil.copy(input_path, output_path)
        doc = Document(output_path)
        
        for update in updates:
            index = update.get("index")
            rewritten = update.get("rewritten", "")
            if index is not None and 0 <= index < len(doc.paragraphs):
                safe_replace_paragraph_text(doc.paragraphs[index], rewritten)
                
        doc.save(output_path)
        print_lg(f"Successfully applied {len(updates)} paragraph updates and saved to: {output_path}")
    except Exception as e:
        critical_error_log(f"Failed to apply docx updates from {input_path} to {output_path}", e)
        raise

def ai_tailor_resume_bullets(job_description: str, inventory_content: str, model, provider: str) -> dict | None:
    """Queries the appropriate AI provider (Gemini, OpenAI, DeepSeek) for tailored resume bullets."""
    from modules.ai.intelligent_matching_prompts import tailored_resume_bullet_prompt
    
    provider_lower = provider.lower()
    
    if provider_lower == "gemini":
        from modules.ai.geminiConnections import gemini_completion
        try:
            prompt = tailored_resume_bullet_prompt.format(inventory_content, job_description)
            return gemini_completion(model, prompt, is_json=True)
        except Exception as e:
            print(f"Gemini resume tailoring failed: {e}")
            return None
            
    elif provider_lower == "openai":
        from modules.ai.openaiConnections import ai_completion
        try:
            prompt = tailored_resume_bullet_prompt.format(inventory_content, job_description)
            messages = [{"role": "user", "content": prompt}]
            return ai_completion(model, messages, response_format={"type": "json_object"})
        except Exception as e:
            print(f"OpenAI resume tailoring failed: {e}")
            return None
            
    elif provider_lower == "deepseek":
        from modules.ai.deepseekConnections import deepseek_completion
        try:
            prompt = tailored_resume_bullet_prompt.format(inventory_content, job_description)
            messages = [{"role": "user", "content": prompt}]
            return deepseek_completion(model, messages, response_format={"type": "json_object"})
        except Exception as e:
            print(f"DeepSeek resume tailoring failed: {e}")
            return None
            
    else:
        print(f"Unsupported AI provider for resume tailoring: {provider}")
        return None

def generate_tailored_resume(job_description: str, job_id: str, company_name: str, model, provider: str = None) -> Path | None:
    """API wrapper to match JD, query the configured AI provider, and compile tailored resume docx."""
    if not provider:
        from config.secrets import ai_provider
        provider = ai_provider

    # Resolve Master Resume Path (Option B)
    from config.questions import default_resume_path
    
    master_docx_path = None
    if default_resume_path.lower().endswith(".docx") and os.path.exists(default_resume_path):
        master_docx_path = Path(default_resume_path)
    else:
        # Fallback to standard docx location
        candidates = [
            Path("user_data/resume/resume.docx"),
            Path("resume.docx"),
            Path("user_data/resume/resume.pdf").with_suffix(".docx")
        ]
        for c in candidates:
            if c.exists():
                master_docx_path = c
                break

    if not master_docx_path:
        print_lg("WARNING: Master resume docx not found! Skipping dynamic resume tailoring and falling back to default resume.")
        return None

    print_lg(f"Found Master Resume DOCX: {master_docx_path}")
    
    # 1. Extract paragraphs from the master resume
    paragraphs = extract_paragraphs_from_docx(str(master_docx_path))
    if not paragraphs:
        print_lg("WARNING: Master resume contains no paragraphs! Skipping dynamic resume tailoring.")
        return None
        
    paragraphs_text = "\n".join([f"[{i}] {text}" for i, text in enumerate(paragraphs)])
        
    # 2. Query AI for tailored summary and bullets
    try:
        print_lg(f"Requesting resume bullet tailoring from {provider} AI for Job ID: {job_id}...")
        tailored_data = ai_tailor_resume_bullets(job_description, paragraphs_text, model, provider)
        if not tailored_data or "error" in tailored_data:
            raise ValueError(f"AI API returned error: {tailored_data}")
    except Exception as e:
        critical_error_log(f"Failed to get tailored resume content from {provider} AI!", e)
        return None
        
    # 3. Compile and save the tailored DOCX file
    clean_company = re.sub(r'[^a-zA-Z0-9]', '_', company_name)
    filename = f"Tailored_Resume_{clean_company}_{job_id}.docx"
    output_dir = Path("all resumes")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / filename
    
    try:
        apply_docx_updates(str(master_docx_path), str(output_path), tailored_data.get("updates", []))
        return output_path
    except Exception as e:
        critical_error_log(f"Failed to compile tailored docx for {company_name}", e)
        return None
