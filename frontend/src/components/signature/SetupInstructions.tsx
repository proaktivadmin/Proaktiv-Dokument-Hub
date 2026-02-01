"use client";

import { useCallback, useEffect, useState } from "react";
import { ChevronDown, Monitor, Smartphone } from "lucide-react";
import { Button } from "@/components/ui/button";

type PcOs = "windows" | "mac";
type PhoneOs = "ios" | "android";

const PC_STORAGE_KEY = "signature-pc-os";
const PHONE_STORAGE_KEY = "signature-phone-os";

function detectPcOs(): PcOs {
  if (typeof navigator === "undefined") return "windows";
  const ua = (navigator.platform || navigator.userAgent).toLowerCase();
  return /mac/i.test(ua) ? "mac" : "windows";
}

function detectPhoneOs(): PhoneOs {
  if (typeof navigator === "undefined") return "ios";
  return /android/i.test(navigator.userAgent) ? "android" : "ios";
}

function loadOrDetect<T extends string>(key: string, detect: () => T): T {
  if (typeof window === "undefined") return detect();
  const stored = localStorage.getItem(key);
  if (stored === "windows" || stored === "mac" || stored === "ios" || stored === "android") {
    return stored as T;
  }
  return detect();
}

interface ToggleButtonsProps<T extends string> {
  value: T;
  onChange: (v: T) => void;
  options: { value: T; label: string }[];
}

function ToggleButtons<T extends string>({ value, onChange, options }: ToggleButtonsProps<T>) {
  return (
    <div className="flex gap-1 rounded-lg bg-muted p-1">
      {options.map((opt) => (
        <button
          key={opt.value}
          type="button"
          onClick={() => onChange(opt.value)}
          className={`rounded-md px-3 py-1.5 text-xs font-medium transition-colors duration-fast ease-standard ${
            value === opt.value
              ? "bg-background text-foreground shadow-sm"
              : "text-muted-foreground hover:text-foreground"
          }`}
        >
          {opt.label}
        </button>
      ))}
    </div>
  );
}

