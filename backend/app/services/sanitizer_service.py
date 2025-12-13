"""
Sanitizer Service - Cleans and standardizes HTML templates for Vitec Next.

Ported from legacy sanitizer.js to Python using BeautifulSoup.
"""

import re
from typing import Optional
from bs4 import BeautifulSoup, Comment


class SanitizerService:
    """
    Service for sanitizing HTML templates to conform to Vitec Next standards.
    
    This service:
    - Strips legacy inline styles (font-family, font-size, color, background-color)
    - Removes deprecated <font> tags while preserving content
    - Updates Vitec resource pointers to the new stylesheet
    - Ensures content is wrapped in a standard #vitecTemplate wrapper
    """

    # Regex patterns for style cleanup
    OLD_STYLES_PATTERN = re.compile(
        r'(font-family|font-size|color|background-color)\s*:[^;"]+;?',
        re.IGNORECASE
    )
    
    # Default resource string for Vitec templates
    DEFAULT_RESOURCE_STRING = "resource:Vitec Stilark"
    NEW_RESOURCE_STRING = "resource:Vitec Stilark Premium Gold Navy"
    
    # Tags to completely remove (but keep their content)
    UNWRAP_TAGS = ['font']
    
    # Attributes to strip from all elements
    DANGEROUS_ATTRIBUTES = ['onclick', 'onload', 'onerror', 'onmouseover']

    def __init__(self, theme_class: str = "proaktiv-theme"):
        """
        Initialize the sanitizer service.
        
        Args:
            theme_class: The CSS class to apply to the wrapper div.
        """
        self.theme_class = theme_class

    def sanitize(self, html: str, update_resource: bool = True) -> str:
        """
        Sanitize an HTML template string.
        
        Args:
            html: The raw HTML content to sanitize.
            update_resource: Whether to update the Vitec resource pointer.
            
        Returns:
            The sanitized HTML string.
        """
        if not html or not html.strip():
            return self._create_empty_wrapper()
        
        # Parse the HTML
        soup = BeautifulSoup(html, 'lxml')
        
        # Step 1: Update resource pointers
        if update_resource:
            self._update_resource_pointers(soup)
        
        # Step 2: Strip legacy inline styles
        self._strip_inline_styles(soup)
        
        # Step 3: Remove <font> tags (unwrap them, keeping content)
        self._unwrap_deprecated_tags(soup)
        
        # Step 4: Remove dangerous attributes
        self._remove_dangerous_attributes(soup)
        
        # Step 5: Ensure proper wrapper
        result = self._ensure_wrapper(soup)
        
        return result

    def _update_resource_pointers(self, soup: BeautifulSoup) -> None:
        """
        Update Vitec resource template pointers to the new stylesheet.
        
        Args:
            soup: The BeautifulSoup object to modify.
        """
        # Find all elements with vitec-template attribute
        for element in soup.find_all(attrs={"vitec-template": True}):
            current_value = element.get("vitec-template", "")
            if current_value.startswith("resource:"):
                element["vitec-template"] = self.NEW_RESOURCE_STRING

    def _strip_inline_styles(self, soup: BeautifulSoup) -> None:
        """
        Remove legacy inline styles from all elements.
        
        Specifically removes: font-family, font-size, color, background-color
        
        Args:
            soup: The BeautifulSoup object to modify.
        """
        for element in soup.find_all(style=True):
            original_style = element.get("style", "")
            if original_style:
                # Remove legacy style properties
                new_style = self.OLD_STYLES_PATTERN.sub('', original_style)
                # Clean up multiple semicolons and whitespace
                new_style = re.sub(r';\s*;', ';', new_style)
                new_style = re.sub(r'^\s*;\s*', '', new_style)
                new_style = re.sub(r'\s*;\s*$', '', new_style)
                new_style = new_style.strip()
                
                if new_style:
                    element["style"] = new_style
                else:
                    # Remove empty style attribute
                    del element["style"]

    def _unwrap_deprecated_tags(self, soup: BeautifulSoup) -> None:
        """
        Remove deprecated tags while preserving their content.
        
        Args:
            soup: The BeautifulSoup object to modify.
        """
        for tag_name in self.UNWRAP_TAGS:
            for tag in soup.find_all(tag_name):
                tag.unwrap()

    def _remove_dangerous_attributes(self, soup: BeautifulSoup) -> None:
        """
        Remove potentially dangerous event handler attributes.
        
        Args:
            soup: The BeautifulSoup object to modify.
        """
        for attr in self.DANGEROUS_ATTRIBUTES:
            for element in soup.find_all(attrs={attr: True}):
                del element[attr]

    def _ensure_wrapper(self, soup: BeautifulSoup) -> str:
        """
        Ensure the content is wrapped in a #vitecTemplate div.
        
        Args:
            soup: The BeautifulSoup object to process.
            
        Returns:
            The final HTML string with proper wrapper.
        """
        # Check if #vitecTemplate already exists
        existing_wrapper = soup.find(id="vitecTemplate")
        
        if existing_wrapper:
            # Ensure the theme class is applied
            current_classes = existing_wrapper.get("class", [])
            if isinstance(current_classes, str):
                current_classes = current_classes.split()
            if self.theme_class not in current_classes:
                current_classes.append(self.theme_class)
                existing_wrapper["class"] = current_classes
            
            # Return the soup as string
            return self._extract_content(soup)
        
        # No existing wrapper - we need to wrap the content
        # Check if there's a body tag
        body = soup.find("body")
        if body:
            # Wrap body content
            body_content = "".join(str(child) for child in body.children)
            wrapper_html = f'<div id="vitecTemplate" class="{self.theme_class}">\n{body_content}\n</div>'
            body.clear()
            body.append(BeautifulSoup(wrapper_html, 'lxml').find(id="vitecTemplate"))
            return self._extract_content(soup)
        
        # No body tag - wrap the entire content
        content = self._extract_content(soup)
        return f'<div id="vitecTemplate" class="{self.theme_class}">\n{content}\n</div>'

    def _extract_content(self, soup: BeautifulSoup) -> str:
        """
        Extract the main content from the soup, handling full HTML documents.
        
        Args:
            soup: The BeautifulSoup object.
            
        Returns:
            The extracted HTML content as a string.
        """
        # If it's a full HTML document, extract body content
        body = soup.find("body")
        if body:
            return "".join(str(child) for child in body.children).strip()
        
        # Otherwise, return the entire parsed content (minus html/body wrappers lxml adds)
        # lxml wraps fragments in <html><body>...</body></html>
        if soup.html and soup.body:
            return "".join(str(child) for child in soup.body.children).strip()
        
        return str(soup).strip()

    def _create_empty_wrapper(self) -> str:
        """
        Create an empty Vitec template wrapper.
        
        Returns:
            An empty wrapper div string.
        """
        return f'<div id="vitecTemplate" class="{self.theme_class}"></div>'

    def strip_styles_only(self, html: str) -> str:
        """
        Strip only inline styles without other processing.
        
        Useful for partial cleanup operations.
        
        Args:
            html: The HTML content.
            
        Returns:
            HTML with inline styles removed.
        """
        soup = BeautifulSoup(html, 'lxml')
        self._strip_inline_styles(soup)
        return self._extract_content(soup)

    def validate_structure(self, html: str) -> dict:
        """
        Validate the structure of an HTML template.
        
        Args:
            html: The HTML content to validate.
            
        Returns:
            A dict with validation results.
        """
        soup = BeautifulSoup(html, 'lxml')
        
        has_wrapper = soup.find(id="vitecTemplate") is not None
        has_resource = soup.find(attrs={"vitec-template": True}) is not None
        has_legacy_fonts = len(soup.find_all("font")) > 0
        
        # Count elements with legacy styles
        legacy_style_count = 0
        for element in soup.find_all(style=True):
            style = element.get("style", "")
            if self.OLD_STYLES_PATTERN.search(style):
                legacy_style_count += 1
        
        return {
            "has_vitec_wrapper": has_wrapper,
            "has_resource_reference": has_resource,
            "has_legacy_font_tags": has_legacy_fonts,
            "legacy_style_count": legacy_style_count,
            "is_valid": has_wrapper and not has_legacy_fonts and legacy_style_count == 0
        }


# Singleton instance for dependency injection
_sanitizer_service: Optional[SanitizerService] = None


def get_sanitizer_service() -> SanitizerService:
    """
    Get the singleton SanitizerService instance.
    
    Returns:
        The SanitizerService instance.
    """
    global _sanitizer_service
    if _sanitizer_service is None:
        _sanitizer_service = SanitizerService()
    return _sanitizer_service
