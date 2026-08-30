"""
production_rag.core.guardrail - Input & Output Safety Guardian
"""

import re
from production_rag.config.settings import settings

class SafetyGuardian:
    """Validates inputs for prompt injection and outputs for destructive CLI/SQL commands."""
    
    @staticmethod
    def inspect_input(query: str) -> dict:
        """Scan input query for prompt injection or system prompt override attempts."""
        suspicious_patterns = [
            r"ignore previous instructions",
            r"system prompt",
            r"you are now a",
            r"override rule",
            r"drop database",
            r"delete from",
            r"rm -rf",
            r"sudo rm"
        ]
        query_lower = query.lower()
        for pattern in suspicious_patterns:
            if re.search(pattern, query_lower):
                return {
                    "is_safe": False,
                    "reason": f"Input contains suspicious pattern: '{pattern}'"
                }
        return {"is_safe": True, "reason": "Input cleared"}
    
    @staticmethod
    def inspect_output(output_text: str) -> dict:
        """Scan generated output for dangerous shell commands or destructive SQL."""
        text_lower = output_text.lower()
        flagged_keywords = []
        
        for keyword in settings.BLOCKED_COMMAND_KEYWORDS:
            if keyword.lower() in text_lower:
                flagged_keywords.append(keyword)
                
        if flagged_keywords:
            warning_banner = (
                "\n\n> ⚠️ **SECURITY GUARDRAIL WARNING**: The generated response contains potentially "
                f"hazardous commands ({', '.join(flagged_keywords)}). Proceed with caution and verify in non-production environments first."
            )
            return {
                "is_safe": False,
                "flagged": flagged_keywords,
                "sanitized_output": output_text + warning_banner
            }
            
        return {
            "is_safe": True,
            "flagged": [],
            "sanitized_output": output_text
        }
