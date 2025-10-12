"""
Input Sanitization for AI Prompt Injection Prevention

Phase 8-2: Security Hardening
Prevents prompt injection attacks and malicious input
"""

import re
from typing import Optional


class InputSanitizer:
    """
    Sanitizes user input to prevent:
    - Prompt injection attacks
    - AI model manipulation
    - Data exfiltration attempts
    - Control character exploits
    """

    # Dangerous patterns that could manipulate AI models
    DANGEROUS_PATTERNS = [
        # Direct instruction injection
        r'ignore\s+(?:previous|all|above)\s+instructions?',
        r'disregard\s+(?:previous|all|above)\s+instructions?',
        r'forget\s+(?:previous|all|above)\s+instructions?',

        # System prompt manipulation
        r'(?:system|assistant|user)\s*[:=]',
        r'<\|(?:system|assistant|user)\|>',
        r'\[(?:INST|SYS)\]',
        r'</s>',  # End of sequence token

        # Role confusion attempts
        r'you\s+are\s+now',
        r'act\s+as',
        r'pretend\s+(?:to\s+be|you\s+are)',

        # Data exfiltration attempts
        r'print\s+(?:all|your|the)\s+(?:instructions|prompts|rules)',
        r'show\s+(?:me\s+)?(?:all|your|the)\s+(?:instructions|prompts|rules)',
        r'reveal\s+(?:all|your|the)\s+(?:instructions|prompts|system)',

        # Encoding bypass attempts
        r'\\x[0-9a-fA-F]{2}',  # Hex encoding
        r'\\u[0-9a-fA-F]{4}',  # Unicode encoding
        r'&#\d+;',  # HTML entities

        # Code injection attempts
        r'eval\s*\(',
        r'exec\s*\(',
        r'__import__\s*\(',
    ]

    # Compile patterns for efficiency
    DANGEROUS_REGEX = [
        re.compile(pattern, re.IGNORECASE) for pattern in DANGEROUS_PATTERNS
    ]

    @classmethod
    def sanitize_text(
        cls,
        text: str,
        max_length: int = 2000,
        allow_newlines: bool = True
    ) -> str:
        """
        Sanitize user input text

        Args:
            text: Input text to sanitize
            max_length: Maximum allowed text length
            allow_newlines: Whether to allow newline characters

        Returns:
            Sanitized text safe for AI prompts
        """
        if not text or not isinstance(text, str):
            return ""

        # Step 1: Remove null bytes and control characters (except newlines/tabs if allowed)
        if allow_newlines:
            # Allow newlines (\n), carriage returns (\r), tabs (\t)
            text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
        else:
            # Remove all control characters including newlines
            text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)

        # Step 2: Check for dangerous patterns
        for pattern in cls.DANGEROUS_REGEX:
            if pattern.search(text):
                # Replace with safe placeholder
                text = pattern.sub('[REDACTED FOR SECURITY]', text)

        # Step 3: Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)  # Collapse multiple spaces
        text = text.strip()

        # Step 4: Truncate to max length
        if len(text) > max_length:
            text = text[:max_length] + "..."

        # Step 5: Escape special markdown/HTML that could cause rendering issues
        # (Not strictly security, but prevents UI issues)
        text = cls._escape_special_chars(text)

        return text

    @classmethod
    def _escape_special_chars(cls, text: str) -> str:
        """Escape special characters that could cause display issues"""
        # Remove all HTML tags (including potentially dangerous ones)
        text = re.sub(r'<script[^>]*>.*?</script>', '[SCRIPT_REMOVED]', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r'<iframe[^>]*>.*?</iframe>', '[IFRAME_REMOVED]', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r'<style[^>]*>.*?</style>', '[STYLE_REMOVED]', text, flags=re.IGNORECASE | re.DOTALL)

        # Remove all other HTML tags (including self-closing ones like <img>)
        text = re.sub(r'<[^>]+>', '[HTML_TAG_REMOVED]', text)

        # Remove JavaScript event handlers (onerror, onclick, etc.)
        text = re.sub(r'\bon\w+\s*=\s*["\']?[^"\'>\s]*["\']?', '[EVENT_HANDLER_REMOVED]', text, flags=re.IGNORECASE)

        # Remove javascript: protocol
        text = re.sub(r'javascript\s*:', '[JS_PROTOCOL_REMOVED]', text, flags=re.IGNORECASE)

        return text

    @classmethod
    def sanitize_medical_complaint(cls, text: str) -> str:
        """
        Sanitize chief complaint with medical context preservation

        More lenient than general sanitization to preserve medical terminology
        """
        return cls.sanitize_text(text, max_length=500, allow_newlines=False)

    @classmethod
    def sanitize_medical_history(cls, text: str) -> str:
        """Sanitize history of present illness"""
        return cls.sanitize_text(text, max_length=2000, allow_newlines=True)

    @classmethod
    def sanitize_list(cls, items: list, max_items: int = 50) -> list:
        """
        Sanitize list of strings

        Args:
            items: List of strings to sanitize
            max_items: Maximum number of items to allow

        Returns:
            Sanitized list
        """
        if not items or not isinstance(items, list):
            return []

        # Limit number of items
        items = items[:max_items]

        # Sanitize each item
        sanitized = []
        for item in items:
            if isinstance(item, str):
                sanitized_item = cls.sanitize_text(item, max_length=200, allow_newlines=False)
                if sanitized_item:  # Only add non-empty strings
                    sanitized.append(sanitized_item)

        return sanitized

    @classmethod
    def validate_medication_name(cls, medication: str) -> bool:
        """
        Validate medication name format

        Args:
            medication: Medication name to validate

        Returns:
            True if valid format, False otherwise
        """
        if not medication or not isinstance(medication, str):
            return False

        # Medication names should be alphanumeric with hyphens/spaces only
        # Length: 2-100 characters
        pattern = r'^[a-zA-Z0-9\s\-]{2,100}$'

        return bool(re.match(pattern, medication.strip()))

    @classmethod
    def detect_injection_attempt(cls, text: str) -> Optional[str]:
        """
        Detect potential injection attempts

        Args:
            text: Text to analyze

        Returns:
            Detection message if injection detected, None otherwise
        """
        if not text or not isinstance(text, str):
            return None

        for i, pattern in enumerate(cls.DANGEROUS_REGEX):
            match = pattern.search(text)
            if match:
                return f"Potential injection attempt detected: Pattern {i+1} matched '{match.group()}'"

        return None


# Global sanitizer instance
sanitizer = InputSanitizer()