export function SetupInstructions() {
  const [pcOs, setPcOs] = useState<PcOs>(() => loadOrDetect(PC_STORAGE_KEY, detectPcOs));
  const [phoneOs, setPhoneOs] = useState<PhoneOs>(() => loadOrDetect(PHONE_STORAGE_KEY, detectPhoneOs));

  const handlePcChange = useCallback((v: PcOs) => {
    setPcOs(v);
    localStorage.setItem(PC_STORAGE_KEY, v);
  }, []);

  const handlePhoneChange = useCallback((v: PhoneOs) => {
    setPhoneOs(v);
    localStorage.setItem(PHONE_STORAGE_KEY, v);
  }, []);

  // Sync initial detection to localStorage on mount
  useEffect(() => {
    if (!localStorage.getItem(PC_STORAGE_KEY)) {
      localStorage.setItem(PC_STORAGE_KEY, pcOs);
    }
    if (!localStorage.getItem(PHONE_STORAGE_KEY)) {
      localStorage.setItem(PHONE_STORAGE_KEY, phoneOs);
    }
  }, [pcOs, phoneOs]);

  return (
    <details className="group rounded-lg border bg-white shadow-card ring-1 ring-black/3">
      <summary className="flex cursor-pointer items-center justify-between gap-3 px-6 py-4 text-sm font-medium text-foreground transition-colors duration-fast ease-standard hover:text-foreground">
        <span>Slik legger du inn signaturen</span>
        <ChevronDown className="h-4 w-4 text-muted-foreground transition-transform duration-fast ease-standard group-open:rotate-180" />
      </summary>
      <div className="space-y-6 border-t px-6 py-4 text-sm text-muted-foreground">
        {/* Platform selectors */}
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:gap-6">
          <div className="flex items-center gap-2">
            <Monitor className="h-4 w-4 text-muted-foreground" />
            <span className="text-xs font-medium text-foreground">PC:</span>
            <ToggleButtons
              value={pcOs}
              onChange={handlePcChange}
              options={[
                { value: "windows" as PcOs, label: "Windows" },
                { value: "mac" as PcOs, label: "Mac" },
              ]}
            />
          </div>
          <div className="flex items-center gap-2">
            <Smartphone className="h-4 w-4 text-muted-foreground" />
            <span className="text-xs font-medium text-foreground">Telefon:</span>
            <ToggleButtons
              value={phoneOs}
              onChange={handlePhoneChange}
              options={[
                { value: "ios" as PhoneOs, label: "iPhone" },
                { value: "android" as PhoneOs, label: "Android" },
              ]}
            />
          </div>
        </div>

        {/* PC Instructions */}
        <div className="space-y-4">
          <p className="text-xs font-semibold uppercase tracking-wider text-foreground/60">
            PC – {pcOs === "windows" ? "Windows" : "Mac"}
          </p>

          {pcOs === "windows" && (
            <>
              <InstructionBlock
                title="Outlook (ny versjon)"
                steps={[
                  "Klikk på tannhjulikonet (Innstillinger) øverst til høyre.",
                  "Velg «Kontoer» → «Signaturer».",
                  "Klikk «+ Ny signatur» og gi den et navn.",
                  "Lim inn signaturen (Ctrl+V) i redigeringsfeltet.",
                  "Velg signaturen som standard for nye e-poster og svar, og klikk «Lagre».",
                ]}
              />
              <InstructionBlock
                title="Outlook (klassisk)"
                steps={[
                  "Gå til Fil → Alternativer → E-post → Signaturer.",
                  "Klikk «Ny», gi signaturen et navn.",
                  "Lim inn signaturen (Ctrl+V) i redigeringsfeltet.",
                  "Velg signaturen som standard under «Velg standardsignatur».",
                  "Klikk «OK» for å lagre.",
                ]}
              />
            </>
          )}

          {pcOs === "mac" && (
            <>
              <InstructionBlock
                title="Outlook for Mac"
                steps={[
                  "Åpne Outlook → Innstillinger (⌘,) → Signaturer.",
                  "Klikk «+» for å opprette en ny signatur.",
                  "Lim inn signaturen (⌘V) i redigeringsfeltet.",
                  "Gi signaturen et navn og lukk vinduet.",
                  "Signaturen velges automatisk, eller velg den under «Ny melding»-innstillinger.",
                ]}
              />
              <InstructionBlock
                title="Apple Mail"
                steps={[
                  "Åpne Mail → Innstillinger (⌘,) → Signaturer.",
                  "Velg e-postkontoen din i venstre kolonne.",
                  "Klikk «+» for å opprette en ny signatur.",
                  "Lim inn signaturen (⌘V) i redigeringsfeltet til høyre.",
                  "Fjern haken for «Bruk alltid standardskrift» hvis den er på.",
                  "Velg signaturen i nedtrekkslisten «Velg signatur» for kontoen.",
                ]}
              />
            </>
          )}
        </div>

        {/* Phone Instructions */}
        <div className="space-y-4">
          <p className="text-xs font-semibold uppercase tracking-wider text-foreground/60">
            Telefon – {phoneOs === "ios" ? "iPhone" : "Android"}
          </p>

          {phoneOs === "ios" && (
            <>
              <InstructionBlock
                title="Mail-appen (iOS)"
                steps={[
                  "Åpne Innstillinger → Mail → Signatur.",
                  "Velg kontoen du vil endre signatur for.",
                  "Slett eksisterende tekst og lim inn den nye signaturen.",
                  "Gå tilbake for å lagre.",
                ]}
                note="Merk: iOS Mail støtter kun enkel tekst-formatering. For best resultat, sett opp signaturen på PC først."
              >
                <Button
                  variant="outline"
                  size="sm"
                  className="mt-2"
                  asChild
                >
                  <a href="App-Prefs:root=MAIL&path=Compose">
                    Åpne Mail-innstillinger
                  </a>
                </Button>
              </InstructionBlock>
              <InstructionBlock
                title="Outlook-appen (iOS)"
                steps={[
                  "Åpne Outlook-appen og trykk på profilbildet ditt øverst til venstre.",
                  "Trykk på tannhjulikonet (Innstillinger) nederst.",
                  "Scroll ned og trykk «Signatur».",
                  "Slett eksisterende tekst og lim inn den nye signaturen.",
                  "Trykk «Ferdig» eller gå tilbake for å lagre.",
                ]}
              />
            </>
          )}

          {phoneOs === "android" && (
            <>
              <InstructionBlock
                title="Gmail-appen"
                steps={[
                  "Åpne Gmail → trykk på hamburgermenyen (≡) → Innstillinger.",
                  "Velg e-postkontoen din.",
                  "Trykk «Mobilsignatur».",
                  "Slett eksisterende tekst og lim inn den nye signaturen.",
                  "Trykk «OK» for å lagre.",
                ]}
                note="Gmail-appen på Android støtter kun ren tekst i signaturer."
              />
              <InstructionBlock
                title="Outlook-appen (Android)"
                steps={[
                  "Åpne Outlook-appen og trykk på profilbildet ditt øverst til venstre.",
                  "Trykk på tannhjulikonet (Innstillinger).",
                  "Trykk «Signatur» under e-postinnstillinger.",
                  "Slett eksisterende tekst og lim inn den nye signaturen.",
                  "Trykk tilbakeknappen for å lagre.",
                ]}
              />
            </>
          )}
        </div>
      </div>
    </details>
  );
}

interface InstructionBlockProps {
  title: string;
  steps: string[];
  note?: string;
  children?: React.ReactNode;
}

function InstructionBlock({ title, steps, note, children }: InstructionBlockProps) {
  return (
    <div className="space-y-2">
      <p className="font-medium text-foreground">{title}</p>
      <ol className="list-decimal space-y-1 pl-4">
        {steps.map((step, i) => (
          <li key={i}>{step}</li>
        ))}
      </ol>
      {note && (
        <p className="text-xs text-muted-foreground/70 italic">{note}</p>
      )}
      {children}
    </div>
  );
}
