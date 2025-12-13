const fs = require('fs');
const path = require('path');

const OLD_STYLES_REGEX = /(font-family|font-size|color|background-color)\s*:[^;"]+;?/gi;
const FONT_TAG_REGEX = /<\/?font[^>]*>/gi;
const RESOURCE_SPAN_REGEX = /vitec-template="resource:[^"]+"/gi;
const NEW_RESOURCE_STRING = 'vitec-template="resource:Vitec Stilark Premium Gold Navy"';

/**
 * Sanitizes a legacy HTML string.
 * @param {string} html - The raw HTML content.
 * @returns {string} - The sanitized and updated HTML.
 */
function sanitizeTemplate(html) {
    let cleaned = html;

    // 1. Update Resource Pointer
    // Looks for existing vitec-template attribute and replaces it
    if (RESOURCE_SPAN_REGEX.test(cleaned)) {
        cleaned = cleaned.replace(RESOURCE_SPAN_REGEX, NEW_RESOURCE_STRING);
    } else {
        // If not found, try to find a generic vitec-resource span and inject/update logic manually
        // For now, we assume standard Vitec structure or we might need to insert it
        // Regex for the whole span might be safer
        // <span class="vitec-resource" vitec-template="resource:Vitec Stilark"></span>
        const wholeSpanRegex = /<span[^>]*class=["']vitec-resource["'][^>]*>/i;
        if (wholeSpanRegex.test(cleaned)) {
            // We found the span but maybe the attribute is missing or different? 
            // Let's simple replace the attribute if found, done above.
            // If we are here, regex didn't match the attribute but span exists. 
            // Complex case, skip for MVP regex.
        }
    }

    // 2. Strip Legacy Inline Styles
    // We want to remove font-family, color, etc. from style="..."
    // This is tricky with regex inside attributes.
    // Strategy: Find style="..." blocks, and replace inside them.
    cleaned = cleaned.replace(/style="([^"]*)"/gi, (match, styleContent) => {
        const newStyle = styleContent.replace(OLD_STYLES_REGEX, '').trim();
        return `style="${newStyle}"`;
    });

    // 3. Remove <font> tags completely (stripping tag, keeping content)
    // Note: Regex replace of open/close tags independently works for simple nesting.
    cleaned = cleaned.replace(FONT_TAG_REGEX, '');

    // 4. Ensure Wrapper
    // Check if #vitecTemplate exists
    if (!cleaned.includes('id="vitecTemplate"')) {
        // Wrap everything inside body? Or just wrap the whole thing if it's a fragment?
        // Safe bet: If user provides full HTML with body, inject inside body.
        const bodyMatch = cleaned.match(/<body[^>]*>([\s\S]*)<\/body>/i);
        if (bodyMatch) {
            const bodyContent = bodyMatch[1];
            cleaned = cleaned.replace(bodyContent, `
    <div id="vitecTemplate" class="proaktiv-theme">
        ${bodyContent}
    </div>
            `);
        } else {
            // No body tag, wrap the whole thing
            cleaned = `<div id="vitecTemplate" class="proaktiv-theme">\n${cleaned}\n</div>`;
        }
    } else {
        // If it exists, ensure class="proaktiv-theme" is there
        const wrapperRegex = /(<div[^>]*id="vitecTemplate"[^>]*)/i;
        cleaned = cleaned.replace(wrapperRegex, (match) => {
            if (!match.includes('class=')) {
                return `${match.slice(0, -1)} class="proaktiv-theme">`;
            } else if (!match.includes('proaktiv-theme')) {
                return match.replace(/class="([^"]*)"/, 'class="$1 proaktiv-theme"');
            }
            return match;
        });
    }

    return cleaned;
}

/**
 * Process a single file
 */
function processFile(filePath, outputDir) {
    try {
        const content = fs.readFileSync(filePath, 'utf8');
        const sanitized = sanitizeTemplate(content);
        const fileName = path.basename(filePath);
        const outputPath = path.join(outputDir, fileName);
        fs.writeFileSync(outputPath, sanitized);
        return { success: true, file: fileName };
    } catch (err) {
        return { success: false, file: filePath, error: err.message };
    }
}

module.exports = {
    sanitizeTemplate,
    processFile
};
