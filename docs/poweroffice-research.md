# PowerOffice Go (POGO) – Research og referanse

> **Agent-kontekst:** Dette dokumentet er primær referanse for PowerOffice Go (POGO) i Proaktiv Dokument Hub-konteksten. Bruk ved spørsmål om bankintegrasjon, EHF-faktura, Vitec Next-integrasjon, eller optimalisering av regnskapsflyt for eiendomsmegling.

**Sist oppdatert:** 2026-03-10  
**Kontekst:** Proaktiv har 19 megleravdelinger i både POGO og Vitec Next. Azets er revisor/regnskapsfører-partner. Nylig overgang til POGO + Vitec Next.

---

## 1. Oversikt

| Aspekt | Verdi |
|--------|------|
| **Løsning** | PowerOffice Go (POGO) |
| **Leverandør** | PowerOffice (Visma) |
| **Type** | Skybasert regnskapssystem |
| **Integrasjon** | Vitec Next (meglersystem) |
| **Revisor** | Azets (PowerOffice Premium Partner) |
| **Avdelinger** | 19 megleravdelinger |

---

## 2. Bankintegrasjon – Norske banker

### 2.1 Direkteintegrasjon (støttede banker)

PowerOffice tilbyr **direkteintegrasjon** med over 30 norske banker. Hovedfunksjoner:
- Automatisk bankavstemming
- Direkte remittering
- Regnskapsgodkjente betalinger (BankID)
- Utenlandsbetalinger og alle valutaer

**Storbanker:**
- DNB
- Nordea
- Danske Bank
- Handelsbanken
- SEB
- Swedbank

**Sparebanker og andre:**
BN Bank, Boligbanken, Cultura Bank, EIKA, Etne Sparebank, Fana Sparebank, Flekkefjord Sparebank, Haugesund Sparebank, Landkreditt Bank, Lillesands Sparebank, LokalBank-alliansen, Luster Sparebank, Næringsbanken, Pareto Bank, Skudenes & Aakra Sparebank, **SpareBank 1**, SpareBank 1 Helgeland, Sparebanken Møre, Sparebanken Sogn og Fjordane, Sparebanken Sør, Sparebanken Vest, Sparebanken Øst, Spareskillingsbanken, Søgne og Greipstad Sparebank, Voss Sparebank.

**PowerOffice support (bank):**  
https://support.poweroffice.com/hc/no/sections/115001449226-Direkteintegrasjon-bank

### 2.2 Tekniske krav for bankintegrasjon

- **Betalingsgodkjenning:** Bankkonto må ha remitteringsavtale
- **BankID:** Brukere må verifiseres med BankID for betalingsgodkjenning
- **Bankavstemming:** Importerte filer må være konsekutive (inngående saldo = utgående saldo fra forrige fil)
- **KAR/AML:** PowerOffice integrerer med KAR (Kontonummer- og adresseregister) for kontoverifisering

### 2.3 Sjekkliste – Er bankoppsettet optimalisert?

- [ ] Er alle 19 avdelingers bankkontoer koblet til POGO med direkteintegrasjon?
- [ ] Er regnskapsgodkjente betalinger aktivert (BankID)?
- [ ] Er bankavstemming satt til automatisk import?
- [ ] Er klientkontoer (klientmidler) aktivert med klientansvar per avdeling?
- [ ] Bruker dere samme bank som har direkteintegrasjon, eller en bank uten støtte?

---

## 3. EHF-faktura – Automatisk mottak og bokføring

### 3.1 Hva POGO tilbyr

- **Automatisk mottak** av EHF-fakturaer
- **100 % nøyaktig** datainnlesning (ingen manuell inntasting)
- **Automatisk bokføring** ved mottak
- **EHF-sending** til kunder (organisasjonsnummer + ELMA-sjekk)

### 3.2 Tekniske krav

| Krav | Verdi |
|------|-------|
| PowerOffice versjon | 28.5 eller nyere |
| PowerOffice ServerService | 4.5.3 eller nyere |
| Leveringsmetode | "EHF Faktura" |
| Kundens org.nr | Obligatorisk |
| "Deres referanse" | Obligatorisk for EHF |

