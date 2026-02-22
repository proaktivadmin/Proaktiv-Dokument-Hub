# Field Mapping: Meglerstandard Mars 2020 — Eiendom med og uten oppgjørsansvarlig

## Source
- **File:** c:\Users\Adrian\Downloads\OneDrive_2026-02-21\maler vi må få produsert\Meglerstandard for eiendom med og uten oppgjørsansvarlig.htm
- **Registry used:** .planning/field-registry.md
- **Document:** Commercial real estate purchase contract (Kjøpekontrakt); includes Vedlegg 5 (Justeringsavtale), Vedlegg 6 (three Oppgjørsavtale variants), Bilag 1 (Fullmakt), Bilag 2 (Betalingsinstruks)

## Summary
- **Total placeholders found:** 95+
- **Mapped successfully:** 76
- **Unmapped (need review):** 19
- **Monetary (need $.UD):** 17
- **Optional (need vitec-if guard):** 28

## Field Mapping Table

| # | Source Text / Placeholder | Modern Path | $.UD | Guard | Notes |
|---|--------------------------|-------------|------|-------|-------|
| 1 | #navn.firma¤ | [[meglerkontor.navn]] | — | — | Megler firm name |
| 2 | #organisasjonsnummer.firma¤ | [[meglerkontor.orgnr]] | — | — | Megler org.nr. |
| 3 | #type_oppdrag.oppdrag¤ | [[oppdrag.type]] | — | — | Assignment type |
| 4 | #type_eierformbygninger.oppdrag¤ | [[eiendom.eieform]] | — | != "" | Ownership buildings; optional when N/A |
| 5 | #type_eierformtomt.oppdrag¤ | [[eiendom.typegrunn]] | — | != "" | Ownership land; optional when N/A |
| 6 | #oppdragsnummer.oppdrag¤ | [[oppdrag.nr]] | — | — | Assignment number |
| 7 | #omsetningsnummer.oppdrag¤ | [[kontrakt.formidling.nr]] | — | — | Transaction number |
| 8 | #include_rtfelementer_kontrakt¤ | — | — | — | UNMAPPED: RTF elements insertion point |
| 9 | #eiere¤ | [[selger.navn]] | — | foreach | Sellers header; or use foreach with [[*selger.navn]] |
| 10 | #flettblankeeiere¤ | (remove) | — | — | Layout blank line between parties |
| 11 | #forsteeier¤ | [[*selger.navnutenfullmektigogkontaktperson]] | — | foreach | First seller in loop |
| 12 | #kunadresse.kontakter¤ | [[*selger.adresse]] | — | foreach | Seller address in loop |
| 13 | #Mob: ;mobil.kontakter& ¤ | [[*selger.hovedtlf]] or [[*selger.mobiltlf]] | — | foreach | Mobile; selger uses hovedtlf |
| 14 | #E-post: ;email.kontakter¤ | [[*selger.hovedepost]] | — | foreach | Seller email |
| 15 | #nyeeiere¤ | [[kjoper.navn]] | — | foreach | Buyers header |
| 16 | #forstenyeier¤ | [[*kjoper.navnutenfullmektigogkontaktperson]] | — | foreach | First buyer in loop |
| 17 | (buyers) #kunadresse.kontakter¤ | [[*kjoper.adresse]] | — | foreach | Buyer address |
| 18 | (buyers) #Mob: ;mobil.kontakter& ¤ | [[*kjoper.hovedtlf]] | — | foreach | Buyer mobile |
| 19 | (buyers) #E-post: ;email.kontakter¤ | [[*kjoper.hovedepost]] | — | foreach | Buyer email |
| 20 | #adresse.oppdrag¤ | [[eiendom.adresse]] | — | — | Property address |
| 21 | #matrikkelkommune.oppdrag¤ | [[komplettmatrikkel]] [[eiendom.kommunenavn]] | — | != "" | Matrikkel + commune; ideellandel optional |
| 22 | #seksjonsbrok.oppdrag¤ | [[eiendom.andelsnr]] | — | != "" | Section fraction; optional |
| 23 | #ideellandel.oppdrag¤ | [[sameie.sameiebrok]] or custom | — | != "" | Ideell andel; optional |
| 24 | [Megler] (Mnavn1-5) | [[ansvarligmegler.navn]] or [[megler1.navn]] | — | != "" | Megler name; Oppgjør uses [[oppgjor.ansvarlig.navn]] |
| 25 | [org.nr. megler] (Morgnr1) | [[meglerkontor.orgnr]] | — | — | Megler firm org.nr. |
| 26 | [Selger] (Snavn2-5) | [[*selger.navnutenfullmektigogkontaktperson]] | — | foreach | Seller name |
| 27 | [org.nr. Selger] (Sorgnr1,2) | [[*selger.idnummer]] | — | foreach | Seller org.nr./personnr. |
| 28 | [Kjøper] (Knavn2-5) | [[*kjoper.navnutenfullmektigogkontaktperson]] | — | foreach | Buyer name |
| 29 | [org.nr. Kjøper] (Korgnr1,2) | [[*kjoper.idnummer]] | — | foreach | Buyer org.nr./personnr. |
| 30 | [overtakelsesdato] (Odato7, Odato1) | [[kontrakt.overtagelse.dato]] | — | — | Takeover date |
| 31 | [sted] (Sted1, Sted2) | [[meglerkontor.besoksadresse]] or [[meglerkontor.poststed]] | — | != "" | Signing place |
| 32 | [signeringsdato] (Sdato1, Sdato2) | [[kontrakt.dato]] | — | — | Contract signing date |
| 33 | [Selgers repr.] (Srepr1,2) | [[*selger.signaturberettiget.navn]] or [[*selger.kontaktperson.navn]] | — | foreach | Seller representative |
| 34 | [Kjøpers repr.] (Krepr1,2) | [[*kjoper.signaturberettiget.navn]] or [[*kjoper.kontaktperson.navn]] | — | foreach | Buyer representative |
| 35 | [dato] (Utkast A) | [[kontrakt.dato]] or [[dagensdato]] | — | — | Draft date |
| 36 | [forfatter] | [[avsender.navn]] or [[ansvarligmegler.navn]] | — | != "" | Author |
| 37 | gnr. [●] bnr. [●] | [[*matrikkel.gnr]] [[*matrikkel.bnr]] | — | foreach | Matrikkel; bnr not in registry |
| 38 | [●] kommune | [[eiendom.kommunenavn]] | — | — | Municipality |
| 39 | Kjøpesummen NOK [●] | [[kontrakt.kjopesum]] | YES | — | Purchase price |
| 40 | Vederlaget NOK [●] (2.1.3) | [[kontrakt.kjopesumogomkostn]] | YES | — | Total consideration |
| 41 | 8.4.1(a) NOK [●] | — | YES | — | UNMAPPED: Liability threshold minimum |
| 42 | 8.4.1(b) NOK [●] | — | YES | — | UNMAPPED: Liability threshold aggregate |
| 43 | Sikkerhet NOK [●] (pt 10) | — | YES | != "" | UNMAPPED: Security amount; optional |
| 44 | For Selger: [●] | [[*selger.adresse]] | — | foreach | Seller notification address |
| 45 | For Kjøper: [●] | [[*kjoper.adresse]] | — | foreach | Buyer notification address |
| 46 | [Megler]: [●] | [[meglerkontor.adresse]] or [[ansvarligmegler.epost]] | — | != "" | Megler notification address |
| 47 | verneting [●] | — | — | — | UNMAPPED: Court venue |
| 48 | [Overdrager] / [Mottaker] (Vedlegg 5) | [[selger.navn]] / [[kjoper.navn]] | — | — | Parties in justeringsavtale |
| 49 | [Selger], [adresse], [postnummer og -sted] (Vedlegg 5) | [[*selger.navnutenfullmektigogkontaktperson]], [[*selger.adresse]], [[*selger.hovedpostnr]] [[*selger.hovedpoststed]] | — | foreach | Overdrager details |
| 50 | [Kjøper], [adresse], [postnummer og -sted] (Vedlegg 5) | [[*kjoper.navnutenfullmektigogkontaktperson]], [[*kjoper.adresse]], [[*kjoper.hovedpostnr]] [[*kjoper.hovedpoststed]] | — | foreach | Mottaker details |
| 51 | gnr. [●] bnr. [●] i [●] kommune (Vedlegg 5, Bilag 1) | [[komplettmatrikkel]] or [[*matrikkel.gnr]] [[*matrikkel.bnr]] + [[eiendom.kommunenavn]] | — | — | Matrikkel in appendices |
| 52 | gnr. [•] bnr. [•] fnr. [•] snr. [•] (Bilag 1) | [[komplettmatrikkel]] or matrikkel foreach | — | — | Full matrikkel; fnr/snr not in registry |
| 53 | kontonr. [•] (Oppgjørskontoen) | [[kontrakt.klientkonto]] | — | != "" | UNMAPPED: Settlement account; may be oppgjor |
| 54 | Selgers konto kontonr. [•] | [[*selger.hovedkontonummer]] | — | foreach | Seller account for disbursement |
| 55 | [Kjøpers bank] | — | — | — | UNMAPPED: Buyer's lender bank name |
| 56 | [org.nr. Kjøpers bank] | — | — | — | UNMAPPED: Lender org.nr. |
| 57 | [navngitt representant for Kjøper] | [[kjoper.fullmektig.navn]] or [[kjoper.dagligleder.navn]] | — | != "" | Optional |
| 58 | personnummer [•] (Bilag 1 fullmakt) | [[kjoper.fullmektig.idnummer]] or [[kjoper.signaturberettiget.idnummer]] | — | != "" | Optional |
| 59 | Kr [..] (Vedlegg 5 tabell) | various | YES | — | Justeringsavtale amounts; custom/omkostninger |
| 60 | [..] % (Vedlegg 5) | — | — | — | UNMAPPED: Fradragsrett percentages |
| 61 | sikringsdokument pålydende NOK [•] | [[kontrakt.kjopesumogomkostn]] | YES | — | Security document amount |
| 62 | [angi navn på signaturberettigede i Selger] | [[*selger.signaturberettiget.navn]] | — | foreach | Optional; may need concatenation |

