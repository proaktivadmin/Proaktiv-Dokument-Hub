/**
 * Vitec Next - Kunderelasjonstyper (Receivers)
 * Source: .cursor/vitec-reference.md
 */

export interface ReceiverType {
  id: number;
  name: string;
  reserved_for?: string | null;
  group?: string | null;
  ranking?: string | null;
  rules?: string | null;
  source?: "Vitec" | "Custom";
}

export const RECEIVER_TYPES: ReceiverType[] = [
  { id: 1, name: "Selger", reserved_for: "Selger", group: "Selger", ranking: "1", rules: null, source: "Vitec" },
  { id: 2, name: "Kjøper", reserved_for: "Kjøper", group: "Kjøper", ranking: "2", rules: "Leadsoppfølging", source: "Vitec" },
  { id: 3, name: "Visningsdeltager", reserved_for: "Visningsdeltaker", group: "Visningsdeltaker", ranking: "-", rules: "Budoppfølging, Leadsoppfølging", source: "Vitec" },
  { id: 4, name: "Budgiver", reserved_for: "Budgiver", group: "Budgiver", ranking: "3", rules: "Budoppfølging, Leadsoppfølging", source: "Vitec" },
  { id: 5, name: "Interessent", reserved_for: "-", group: "Interessent", ranking: "-", rules: "Visningsinvitasjon, Budoppfølging", source: "Vitec" },
  { id: 6, name: "Interessent - Match", reserved_for: "-", group: "Match", ranking: "-", rules: null, source: "Vitec" },
  { id: 7, name: "Utleier", reserved_for: "-", group: "Selger", ranking: "-", rules: "Utleie", source: "Vitec" },
  { id: 8, name: "Leietaker", reserved_for: "-", group: "Kjøper", ranking: "-", rules: "Utleie, Leadsoppfølging", source: "Vitec" },
  { id: 9, name: "Borettslag", reserved_for: "-", group: "Borettslag/Sameie/Aksjelag", ranking: "-", rules: null, source: "Vitec" },
  { id: 11, name: "Bank - selger", reserved_for: "-", group: "Panthaver", ranking: "-", rules: null, source: "Vitec" },
  { id: 12, name: "Forretningsfører", reserved_for: "-", group: "Forretningsfører", ranking: "-", rules: null, source: "Vitec" },
  { id: 13, name: "Bank - kjøper", reserved_for: "-", group: "Panthaver", ranking: "-", rules: null, source: "Vitec" },
  { id: 14, name: "Ikke interessert", reserved_for: "-", group: "Interessent", ranking: "-", rules: null, source: "Vitec" },
  { id: 15, name: "Hjemmelshaver", reserved_for: "-", group: "Hjemmelshaver", ranking: "-", rules: null, source: "Vitec" },
  { id: 16, name: "Panthaver", reserved_for: "-", group: "Panthaver", ranking: "-", rules: null, source: "Vitec" },
  { id: 17, name: "Saksøkt", reserved_for: "-", group: "Saksøkt", ranking: "-", rules: null, source: "Vitec" },
  { id: 18, name: "Kreditor", reserved_for: "-", group: "-", ranking: "-", rules: null, source: "Vitec" },
  { id: 19, name: "Prosessfullmektig", reserved_for: "-", group: "Prosessfullmektig", ranking: "-", rules: null, source: "Vitec" },
  { id: 20, name: "Saksøker", reserved_for: "-", group: "Saksøker", ranking: "-", rules: null, source: "Vitec" },
  { id: 21, name: "Opprinnelig kjøper", reserved_for: "-", group: "Opprinnelig kjøper", ranking: "-", rules: "Leadsoppfølging", source: "Vitec" },
  { id: 22, name: "Fremleier", reserved_for: "-", group: "-", ranking: "-", rules: "Leadsoppfølging", source: "Vitec" },
  { id: 23, name: "Fremleietaker", reserved_for: "-", group: "-", ranking: "-", rules: "Leadsoppfølging", source: "Vitec" },
  { id: 24, name: "Takstmann", reserved_for: "-", group: "Bygningssakkyndig", ranking: "-", rules: null, source: "Vitec" },
  { id: 25, name: "Sameie", reserved_for: "-", group: "Borettslag/Sameie/Aksjelag", ranking: "-", rules: null, source: "Vitec" },
  { id: 26, name: "Aksjeselskap", reserved_for: "-", group: "Borettslag/Sameie/Aksjelag", ranking: "-", rules: null, source: "Vitec" },
  { id: 27, name: "Kommune", reserved_for: "-", group: "-", ranking: "-", rules: null, source: "Vitec" },
  { id: 28, name: "Interessent - budoppfølging", reserved_for: "-", group: "Interessent", ranking: "-", rules: "Visningsinvitasjon, Budoppfølging", source: "Vitec" },
  { id: 29, name: "Interessent - autoprospekt", reserved_for: "-", group: "Interessent", ranking: "-", rules: "Visningsinvitasjon", source: "Vitec" },
  { id: 30, name: "Fester", reserved_for: "-", group: "Fester", ranking: "-", rules: null, source: "Vitec" },
  { id: 31, name: "Fakturamottaker", reserved_for: "-", group: "Fakturamottaker", ranking: "-", rules: null, source: "Vitec" },
  { id: 32, name: "Hjemmelsutsteder", reserved_for: "-", group: "Hjemmelsutsteder", ranking: "-", rules: null, source: "Vitec" },
  { id: 33, name: "Fullmektig", reserved_for: "-", group: "Fullmektig", ranking: "-", rules: null, source: "Vitec" },
  { id: 34, name: "Grunneier", reserved_for: "-", group: "Grunneier", ranking: "-", rules: null, source: "Vitec" },
  { id: 36, name: "Tidligere eier/avdød", reserved_for: "-", group: "Tidligere eier / avdød", ranking: "-", rules: null, source: "Vitec" },
  { id: 37, name: "Arving", reserved_for: "-", group: "Arving", ranking: "-", rules: null, source: "Vitec" },
  { id: 38, name: "Selgers ektefelle", reserved_for: "-", group: "Selgers ektefelle", ranking: "-", rules: null, source: "Vitec" },
  { id: 39, name: "Kontodisponent selger", reserved_for: "-", group: "Disponent selger/utleier", ranking: "-", rules: null, source: "Vitec" },
  { id: 40, name: "Kontodisponent kjøper", reserved_for: "-", group: "Disponent kjøper/leietaker", ranking: "-", rules: null, source: "Vitec" },
  // Extra receiver commonly referenced in workflows
  { id: 1000, name: "Kartverket", reserved_for: "Kartverket", group: "Offentlig", ranking: "-", rules: null, source: "Custom" },
];

export const RECEIVER_GROUPS = Array.from(
  new Set(RECEIVER_TYPES.map((r) => r.group || "-"))
);