### 3.3 Peppol/EHF-aksesspunkt

For å **motta** EHF-fakturaer må POGO kobles til et **Peppol-aksesspunkt** (sertifisert tjeneste). PowerOffice er ikke selv aksesspunkt for mottak.

**Aksesspunkt-leverandører (eksempler):**
- **Logiq** – DFØ-godkjent "Best Practice"
- **Amili Access Point** – DFØ-godkjent, ca. 549 kr/mnd + 2 kr/transaksjon
- **Qvalia** – API eller filbasert levering, oppstart innen 24 timer

### 3.4 Tilordning til riktig referanse/avdeling

**Utfordring:** EHF-fakturaer må bokføres mot riktig avdeling/oppdrag for å kunne løftes til Vitec Next.

**Relevante felt i EHF:**
- **BuyerReference** – kjøperens/bestillerens referanse (f.eks. oppdragsnummer)
- **OrderReference** – ordrenummer
- **Kundereferanse** – brukes av Kartverket for samlefaktura

**Kartverket-spesifikt:**
- Kartverket leverer EHF via meldingssentralen (sendregning.no)
- Samlefaktura kan grupperes per **kundereferanse**
- Bestillingsreferanse kan legges inn ved bestilling og vises på faktura
- Kontakt: regnskap@kartverket.no for samlefaktura-oppsett

**Produktregler (Eika-mønster, sjekk om POGO har tilsvarende):**
- Regler per leverandør
- Kobling produkt → regnskapskonto, prosjekt, avdeling
- Automatisk forslag basert på tidligere fakturaer

### 3.5 Sjekkliste – EHF-optimalisering

- [ ] Er Peppol-aksesspunkt aktivert og koblet til POGO?
- [ ] Er EHF-konteringsinnstillinger satt til "Grupper på produkt" (Kartverket-krav)?
- [ ] Er "utbetal fakturaer" fjernet på Kartverkets leverandørkort?
- [ ] Er funksjon for merking av oppdragsnummer hos Kartverket aktivert?
- [ ] Har dere regler for automatisk tilordning av faktura til avdeling/oppdrag basert på referanse?

---

## 4. Vitec Next – PowerOffice-integrasjon

### 4.1 Hva integrasjonen gjør

| Retning | Flyt |
|---------|-----|
| **Next → Go** | Posteringer (inntekt, utlegg) overføres til Go for bokføring |
| **Go → Next** | Innbetalinger og regnskapsposteringer synkroniseres til Next |
| **Go → Next** | Inngående fakturaer hentes fra Go til Next |
| **Ekstern → Go** | EHF-fakturaer fra Kartverket mottas i Go |
| **Go** | Utbetalinger og oppdragsoverføringer håndteres |
| **Bidireksjonelt** | Kunder og oppdrag (prosjekter) synkroniseres |

**Synkroniseringsfrekvens:** Daglig.

### 4.2 Forutsetninger i POGO

- Alle **avdelinger** opprettet med **samme koder** som i Next
- **Bankkontoer** registrert og aktivert med **klientansvar**
- **Reskontroserier** definert for kjøpere og selgere
- **Klientmidler**-funksjonalitet aktivert

### 4.3 Onboarding

Kontakt **Vitec** for onboarding av integrasjonen.  
Support: https://hjelp.vitecnext.no/

### 4.4 Sjekkliste – Next-integrasjon

- [ ] Er alle 19 avdelinger i Go med identiske koder som i Next?
- [ ] Er bankkontoer aktivert med klientansvar?
- [ ] Er reskontroserier for kjøpere og selgere definert?
- [ ] Synkroniseres data daglig uten feil?

---

## 5. Klientmidler og eiendomsmegling

### 5.1 Regulatorisk kontekst

- Klientmidler må holdes **adskilt** fra egne midler
- Klientkonto (egen eller felles) i finansinstitusjon
- Finanstilsynet krever sikkerhetsstillelse (min. 45 mill. kr)
- Klientkonto kan ikke brukes til motregning av meglerforetakets gjeld

### 5.2 POGO-støtte

