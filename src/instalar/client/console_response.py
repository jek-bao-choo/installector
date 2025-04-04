import re
from typing import Dict

class ResponseHandler:
    """Handles parsing and extraction of LLM responses"""
    
    @staticmethod
    def extract_xml_section(text: str, tag: str) -> str:
        """Extract content between XML tags, handling both normal and code block formats"""
        # Handle terminate tags case-insensitively
        if tag.lower() == "terminate":
            pattern = r"<terminate>.*?</terminate>"
            return "true" if re.search(pattern, text, re.DOTALL | re.IGNORECASE) else ""
        
        # Try standard XML tags first
        pattern = f"<{tag}>(.*?)</{tag}>"
        match = re.search(pattern, text, re.DOTALL)
        
        if match:
            content = match.group(1).strip()
            
            # If content contains backtick code blocks, extract from them
            code_pattern = r"```(?:xml|bash|shell|\w+)?\n?(.*?)```"
            code_match = re.search(code_pattern, content, re.DOTALL)
            if code_match:
                return code_match.group(1).strip()
            
            return content
        return ""

    @staticmethod
    def extract_response_sections(text: str) -> Dict[str, str]:
        """Extract all XML sections from the response text"""
        return {
            'think': ResponseHandler.extract_xml_section(text, 'think'),
            'title': ResponseHandler.extract_xml_section(text, 'title_section'),
            'description': ResponseHandler.extract_xml_section(text, 'description_section'),
            'execution': ResponseHandler.extract_xml_section(text, 'execution_section'),
            'expected': ResponseHandler.extract_xml_section(text, 'expected_section'),
            'verification': ResponseHandler.extract_xml_section(text, 'verification_section'),
            'conclusion': ResponseHandler.extract_xml_section(text, 'conclusion_section')
        }
