/**
 * Vitec Preview Renderer
 *
 * Produces a "flettet" preview similar to Vitec Next by:
 * - Replacing merge fields ([[path]] / [[*path]]) with test values
 * - Evaluating vitec-if conditions
 * - Expanding vitec-foreach loops
 *
 * Note: This is a preview renderer, not a full Vitec template engine.
 * It intentionally supports a safe subset of Vitec expressions.
 */

export interface VitecRenderReport {
  merge_fields_replaced: number;
  vitec_if_evaluated: number;
  vitec_if_removed: number;
  vitec_foreach_expanded: number;
  vitec_foreach_iterations: number;
  unsupported_expressions: number;
}

export interface VitecRenderInput {
  /** Raw HTML content (template source) */
  html: string;
  /** Key/value mapping for merge fields (e.g. "eiendom.adresse" -> "Storgata 5B") */
  values: Record<string, string>;
  /**
   * Vitec-like Model object used for evaluating vitec-if / vitec-foreach.
   * Example: { eiendom: { eieform: "Andel" }, kjopere: [{...}], selgere: [{...}] }
   */
  model: Record<string, unknown>;
}

export interface VitecRenderOutput {
  html: string;
  report: VitecRenderReport;
}

type Token =
  | { type: "lparen" }
  | { type: "rparen" }
  | { type: "op"; value: OpToken }
  | { type: "string"; value: string }
  | { type: "number"; value: number }
  | { type: "boolean"; value: boolean }
  | { type: "model"; path: string; isCount: boolean }
  | { type: "unknown"; value: string };

type OpToken = "&&" | "||" | "==" | "!=" | ">=" | "<=" | ">" | "<";

const MERGE_FIELD_REGEX = /\[\[(\*?)([^\]]+)\]\]/g;

export function renderVitecPreview(input: VitecRenderInput): VitecRenderOutput {
  const report: VitecRenderReport = {
    merge_fields_replaced: 0,
    vitec_if_evaluated: 0,
    vitec_if_removed: 0,
    vitec_foreach_expanded: 0,
    vitec_foreach_iterations: 0,
    unsupported_expressions: 0,
  };

  if (!input.html || !input.html.trim()) {
    return { html: input.html, report };
  }

  // Parse as an HTML document, but operate on body contents.
  const parser = new DOMParser();
  const doc = parser.parseFromString(input.html, "text/html");

  // Expand loops first so conditions/merge replacement apply to generated nodes too.
  processForeachLoops(doc.body, input, report);
  processVitecIf(doc.body, input, report);
  replaceMergeFieldsInTree(doc.body, input, report);

  return { html: doc.body.innerHTML, report };
}

function processForeachLoops(root: HTMLElement, input: VitecRenderInput, report: VitecRenderReport) {
  // Process in a loop until no foreach left (handles nested loops and loops inside clones)
  // eslint-disable-next-line no-constant-condition
  while (true) {
    const el = root.querySelector<HTMLElement>("[vitec-foreach]");
    if (!el) break;

    const expr = el.getAttribute("vitec-foreach")?.trim() ?? "";
    const parsed = parseForeachExpression(expr);
    if (!parsed) {
      // Unknown loop expression, remove the node to avoid broken output
      report.unsupported_expressions += 1;
      el.remove();
      continue;
    }

    const collection = getModelValue(input.model, parsed.collectionPath);
    if (!Array.isArray(collection)) {
      // If not iterable, remove loop section
      el.remove();
      continue;
    }

    const parent = el.parentNode;
    if (!parent) {
      el.remove();
      continue;
    }

    report.vitec_foreach_expanded += 1;
    report.vitec_foreach_iterations += collection.length;

    // Insert clones before original, then remove original
    for (const item of collection) {
      const clone = el.cloneNode(true) as HTMLElement;
      clone.removeAttribute("vitec-foreach");
      replaceMergeFieldsInTree(clone, input, report, {
        loopVar: parsed.itemVar,
        loopItem: isRecord(item) ? item : {},
      });
      parent.insertBefore(clone, el);
    }

    parent.removeChild(el);
  }
}

function processVitecIf(root: HTMLElement, input: VitecRenderInput, report: VitecRenderReport) {
  const elements = Array.from(root.querySelectorAll<HTMLElement>("[vitec-if]"));
  for (const el of elements) {
    const expr = el.getAttribute("vitec-if")?.trim() ?? "";
    if (!expr) {
      el.removeAttribute("vitec-if");
      continue;
    }

    const result = safeEvalVitecExpression(expr, input.model);
    report.vitec_if_evaluated += 1;
    if (result === null) {
      report.unsupported_expressions += 1;
      // If we cannot evaluate safely, keep content but remove attribute
      el.removeAttribute("vitec-if");
      continue;
    }

    if (!result) {
      report.vitec_if_removed += 1;
      el.remove();
    } else {
      el.removeAttribute("vitec-if");
    }
  }
}