- **Klientansvar** på bankkontoer
- **Avdelinger** for å skille mellom meglerkontorer
- **Prosjektregnskap** for oppdrag

---

## 6. Azets som partner

- Azets er **PowerOffice Premium Partner**
- Tilbyr: selvbetjening, outsourcing, lønnstjenester
- Hjelper med: behovsavklaring, datainnhenting, **bankintegrasjon med KID**, kontooppsett, kvalitetssikring
- Kontakt: kundesenter.no@azets.com, 40104018

---

## 7. Mulige forbedringer (prioritert)

### Høy prioritet
1. **EHF-automatisering:** Sjekk om Peppol-aksesspunkt er aktivert; hvis ikke, aktivere for automatisk mottak
2. **Referansetilordning:** Kartlegge om POGO har produktregler/konteringsregler for automatisk tilordning til avdeling/oppdrag basert på "vår referanse" eller kundereferanse
3. **Bankoptimalisering:** Verifisere at alle 19 avdelingers banker har direkteintegrasjon; vurdere bytte hvis ikke

### Medium prioritet
4. **Kartverket-oppsett:** Aktiver merking av oppdragsnummer; avklar samlefaktura per kundereferanse med Kartverket
5. **Regnskapsgodkjente betalinger:** Sikre at BankID og remittering er aktivert for alle relevante brukere

### Lav prioritet
6. **Integrera Connector:** Vurdere API-basert integrasjon for egendefinerte flyter
7. **Rapporter og dashboards:** Utnytte prosjektregnskap og sanntidsdata bedre

---

## 8. Åpne spørsmål til avklaring

Disse bør avklares med Azets og/eller Vitec:

1. **EHF-referanse:** Hvordan tilordnes EHF-fakturaer til avdeling/oppdrag i POGO i dag? Finnes produktregler eller konteringsregler?
2. **Peppol-aksesspunkt:** Hvilket aksesspunkt brukes (hvis noe)? Er det aktivert for alle avdelinger?
3. **Banker:** Hvilke banker bruker de 19 avdelingene? Har alle direkteintegrasjon?
4. **Kartverket:** Er "merking av oppdragsnummer" aktivert? Hvordan er samlefaktura satt opp?
5. **Synkronisering:** Er det kjente feil eller manuelle grep i daglig Next–Go-synkronisering?

---

## 9. Eksterne lenker (referanse)

| Ressurs | URL |
|---------|-----|
| PowerOffice bank-support | https://support.poweroffice.com/hc/no/sections/115001449226-Direkteintegrasjon-bank |
| PowerOffice bankavstemming FAQ | https://support.poweroffice.com/hc/no/articles/360037626911 |
| PowerOffice Next-integrasjon | https://www.poweroffice.no/utvidelser/next |
| PowerOffice bank-kategori | https://www.poweroffice.no/utvidelser/kategorier/bank |
| PowerOffice EHF-artikkel | https://www.poweroffice.no/artikler/send-og-motta-ehf-faktura |
| Vitec Next hjelp | https://hjelp.vitecnext.no/ |
| Kartverket EHF-faktura | https://www.kartverket.no/en/property/dokumentavgift-og-gebyr/ehf-faktura |
| Azets PowerOffice | https://www.azets.com/no-no/tjenester/digitale-tjenester/programvare/poweroffice-go |

---

## 10. Agent-instruksjoner

Når du jobber med PowerOffice-relaterte oppgaver:

1. **Sjekk dette dokumentet** først for kontekst og sjekklister
2. **Bank:** Bruk seksjon 2 for støttede banker og tekniske krav
3. **EHF:** Bruk seksjon 3 for mottak, aksesspunkt og referansetilordning
4. **Next:** Bruk seksjon 4 for integrasjonsforutsetninger
5. **Forbedringer:** Bruk seksjon 7 for prioriterte tiltak
6. **Spørsmål:** Bruk seksjon 8 som utgangspunkt for avklaringer med Azets/Vitec

**Ikke gjett** på POGO-spesifikke innstillinger – dokumenter usikkerheter og anbefal å verifisere med Azets eller PowerOffice-support.
