import type { SignatureVersion } from "@/hooks/v3/useSignature";

export const VERSION_LABELS: Record<SignatureVersion, string> = {
  "with-photo": "Med bilde",
  "no-photo": "Uten bilde",
};

export function buildSignatureDoc(html: string): string {
  return `<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <style>
      body {
        margin: 0;
        padding: 12px;
        background: white;
        font-family: Arial, sans-serif;
      }
    </style>
  </head>
  <body>${html}</body>
</html>`;
}