function replaceMergeFieldsInTree(
  root: HTMLElement,
  input: VitecRenderInput,
  report: VitecRenderReport,
  loop?: { loopVar: string; loopItem: Record<string, unknown> }
) {
  // Replace in text nodes
  const walker = root.ownerDocument.createTreeWalker(root, NodeFilter.SHOW_TEXT);
  const textNodes: Text[] = [];
  let current: Node | null;
  while ((current = walker.nextNode())) {
    if (current.nodeType === Node.TEXT_NODE) {
      textNodes.push(current as Text);
    }
  }

  for (const node of textNodes) {
    const original = node.nodeValue ?? "";
    if (!original.includes("[[")) continue;
    const replaced = replaceMergeFieldsInString(original, input, report, loop);
    if (replaced !== original) {
      node.nodeValue = replaced;
    }
  }

  // Replace in attributes
  const elements = Array.from(root.querySelectorAll<HTMLElement>("*"));
  for (const el of elements) {
    for (const attr of Array.from(el.attributes)) {
      if (!attr.value.includes("[[")) continue;
      const replaced = replaceMergeFieldsInString(attr.value, input, report, loop);
      if (replaced !== attr.value) {
        el.setAttribute(attr.name, replaced);
      }
    }
  }
}

function replaceMergeFieldsInString(
  value: string,
  input: VitecRenderInput,
  report: VitecRenderReport,
  loop?: { loopVar: string; loopItem: Record<string, unknown> }
): string {
  return value.replace(MERGE_FIELD_REGEX, (_match, _requiredFlag: string, rawPath: string) => {
    const path = String(rawPath).trim();

    // Loop-scoped fields: [[selger.navn]] inside selger loop
    if (loop && path.startsWith(`${loop.loopVar}.`)) {
      const suffix = path.slice(loop.loopVar.length + 1);
      const v = getRecordValue(loop.loopItem, suffix);
      if (typeof v === "string") {
        report.merge_fields_replaced += 1;
        return v;
      }
      if (typeof v === "number") {
        report.merge_fields_replaced += 1;
        return String(v);
      }
      // fall back to leaving original marker
      return `[[${path}]]`;
    }

    const direct = input.values[path];
    if (direct !== undefined && direct !== null && String(direct).length > 0) {
      report.merge_fields_replaced += 1;
      return String(direct);
    }

    return `[[${path}]]`;
  });
}

function parseForeachExpression(expr: string): { itemVar: string; collectionPath: string } | null {
  // Pattern: "item in Model.collection.path"
  const match = expr.match(/^(\w+)\s+in\s+(.+)$/);
  if (!match) return null;
  const itemVar = match[1];
  const rhs = match[2].trim();

  // Only support Model.<path> for now
  if (rhs.startsWith("Model.")) {
    return { itemVar, collectionPath: rhs.slice("Model.".length) };
  }
  return null;
}

function safeEvalVitecExpression(expr: string, model: Record<string, unknown>): boolean | null {
  try {
    const tokens = tokenize(expr);
    if (tokens.some((t) => t.type === "unknown")) {
      return null;
    }
    const parser = new ExpressionParser(tokens, model);
    return parser.parseExpression();
  } catch {
    return null;
  }
}

function tokenize(expr: string): Token[] {
  const tokens: Token[] = [];
  let i = 0;

  const s = expr.trim();
  while (i < s.length) {
    const ch = s[i];

    // whitespace
    if (/\s/.test(ch)) {
      i += 1;
      continue;
    }

    if (ch === "(") {
      tokens.push({ type: "lparen" });
      i += 1;
      continue;
    }
    if (ch === ")") {
      tokens.push({ type: "rparen" });
      i += 1;
      continue;
    }

    // operators
    const two = s.slice(i, i + 2);
    if (two === "&&" || two === "||" || two === "==" || two === "!=" || two === ">=" || two === "<=") {
      tokens.push({ type: "op", value: two as OpToken });
      i += 2;
      continue;
    }
    if (ch === ">" || ch === "<") {
      tokens.push({ type: "op", value: ch as OpToken });
      i += 1;
      continue;
    }
    // strings
    if (ch === '"' || ch === "'") {
      const quote = ch;
      i += 1;
      let buf = "";
      while (i < s.length) {
        const c = s[i];
        if (c === "\\") {
          const next = s[i + 1];
          if (next) {
            buf += next;
            i += 2;
            continue;
          }
        }
        if (c === quote) {
          i += 1;
          break;
        }
        buf += c;
        i += 1;
      }
      tokens.push({ type: "string", value: buf });
      continue;
    }

    // numbers
    if (/[0-9]/.test(ch)) {
      let j = i;
      while (j < s.length && /[0-9.]/.test(s[j])) j += 1;
      const raw = s.slice(i, j);
      const num = Number(raw);
      if (Number.isFinite(num)) {
        tokens.push({ type: "number", value: num });
      } else {
        tokens.push({ type: "unknown", value: raw });
      }
      i = j;
      continue;
    }

    // identifiers / Model paths / booleans
    if (/[A-Za-z_]/.test(ch)) {
      let j = i;
      while (j < s.length && /[A-Za-z0-9_.]/.test(s[j])) j += 1;
      const raw = s.slice(i, j);
      const lower = raw.toLowerCase();

      if (lower === "true") {
        tokens.push({ type: "boolean", value: true });
      } else if (lower === "false") {
        tokens.push({ type: "boolean", value: false });
      } else if (raw.startsWith("Model.")) {
        const modelPathRaw = raw.slice("Model.".length);
        if (modelPathRaw.endsWith(".Count")) {
          tokens.push({ type: "model", path: modelPathRaw.slice(0, -".Count".length), isCount: true });
        } else {
          tokens.push({ type: "model", path: modelPathRaw, isCount: false });
        }
      } else {
        tokens.push({ type: "unknown", value: raw });
      }

      i = j;
      continue;
    }

    // any other character is unsupported
    tokens.push({ type: "unknown", value: s[i] });
    i += 1;
  }

  return tokens;
}

