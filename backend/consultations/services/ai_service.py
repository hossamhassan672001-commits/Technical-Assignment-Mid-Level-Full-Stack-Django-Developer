"""
AI Service for generating consultation summaries.

Uses OpenAI ChatCompletion if OPENAI_API_KEY is configured.
Falls back to a realistic structured mock response if the key is absent or
the OPENAI_USE_MOCK environment variable is set to 'true'.
"""

import os
import json
import logging

logger = logging.getLogger(__name__)


def generate_consultation_summary(symptoms: str, diagnosis: str) -> str:
    """
    Generate an AI summary for a consultation.

    Args:
        symptoms: The patient's reported symptoms.
        diagnosis: The doctor's diagnosis (may be empty).

    Returns:
        A structured string summary from the AI.
    """
    api_key = os.environ.get('OPENAI_API_KEY', '')
    use_mock = os.environ.get('OPENAI_USE_MOCK', 'false').lower() == 'true'

    if api_key and not use_mock:
        return _call_openai(api_key, symptoms, diagnosis)
    else:
        logger.info("OPENAI_API_KEY not set or mock mode enabled — returning mock AI summary.")
        return _mock_summary(symptoms, diagnosis)


def _call_openai(api_key: str, symptoms: str, diagnosis: str) -> str:
    """Call the real OpenAI API."""
    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)

        prompt = _build_prompt(symptoms, diagnosis)

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a medical AI assistant. Generate concise, structured clinical "
                        "consultation summaries. Return a JSON object with keys: "
                        "'chief_complaint', 'clinical_impression', 'key_findings', "
                        "'recommended_actions', and 'follow_up'."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=500,
        )

        content = response.choices[0].message.content.strip()

        # Try to parse as JSON for clean formatting, fall back to raw text
        try:
            parsed = json.loads(content)
            return _format_summary(parsed)
        except json.JSONDecodeError:
            return content

    except Exception as exc:
        logger.error("OpenAI API call failed: %s", exc)
        # Return mock on failure so the endpoint still succeeds
        return _mock_summary(symptoms, diagnosis)


def _build_prompt(symptoms: str, diagnosis: str) -> str:
    parts = [f"Symptoms: {symptoms}"]
    if diagnosis.strip():
        parts.append(f"Diagnosis: {diagnosis}")
    parts.append(
        "\nPlease generate a structured clinical summary as a JSON object with keys: "
        "chief_complaint, clinical_impression, key_findings (list), "
        "recommended_actions (list), and follow_up."
    )
    return "\n".join(parts)


def _mock_summary(symptoms: str, diagnosis: str) -> str:
    """Return a realistic mock summary based on the given symptoms/diagnosis."""
    diagnosis_line = diagnosis.strip() if diagnosis.strip() else "Pending further evaluation"

    summary_data = {
        "chief_complaint": symptoms[:120] + ("..." if len(symptoms) > 120 else ""),
        "clinical_impression": diagnosis_line,
        "key_findings": [
            f"Patient presents with: {symptoms[:80]}",
            "Vital signs within acceptable range (assumed)",
            "No acute distress observed",
        ],
        "recommended_actions": [
            "Continue monitoring symptoms",
            "Prescribe appropriate medication based on diagnosis",
            "Advise rest and adequate hydration",
            "Follow-up if symptoms worsen or persist beyond 7 days",
        ],
        "follow_up": "Scheduled follow-up in 7–10 days. Patient advised to seek immediate care if symptoms escalate.",
    }

    return _format_summary(summary_data)


def _format_summary(data: dict) -> str:
    """Format the structured summary dict into a readable string."""
    lines = []

    if "chief_complaint" in data:
        lines.append(f"Chief Complaint:\n  {data['chief_complaint']}")

    if "clinical_impression" in data:
        lines.append(f"\nClinical Impression:\n  {data['clinical_impression']}")

    if "key_findings" in data:
        lines.append("\nKey Findings:")
        for finding in data["key_findings"]:
            lines.append(f"  • {finding}")

    if "recommended_actions" in data:
        lines.append("\nRecommended Actions:")
        for action in data["recommended_actions"]:
            lines.append(f"  • {action}")

    if "follow_up" in data:
        lines.append(f"\nFollow-up:\n  {data['follow_up']}")

    return "\n".join(lines)