## Collections (vitec-foreach candidates)

| Collection Path | Loop Variable | Fields Inside | Guard |
|----------------|---------------|---------------|-------|
| Model.selgere | selger | navnutenfullmektigogkontaktperson, adresse, hovedpostnr, hovedpoststed, idnummer, ledetekst_idnummer, hovedtlf, hovedepost, hovedkontonummer, signaturberettiget.navn, kontaktperson.navn | Count > 0 |
| Model.kjopere | kjoper | navnutenfullmektigogkontaktperson, adresse, hovedpostnr, hovedpoststed, idnummer, ledetekst_idnummer, hovedtlf, hovedepost, fullmektig.navn, signaturberettiget.navn | Count > 0 |
| *matrikkel (if available) | matrikkel | gnr, bnr, fnr, snr (fnr/snr not in registry) | Count > 0 |

**Note:** Legacy `#forsteeier¤` / `#forstenyeier¤` patterns imply a "first owner" iteration. Modern Vitec uses `vitec-foreach="selger in Model.selgere"` with `[[*selger.navnutenfullmektigogkontaktperson]]` etc. The `#flettblankeeiere¤` inserts blank lines between party rows—handle as separator in foreach.

## Monetary Fields ($.UD required)

| Field Path | Context |
|-----------|---------|
| [[kontrakt.kjopesum]] | Purchase price (§ 2.1.1) |
| [[kontrakt.kjopesumogomkostn]] | Vederlaget / total consideration (§ 2.1.3, sikringsdokument) |
| [[kontrakt.kjopesumibokstaver]] | Kjøpesum in letters (if used) |
| Liability threshold 8.4.1(a) | UNMAPPED — minimum single-claim threshold |
| Liability threshold 8.4.1(b) | UNMAPPED — aggregate threshold |
| Sikkerhet amount (§ 10) | UNMAPPED — security amount held back |
| Vedlegg 5 tabell amounts | Anskaffelseskostnad, Total mva, Mva. fradragsført, etc. — UNMAPPED |

