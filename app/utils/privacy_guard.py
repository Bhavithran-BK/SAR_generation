import re
import logging

logger = logging.getLogger(__name__)

class NarrativeStitcher:
    """
    Handles re-injection of PII into AI-generated SAR narratives
    using standardized placeholders.
    """
    
    PLACEHOLDERS = {
        "CUSTOMER_NAME": r"\{\{CUSTOMER_NAME\}\}",
        "ACCOUNT_NUMBER": r"\{\{ACCOUNT_NUMBER\}\}",
        "CUSTOMER_ID": r"\{\{CUSTOMER_ID\}\}",
        "COUNTRY": r"\{\{COUNTRY\}\}",
        "CASE_ID": r"\{\{CASE_ID\}\}"
    }

    @staticmethod
    def stitch(narrative: str, pii_data: dict) -> str:
        """
        Replaces placeholders in the narrative with actual PII values.
        Supports both {{PLACEHOLDER}} and {PLACEHOLDER} for robustness.
        """
        stitched = narrative
        
        mapping = {
            "CUSTOMER_NAME": pii_data.get("name", "[NAME MISSING]"),
            "ACCOUNT_NUMBER": pii_data.get("account", "[ACCOUNT MISSING]"),
            "CUSTOMER_ID": pii_data.get("customer_id", "[ID MISSING]"),
            "COUNTRY": pii_data.get("country", "[COUNTRY MISSING]"),
            "CASE_ID": pii_data.get("case_id", "[CASE_ID MISSING]")
        }
        
        for key, value in mapping.items():
            # Replace double braces
            stitched = stitched.replace(f"{{{{{key}}}}}", str(value))
            # Replace single braces (fallback)
            stitched = stitched.replace(f"{{{key}}}", str(value))
            
        return stitched

class PrivacyGuard:
    """
    Validates AI output for potential PII leakage or formatting errors.
    """
    
    @staticmethod
    def check_leakage(text: str, sensitive_values: list) -> bool:
        """
        Returns True if any sensitive value is found in the text.
        """
        for val in sensitive_values:
            if val and str(val).lower() in text.lower():
                logger.warning(f"PII Leakage Detected: Value '{val}' found in AI output.")
                return True
        return False

    @staticmethod
    def validate_placeholders(text: str) -> bool:
        """
        Checks if the text contains any malformed placeholders (e.g. single braces).
        """
        # Check for single { or } that are not part of {{ or }}
        if re.search(r"(?<!\{)\{(?!\{)", text) or re.search(r"(?<!\})\}(?!\})", text):
            return False
        return True
