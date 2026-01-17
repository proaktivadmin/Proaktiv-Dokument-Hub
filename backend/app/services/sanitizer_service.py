"""
Sanitizer Service - Cleans and standardizes HTML templates for Vitec Next.

Full Vitec Stilark Compliance Mode (V2.9):
- Strips ALL inline styles except structural (width, height, margin, padding, border, text-align)
- Ensures Vitec Stilark resource reference is present
- Wraps content in #vitecTemplate div
- Uses Open Sans font (controlled by Vitec Stilark, not inline)

Ported from legacy sanitizer.js to Python using BeautifulSoup.
"""

import re
import logging
from typing import Optional, Tuple, List
from bs4 import BeautifulSoup, Comment, Tag

logger = logging.getLogger(__name__)


class SanitizerService:
    """
    Service for sanitizing HTML templates to conform to Vitec Next standards.
    
    V2.9 Full Compliance Mode:
    - Strips ALL inline styles except structural properties
    - Removes deprecated <font> tags while preserving content
    - Injects Vitec Stilark resource reference
    - Ensures content is wrapped in #vitecTemplate wrapper
    - Validates vitec-if/vitec-foreach syntax
    """

    # Structural styles to PRESERVE (all others are stripped)
    # These control layout, not appearance
    PRESERVE_STYLES = [
        'width', 'height', 'max-width', 'max-height', 'min-width', 'min-height',
        'margin', 'margin-top', 'margin-bottom', 'margin-left', 'margin-right',
        'padding', 'padding-top', 'padding-bottom', 'padding-left', 'padding-right',
        'border', 'border-top', 'border-bottom', 'border-left', 'border-right',
        'border-collapse', 'border-spacing',
        'text-align', 'vertical-align',
        'display', 'float', 'clear',
        'position', 'top', 'bottom', 'left', 'right',
        'table-layout', 'page-break-before', 'page-break-after', 'page-break-inside',
    ]
    
    # Legacy styles pattern (for backwards compatibility detection)
    OLD_STYLES_PATTERN = re.compile(
        r'(font-family|font-size|color|background-color)\s*:[^;"]+;?',
        re.IGNORECASE
    )
    
    # Default Vitec resource string
    DEFAULT_RESOURCE_STRING = "resource:Vitec Stilark"
    VITEC_STILARK_RESOURCE = "resource:Vitec Stilark"
    
    # Tags to completely remove (but keep their content)
    UNWRAP_TAGS = ['font', 'center', 'u']
    
    # Attributes to strip from all elements
    DANGEROUS_ATTRIBUTES = ['onclick', 'onload', 'onerror', 'onmouseover', 'onmouseout']
    
    # System template markers - if these are found, skip sanitization
    SYSTEM_MARKERS = [
        'vitec-stilark',        # System stylesheet
        'vitec-structure',      # Structure CSS
        'theme-proaktiv',       # Theme CSS
        'vitec-system-template', # Explicit system marker
    ]

    def __init__(self, theme_class: str = "proaktiv-theme", full_strip: bool = True):
        """
        Initialize the sanitizer service.
        
        Args:
            theme_class: The CSS class to apply to the wrapper div.
            full_strip: If True, strips ALL non-structural styles (V2.9 mode).
                       If False, only strips legacy font/color styles (legacy mode).
        """
        self.theme_class = theme_class
        self.full_strip = full_strip

    def _is_already_valid(self, soup: BeautifulSoup) -> Tuple[bool, str]:
        """
        Check if the HTML content is already valid and should not be sanitized.
        
        Returns:
            Tuple of (is_valid, reason)
        """
        # Check 1: Already wrapped in #vitecTemplate with correct theme class
        vitec_wrapper = soup.find(id="vitecTemplate")
        if vitec_wrapper:
            classes = vitec_wrapper.get("class", [])
            if isinstance(classes, str):
                classes = classes.split()
            
            # If it has the theme class, it's already been processed
            if self.theme_class in classes:
                return True, "Already wrapped in #vitecTemplate with theme class"
        
        # Check 2: Contains system template markers (comments or classes)
        # Look for HTML comments indicating system template
        for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
            comment_text = str(comment).lower()
            for marker in self.SYSTEM_MARKERS:
                if marker in comment_text:
                    return True, f"Contains system marker: {marker}"
        
        # Check 3: Contains specific Vitec system classes
        for marker in self.SYSTEM_MARKERS:
            if soup.find(class_=lambda x: x and marker in str(x).lower()):
                return True, f"Contains system class: {marker}"
        
        # Check 4: Has vitec-template attribute pointing to premium stylesheet
        resource_elements = soup.find_all(attrs={"vitec-template": True})
        for el in resource_elements:
            resource_val = el.get("vitec-template", "")
            if "Premium" in resource_val or "Gold" in resource_val:
                return True, "Already using premium Vitec stylesheet"
        
        return False, ""

    def sanitize(self, html: str, update_resource: bool = True) -> str:
        """
        Sanitize an HTML template string.
        
        Smart sanitization: Automatically detects if content is already valid
        (wrapped in #vitecTemplate with theme class, or contains system markers)
        and returns it untouched to avoid double-wrapping or breaking system templates.
        
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
        
        # Smart detection: Check if content is already valid
        is_valid, reason = self._is_already_valid(soup)
        if is_valid:
            logger.info(f"Skipping sanitization: {reason}")
            # Return original content (extract it properly to avoid lxml wrappers)
            return self._extract_content(soup)
        
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
                element["vitec-template"] = self.VITEC_STILARK_RESOURCE

    def _strip_inline_styles(self, soup: BeautifulSoup) -> None:
        """
        Remove inline styles from all elements.
        
        V2.9 Full Strip Mode (self.full_strip=True):
        - Strips ALL styles except structural (width, height, margin, padding, border, etc.)
        - Lets Vitec Stilark control all typography and colors
        
        Legacy Mode (self.full_strip=False):
        - Only strips font-family, font-size, color, background-color
        
        Args:
            soup: The BeautifulSoup object to modify.
        """
        for element in soup.find_all(style=True):
            original_style = element.get("style", "")
            if not original_style:
                continue
            
            if self.full_strip:
                # V2.9: Full strip - only preserve structural styles
                new_style = self._filter_styles(original_style, self.PRESERVE_STYLES)
            else:
                # Legacy: Only remove font/color properties
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
    
    def _filter_styles(self, style_string: str, keep_properties: List[str]) -> str:
        """
        Filter a CSS style string to only keep specified properties.
        
        Args:
            style_string: The original CSS style string.
            keep_properties: List of CSS property names to preserve.
            
        Returns:
            Filtered style string with only preserved properties.
        """
        # Split by semicolon and process each declaration
        declarations = style_string.split(';')
        kept = []
        
        for declaration in declarations:
            declaration = declaration.strip()
            if not declaration or ':' not in declaration:
                continue
            
            prop_name = declaration.split(':')[0].strip().lower()
            
            # Check if this property should be preserved
            for keep_prop in keep_properties:
                if prop_name == keep_prop or prop_name.startswith(keep_prop + '-'):
                    kept.append(declaration)
                    break
        
        return '; '.join(kept)

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
        Ensure the content is wrapped in a #vitecTemplate div with Vitec Stilark reference.
        
        V2.9 Requirements:
        1. Content wrapped in <div id="vitecTemplate">
        2. Vitec Stilark resource reference present
        3. Theme class applied to wrapper
        
        Args:
            soup: The BeautifulSoup object to process.
            
        Returns:
            The final HTML string with proper wrapper and Stilark reference.
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
            
            # Ensure Vitec Stilark reference exists
            self._ensure_stilark_reference(existing_wrapper)
            
            # Return the soup as string
            return self._extract_content(soup)
        
        # No existing wrapper - we need to wrap the content
        # Check if there's a body tag
        body = soup.find("body")
        if body:
            # Wrap body content
            body_content = "".join(str(child) for child in body.children)
            wrapper_html = self._create_wrapper_with_stilark(body_content)
            body.clear()
            body.append(BeautifulSoup(wrapper_html, 'lxml').find(id="vitecTemplate"))
            return self._extract_content(soup)
        
        # No body tag - wrap the entire content
        content = self._extract_content(soup)
        return self._create_wrapper_with_stilark(content)
    
    def _ensure_stilark_reference(self, wrapper: Tag) -> None:
        """
        Ensure Vitec Stilark resource reference exists in the wrapper.
        
        If no resource reference exists, inject one at the beginning of the wrapper.
        
        Args:
            wrapper: The #vitecTemplate wrapper element.
        """
        # Check if Stilark reference already exists
        stilark_ref = wrapper.find(attrs={"vitec-template": True})
        if stilark_ref:
            # Update existing reference to standard Stilark
            current_val = stilark_ref.get("vitec-template", "")
            if current_val.startswith("resource:"):
                stilark_ref["vitec-template"] = self.VITEC_STILARK_RESOURCE
            return
        
        # No reference - inject one at the beginning
        stilark_span = BeautifulSoup(
            f'<span vitec-template="{self.VITEC_STILARK_RESOURCE}">&nbsp;</span>',
            'html.parser'
        ).find('span')
        
        if stilark_span:
            # Insert at the beginning of wrapper
            wrapper.insert(0, stilark_span)
    
    def _create_wrapper_with_stilark(self, content: str) -> str:
        """
        Create a complete #vitecTemplate wrapper with Stilark reference.
        
        Args:
            content: The HTML content to wrap.
            
        Returns:
            Complete wrapper HTML string.
        """
        return f'''<div id="vitecTemplate" class="{self.theme_class}">
  <span vitec-template="{self.VITEC_STILARK_RESOURCE}">&nbsp;</span>
  {content}
</div>'''

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