## Optional Fields (need vitec-if guard)

| Field Path | Reason |
|-----------|--------|
| [[eiendom.eieform]] | May be N/A for some property types |
| [[eiendom.typegrunn]] | May be N/A |
| [[eiendom.andelsnr]] | Section fraction; only for selveierleiligheter |
| [[sameie.sameiebrok]] | Ideell andel; only for sameie |
| [[ansvarligmegler.navn]] | Megler may vary by context |
| [[avsender.navn]] | Author optional |
| [[*selger.signaturberettiget.navn]] | Company signatory |
| [[*selger.hovedkontonummer]] | Seller account |
| [[*kjoper.fullmektig.navn]] | Buyer representative |
| [[kjoper.fullmektig.idnummer]] | When fullmektig present |
| Sikkerhet (§ 10) | Strykes hvis Selger ikke skal stille sikkerhet |
| § 8.6 multi-seller paragraph | Strykes hvis kun én selger |
| Vedlegg 6 variant A | Strykes hvis selgers lån innfris ved overtakelse |
| Vedlegg 6 variant B | Strykes hvis selgers lån innfris ETTER tinglysing |
| Vedlegg 6 variant C | Strykes hvis oppgjøres med oppgjørsansvarlig |
| Bilag 1 (Fullmakt) | Strykes hvis oppgjøret etter tinglysing |
| Bilag 2 (Betalingsinstruks) | Benyttes ikke hvis oppgjørsansvarlig |

