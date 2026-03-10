# PowerOffice Go (POGO) – Agent-referanse

> **Bruk:** Ved PowerOffice-relaterte oppgaver. Full research: `docs/poweroffice-research.md`

## Kontekst
- 19 megleravdelinger i POGO + Vitec Next
- Azets = revisor/regnskapsfører
- Nylig overgang til POGO + Next

## Bankintegrasjon
- **30+ norske banker** med direkteintegrasjon (DNB, Nordea, SpareBank 1, BN Bank, m.fl.)
- Krever: remitteringsavtale, BankID for betalingsgodkjenning
- Support: https://support.poweroffice.com/hc/no/sections/115001449226-Direkteintegrasjon-bank

## EHF-faktura
- Automatisk mottak og bokføring i POGO
- **Peppol-aksesspunkt** påkrevd for mottak (Logiq, Amili, Qvalia)
- Kartverket: samlefaktura per kundereferanse; merking av oppdragsnummer må aktiveres
- EHF-konteringsinnstilling: "Grupper på produkt"

## Vitec Next-integrasjon
- Avdelingskoder må være identiske i Go og Next
- Bankkontoer med klientansvar
- Reskontroserier for kjøpere/selgere
- Synkronisering daglig; onboarding via Vitec

## Sjekkliste (prioritet)
1. Peppol-aksesspunkt aktivert?
2. EHF-referanse til avdeling/oppdrag automatisk?
3. Alle banker har direkteintegrasjon?
4. Kartverket oppdragsnummer-merking aktivert?