class ExpressionParser {
  private idx = 0;

  constructor(
    private readonly tokens: Token[],
    private readonly model: Record<string, unknown>
  ) {}

  parseExpression(): boolean {
    return this.parseOr();
  }

  private parseOr(): boolean {
    let left = this.parseAnd();
    while (this.matchOp("||")) {
      const right = this.parseAnd();
      left = left || right;
    }
    return left;
  }

  private parseAnd(): boolean {
    let left = this.parseComparison();
    while (this.matchOp("&&")) {
      const right = this.parseComparison();
      left = left && right;
    }
    return left;
  }

  private parseComparison(): boolean {
    const leftVal = this.parseTerm();
    const op = this.peekOp();
    if (!op || (op !== "==" && op !== "!=" && op !== ">=" && op !== "<=" && op !== ">" && op !== "<")) {
      return toBoolean(leftVal);
    }
    this.consume(); // op
    const rightVal = this.parseTerm();
    return compare(leftVal, rightVal, op);
  }

  private parseTerm(): unknown {
    const token = this.peek();
    if (!token) return undefined;

    if (token.type === "lparen") {
      this.consume();
      const value = this.parseExpression();
      if (this.peek()?.type === "rparen") this.consume();
      return value;
    }

    if (token.type === "string" || token.type === "number" || token.type === "boolean") {
      this.consume();
      return token.value;
    }

    if (token.type === "model") {
      this.consume();
      const resolved = getModelValue(this.model, token.path);
      if (token.isCount) {
        return Array.isArray(resolved) ? resolved.length : 0;
      }
      return resolved;
    }

    // unknown
    this.consume();
    return undefined;
  }

  private peek(): Token | undefined {
    return this.tokens[this.idx];
  }

  private consume(): Token | undefined {
    const t = this.tokens[this.idx];
    this.idx += 1;
    return t;
  }

  private peekOp(): OpToken | undefined {
    const t = this.peek();
    if (!t || t.type !== "op") return undefined;
    return t.value;
  }

  private matchOp(value: "&&" | "||"): boolean {
    const t = this.peek();
    if (t?.type === "op" && t.value === value) {
      this.consume();
      return true;
    }
    return false;
  }
}

function compare(left: unknown, right: unknown, op: "==" | "!=" | ">=" | "<=" | ">" | "<"): boolean {
  if (op === "==" || op === "!=") {
    const eq = looselyEqual(left, right);
    return op === "==" ? eq : !eq;
  }

  const ln = toNumber(left);
  const rn = toNumber(right);
  if (ln === null || rn === null) {
    return false;
  }

  switch (op) {
    case ">":
      return ln > rn;
    case "<":
      return ln < rn;
    case ">=":
      return ln >= rn;
    case "<=":
      return ln <= rn;
    default:
      return false;
  }
}

function looselyEqual(a: unknown, b: unknown): boolean {
  // booleans
  if (typeof a === "boolean" || typeof b === "boolean") {
    return toBoolean(a) === toBoolean(b);
  }
  // numbers
  const an = toNumber(a);
  const bn = toNumber(b);
  if (an !== null && bn !== null) {
    return an === bn;
  }
  // strings
  return String(a ?? "") === String(b ?? "");
}

function toBoolean(v: unknown): boolean {
  if (typeof v === "boolean") return v;
  if (typeof v === "number") return v !== 0;
  if (typeof v === "string") return v.length > 0 && v !== "0" && v.toLowerCase() !== "false";
  return Boolean(v);
}

function toNumber(v: unknown): number | null {
  if (typeof v === "number" && Number.isFinite(v)) return v;
  if (typeof v === "string") {
    const n = Number(v);
    return Number.isFinite(n) ? n : null;
  }
  return null;
}

function getModelValue(model: Record<string, unknown>, path: string): unknown {
  const parts = path.split(".").filter(Boolean);
  let current: unknown = model;
  for (const part of parts) {
    if (!isRecord(current)) return undefined;
    current = current[part];
  }
  return current;
}

function getRecordValue(record: Record<string, unknown>, path: string): unknown {
  const parts = path.split(".").filter(Boolean);
  let current: unknown = record;
  for (const part of parts) {
    if (!isRecord(current)) return undefined;
    current = current[part];
  }
  return current;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