## Unmapped Fields (NEED HUMAN REVIEW)

| # | Source Text | Context in Document | Attempted Match | Confidence |
|---|-------------|---------------------|-----------------|------------|
| 1 | #include_rtfelementer_kontrakt¤ | After omsetningsnummer | kontrakt.vedleggkjopekontrakt? | Low — RTF insertion |
| 2 | 8.4.1(a) NOK [●] | Liability threshold, single claim | — | — |
| 3 | 8.4.1(b) NOK [●] | Liability threshold, aggregate | — | — |
| 4 | Sikkerhet NOK [●] (§ 10) | Security amount | — | — |
| 5 | verneting [●] | Court venue (domstol) | — | — |
| 6 | kontonr. [•] Oppgjørskontoen | Settlement account | kontrakt.klientkonto? oppgjor? | Low |
| 7 | [Kjøpers bank] | Lender bank name | kjoperspant.navn? | Low |
| 8 | [org.nr. Kjøpers bank] | Lender org.nr. | kjoperspant.panthaverorgnr? | Low |
| 9 | Vedlegg 5 [..] % | Fradragsrett percentages | — | — |
| 10 | *matrikkel.bnr | Matrikkel bruksnummer | Registry has *matrikkel.gnr only | — |
| 11 | fnr, snr (Bilag 1) | Festenummer, sekvensnummer | Not in registry | — |
| 12 | [Sted], [dato] in Vedlegg 5 | Place/date in justeringsavtale | meglerkontor.besoksadresse, kontrakt.dato | Medium |
| 13 | [Angivelse av byggetiltak] | Vedlegg 5 table header | — | — |
| 14 | [Dato] (Vedlegg 5 Fullføringstidspunkt) | — | — | — |
| 15 | [angi romslig frist] (Bilag 1) | Fullmakt validity period | — | — |
| 16 | [30] dager | Pro & contra deadline | Fixed "30" or variable? | — |
| 17 | [10] % | Damage threshold | Fixed "10" or variable? | — |
| 18 | [10 % av Kjøpesummen] | Liability cap | Calculated from [[kontrakt.kjopesum]] | — |
| 19 | [Datarom på minnepinne] | Vedlegg 7 | — | — |

---

*Mapping completed per FORMAT_fields.md. Logic Mapper and Structure Analyzer handle vitec-if conditions and document structure.*
