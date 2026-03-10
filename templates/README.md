# Vitec Next Master Template Library

Auto-generated from `vitec-next-export.json`.
Re-generate with: `python scripts/tools/build_template_library.py`

## Stats

- **Total templates:** 249
- **With HTML content:** 249
- **Without content:** 0

### By Origin

- kundemal: 116
- vitec-system: 133

### By Channel

- email: 20
- pdf_email: 204
- sms: 25

### By Category

- Akseptbrev kjøper: 10
- Akseptbrev selger: 6
- Annet: 121
- Budskjema: 2
- E-post ut: 4
- Erklæring: 7
- Formuesverdi: 1
- Forretningsførerinfo: 4
- Fullmakt kjøper: 3
- Fullmakt selger: 4
- Følgebrev: 7
- Hjemmelserklæring: 1
- Hvitvaskingsdokument: 3
- Konsesjonsskjema: 3
- Kontrakt: 8
- Oppdragsavtale: 6
- Oppgjørsdokument kjøper: 10
- Oppgjørsdokument selger: 15
- Oppgjørsoppstilling kjøper: 2
- Oppgjørsoppstilling selger: 2
- Oppgjørsskjema: 5
- Overtakelsesprotokoll: 2
- Pantedokument, sikring: 1
- Pantefrafall: 1
- Pantesperre: 1
- Rekvisisjon: 9
- Restgjeldsoppgave: 1
- Samtykke fra bortfester: 2
- Samtykke fra rettighetshaver til urådighet: 1
- Seksjoneringsbegjæring: 1
- Skjøte/hjemmelsoverf.: 2
- Takst: 1
- Tilbud: 2
- Transporterklæring: 1

## Structure

```
templates/
  master/              # All templates by origin
    vitec-system/      # Vitec standard templates
    kundemal/          # Custom (Proaktiv) templates
  by-category/         # Same templates grouped by Vitec category
    kontrakt/
    oppdragsavtale/
    ...
  index.json           # Machine-readable index
  README.md            # This file
```

## Template Index

| Title | Origin | Channel | Category | Status |
|-------|--------|---------|----------|--------|
| Akseptbrev kjøper | vitec-system | pdf_email | Akseptbrev kjøper | archived (x) |
| Akseptbrev kjøper Fysisk kontraktsmøte uten kontrakt | kundemal | pdf_email | Akseptbrev kjøper | published (x) |
| Akseptbrev kjøper digitalt kontraktsmøte (Proaktiv 01/02.26) | kundemal | pdf_email | Akseptbrev kjøper | published (x) |
| Akseptbrev kjøper digitalt kontraktsmøte uten kontrakt (Proa | kundemal | pdf_email | Akseptbrev kjøper | published (x) |
| Akseptbrev kjøper fysisk kontraktsmøte (Proaktiv 01/02.26) | kundemal | pdf_email | Akseptbrev kjøper | published (x) |
| Akseptbrev kjøper prosjekt | vitec-system | pdf_email | Akseptbrev kjøper | archived (x) |
| Akseptbrev kjøper prosjekt - Proaktiv (må redigeres) | kundemal | pdf_email | Akseptbrev kjøper | published (x) |
| Akseptbrev kjøper uten oppgjørsskjema (e-post) | vitec-system | email | Akseptbrev kjøper | archived (x) |
| Oppdragsavtale Næring (under arbeid) | kundemal | pdf_email | Akseptbrev kjøper | published (x) |
| Testmal e-post | kundemal | email | Akseptbrev kjøper | archived (x) |
| Akseptbrev selger | vitec-system | pdf_email | Akseptbrev selger | archived (x) |
| Akseptbrev selger Fysisk kontraktsmøte | kundemal | pdf_email | Akseptbrev selger | published (x) |
| Akseptbrev selger Fysisk kontraktsmøte uten kjøpekontrakt | kundemal | pdf_email | Akseptbrev selger | published (x) |
| Akseptbrev selger digital kontraktssignering | kundemal | pdf_email | Akseptbrev selger | published (x) |
| Akseptbrev selger digital kontraktssignering uten kjøpekontr | kundemal | pdf_email | Akseptbrev selger | published (x) |
| Akseptbrev selger uten oppgjørsskjema (e-post) | vitec-system | email | Akseptbrev selger | archived (x) |
| Aksept av oppdrag (Bolig/Standard)(Proaktiv 01/02.26) | kundemal | pdf_email | Annet | published (x) |
| Aksept av oppdrag - Tomt (Proaktiv 01/02.26) | kundemal | pdf_email | Annet | published (x) |
| Aksjeeierbok (Næring) | vitec-system | pdf_email | Annet | published (x) |
| Alle flettefelt 25.9 | vitec-system | pdf_email | Annet | published (x) |
| Alle flettekoder 25.9 | vitec-system | pdf_email | Annet | published (x) |
| Anbefaling til saksøker om å begjære bud stadfestet | vitec-system | pdf_email | Annet | published (x) |
| Anmodning om beboerliste Folkeregisteret (Tvangssalg) | vitec-system | pdf_email | Annet | published (x) |
| Anmodning om stadfestelse til tingretten (Tvangssalg) | vitec-system | pdf_email | Annet | published (x) |
| Anmodning om tilgang til salgsobjekt (Tvangssalg) | vitec-system | pdf_email | Annet | published (x) |
| Anmodning pantefrafall | vitec-system | pdf_email | Annet | published (x) |
| Avsender | vitec-system | pdf_email | Annet | archived (x) |
| Avsender | kundemal | pdf_email | Annet | published (x) |
| BROKER SMS -  Melding til selger før budstart | kundemal | sms | Annet | published (x) |
| BROKER SMS - Melding når lead ikke svarte | kundemal | sms | Annet | published (x) |
| BROKER SMS - Melding til digitalt lead | kundemal | sms | Annet | published (x) |
| BROKER SMS - Melding til lead når avtalt visning utgår | kundemal | sms | Annet | published (x) |
| BROKER SMS - Melding til lead om avbokat kundemøte | kundemal | sms | Annet | published (x) |
| BROKER SMS - Melding til lead om bekreftet kundemøte | kundemal | sms | Annet | published (x) |
| BROKER SMS - Melding til lead om bekreftet påmelding til avt | kundemal | sms | Annet | published (x) |
| BROKER SMS - Melding til leads etter de deltok på visning | kundemal | sms | Annet | published (x) |
| BROKER SMS - Melding til leads før visning | kundemal | sms | Annet | published (x) |
| BROKER SMS - Melding til selger før visning | kundemal | sms | Annet | published (x) |
| BROKER SMS - Påminnelse til leads om avtalt visning | kundemal | sms | Annet | published (x) |
| Begjære fravikelse overfor Saksøker | kundemal | pdf_email | Annet | published (x) |
| Begjæring om bistand til takst (Tvangssalg) | vitec-system | pdf_email | Annet | published (x) |
| Begjæring om stadfestelse og utkast til fordeling | kundemal | pdf_email | Annet | published (x) |
| Begjæring om utstedelse av skjøte/hjemmelsdokument (Tvangssa | vitec-system | pdf_email | Annet | published (x) |
| Bekreftelse på mottatt tvangssalgsoppdrag | vitec-system | pdf_email | Annet | published (x) |
| Boligkjøperforsikring | kundemal | pdf_email | Annet | published (x) |
| E-post signatur | vitec-system | pdf_email | Annet | published (x) |
| E-signeringsforespørsel SMS | vitec-system | sms | Annet | published (x) |
| E-signeringsforespørsel SMS (Proaktiv) | kundemal | sms | Annet | archived (x) |
| E-signeringsforespørsel e-post | vitec-system | email | Annet | published (x) |
| E-signeringspåminnelse SMS | vitec-system | sms | Annet | published (x) |
| E-signeringspåminnelse SMS (Proaktiv) | kundemal | sms | Annet | archived (x) |
| E-signeringspåminnelse e-post | vitec-system | email | Annet | published (x) |
| Eierskiftemelding grunneier | vitec-system | pdf_email | Annet | archived (x) |
| Foreleggelse av bud og melding om begjæring av stadfestelse  | vitec-system | pdf_email | Annet | published (x) |
| Forkjøpsrett benyttet, brev opprinnelig kjøper | vitec-system | pdf_email | Annet | published (x) |
| Fornyelse av oppdrag | kundemal | pdf_email | Annet | published (x) |
| Forslag til fordelingskjennelse (Tvangssalg) | vitec-system | pdf_email | Annet | published (x) |
| Fravikelsesbegjæring fra kjøper etter overtakelse (Tvangssal | vitec-system | pdf_email | Annet | published (x) |
| Følgebrev - Tinglyst pantedokument til kjøpers bank (Proakti | kundemal | pdf_email | Annet | published (x) |
| Følgebrev selger prospekt (e-post) | vitec-system | email | Annet | published (x) |
| Gevinstbeskatning fritidseiendom | kundemal | email | Annet | published (x) |
| Gevinstbeskatning kontraktsposisjon | kundemal | email | Annet | published (x) |
| Gjeldsbrev med urådighetssperre (Proaktiv 01/02.26) | kundemal | pdf_email | Annet | published (x) |
| Grunnlag brevmal generell | vitec-system | pdf_email | Annet | published (x) |
| Grunnlag brevmal kjøper | vitec-system | pdf_email | Annet | published (x) |
| Grunnlag brevmal selger | vitec-system | pdf_email | Annet | published (x) |
| Grunnlag brevmal selger og kjøper | vitec-system | pdf_email | Annet | published (x) |
| Grunnlag brevmal tabell | vitec-system | pdf_email | Annet | published (x) |
| Informasjon etter signering av kontrakt - prosjekt (kjøper)  | kundemal | pdf_email | Annet | published (x) |
| Informasjon frem mot overtakelsen (etter kontraktsmøte, kjøp | kundemal | pdf_email | Annet | published (x) |
| Informasjon frem mot overtakelsen (etter kontraktsmøte, selg | kundemal | pdf_email | Annet | published (x) |
| Informasjon om Off-Market salg (selger) (Proaktiv 01/02.26) | kundemal | pdf_email | Annet | published (x) |
| Informasjonsbrev til selger etter oppdragsinngåelse // Proak | kundemal | email | Annet | archived (x) |
| Innhenting av opplysninger - Bortfester (Proaktiv 01/02.26) | kundemal | pdf_email | Annet | published (x) |
| Innhenting av opplysninger - sameie/brl. | kundemal | pdf_email | Annet | published (x) |
| Innhenting av opplysninger borettslag // Proaktiv QA: ikke u | kundemal | pdf_email | Annet | archived (x) |
| Innhenting av opplysninger fra forening/veilag (Proaktiv 01/ | kundemal | pdf_email | Annet | published (x) |
| Innkreving av kjøpesum fra kjøper (Tvangssalg) | vitec-system | pdf_email | Annet | published (x) |
| Innkreving av kjøpesum fra kjøper (Tvangssalg) Proaktiv(kopi | kundemal | pdf_email | Annet | published (x) |
| Innkreving av kjøpesum fra kjøper ved anke | vitec-system | pdf_email | Annet | published (x) |
| Kjennelse stadfestelse | vitec-system | pdf_email | Annet | published (x) |
| Kjennelse ved fordeling av kjøpesum etter tvangssalg | vitec-system | pdf_email | Annet | published (x) |
| Kundeopplysningsskjema kjøper | vitec-system | pdf_email | Annet | published (x) |
| Kundeopplysningsskjema selger | vitec-system | pdf_email | Annet | published (x) |
| Mottaker | vitec-system | pdf_email | Annet | published (x) |
| Notering av gjeldsbrev med urådighetssperre (Proaktiv 01/02. | kundemal | pdf_email | Annet | published (x) |
| Oppgjørsbrev kjøper | vitec-system | pdf_email | Annet | published (x) |
| Oppgjørsbrev selger | vitec-system | pdf_email | Annet | published (x) |
| Oversendelse av kontraktsutkast (Digitalt) (Proaktiv 01/02.2 | kundemal | pdf_email | Annet | published (x) |
| Oversendelse av kontraktsutkast (Fysisk)(Proaktiv 01/02.26) | kundemal | pdf_email | Annet | published (x) |
| Parallellavklaring forkjøpsrett (Andel) (Proaktiv 01/02.26) | kundemal | pdf_email | Annet | published (x) |
| Proaktiv - Restgjeldsforespørsel ved oppgjør | kundemal | pdf_email | Annet | published (x) |
| Proaktiv e-post signatur (uten bilde) | kundemal | pdf_email | Annet | archived (x) |
| Restgjeldsforespørsel ved oppgjør | vitec-system | pdf_email | Annet | published (x) |
| Restgjeldsforespørsel ved oppgjør Tvangssalg | vitec-system | pdf_email | Annet | published (x) |
| SMS -  Melding etter visning med budportal link | kundemal | sms | Annet | published (x) |
| SMS - Fullt oppgjør innbetalt - Alle parter | kundemal | sms | Annet | published (x) |
| SMS - Melding til selger når boligen er publisert | kundemal | sms | Annet | published (x) |
| SMS - Melding til styreleder i sameiet vedr. restanser Proak | kundemal | sms | Annet | published (x) |
| SMS - Oppgjør utbetalt- selger | kundemal | sms | Annet | published (x) |
| SMS - Oppgjør utbetalt- selger (kopi) | kundemal | sms | Annet | published (x) |
| SMS - Påminnelse til selger om befaring | kundemal | sms | Annet | published (x) |
| SMS-signatur | kundemal | sms | Annet | published (x) |
| SMS-signatur | vitec-system | sms | Annet | archived (x) |
| Saldoforespørsel | vitec-system | pdf_email | Annet | archived (x) |
| Saldoforespørsel (Tvangssalg) | vitec-system | pdf_email | Annet | published (x) |
| Saldoforespørsel Proaktiv (system) | kundemal | pdf_email | Annet | published (x) |
| Salgsmelding til forretningsfører uten forkjøpsrett (Proakti | kundemal | pdf_email | Annet | published (x) |
| Salgsmelding til forretningsfører ved forkjøpsrett - (Tvangs | kundemal | pdf_email | Annet | published (x) |
| Salgsmelding til forretningsfører ved forkjøpsrett og styreg | kundemal | pdf_email | Annet | published (x) |
| Salgsmelding til forretningsfører ved forkjøpsrett uten styr | kundemal | pdf_email | Annet | published (x) |
| Samtykke til overdragelse - Bortfester (Proaktiv 01/02.26) | kundemal | pdf_email | Annet | published (x) |
| Skjema for risikovurdering av kunde og oppdrag (Næring) | vitec-system | pdf_email | Annet | published (x) |
| Tilbudsbrev | vitec-system | pdf_email | Annet | published (x) |
| Tilbudsbrev - Proaktiv | kundemal | pdf_email | Annet | published (x) |
| Tilbudsbrev Næring | kundemal | pdf_email | Annet | published (x) |
| Transport av aksjeleilighet (Proaktiv 01/02.26) | kundemal | pdf_email | Annet | published (x) |
| Utsendelse salgsoppgave (e-post) | vitec-system | email | Annet | archived (x) |
| Varsel om heving av tvangssalg | vitec-system | pdf_email | Annet | published (x) |
| Varsel om tvangssalg til panthaver/rettighetshaver | vitec-system | pdf_email | Annet | published (x) |
| Varsel om tvangssalg til panthaver/rettighetshaver Proaktiv( | kundemal | pdf_email | Annet | published (x) |
| Varsel om tvangssalg til saksøker | vitec-system | pdf_email | Annet | published (x) |
| Varsel om tvangssalg til saksøkte | vitec-system | pdf_email | Annet | published (x) |
| Varsel om tvangssalg til saksøkte Proaktiv | kundemal | pdf_email | Annet | published (x) |
| Varsel om tvangssalg til saksøktes husstand | vitec-system | pdf_email | Annet | published (x) |
| Varsel til kjøper ved forsinket betaling (Tvangssalg) | vitec-system | pdf_email | Annet | published (x) |
| Vitec Bunntekst | vitec-system | pdf_email | Annet | published (x) |
| Vitec Bunntekst Fremleiekontrakt | vitec-system | pdf_email | Annet | published (x) |
| Vitec Bunntekst Kontrakt | vitec-system | pdf_email | Annet | published (x) |
| Vitec Bunntekst Oppdragsavtale | vitec-system | pdf_email | Annet | archived (x) |
| Vitec Bunntekst Oppdragsavtale | kundemal | pdf_email | Annet | published (x) |
| Vitec Bunntekst Sidetall | vitec-system | pdf_email | Annet | published (x) |
| Vitec Bunntekst Sikring | vitec-system | pdf_email | Annet | published (x) |
| Vitec Bunntekst Skjøte | vitec-system | pdf_email | Annet | published (x) |
| Vitec Stilark | vitec-system | pdf_email | Annet | published (x) |
| Vitec Topptekst | vitec-system | pdf_email | Annet | published (x) |
| sms til selger vedr. energimerking | kundemal | sms | Annet | published (x) |
| Budskjema | vitec-system | pdf_email | Budskjema | published (x) |
| Kjøpetilbud prosjekt | vitec-system | pdf_email | Budskjema | published (x) |
| Bestilling av foto | kundemal | email | E-post ut | published (x) |
| Gevinstbeskatning | kundemal | email | E-post ut | published (x) |
| Godkjenning av salgsoppgave (E-post) (Proaktiv 01/02.26) | kundemal | email | E-post ut | published (x) |
| Informasjon fra styreleder | kundemal | email | E-post ut | published (x) |
| Erklæring fra panthavere/rettighetshavere (Tvangssalg) | vitec-system | pdf_email | Erklæring | published (x) |
| Erklæring fra panthavere/rettighetshavere (Tvangssalg) Proak | kundemal | pdf_email | Erklæring | published (x) |
| Erklæring fra saksøkte (Tvangssalg) | vitec-system | pdf_email | Erklæring | published (x) |
| Erklæring fra saksøkte (Tvangssalg) Proaktiv(kopi) | kundemal | pdf_email | Erklæring | published (x) |
| Erklæring juridisk person | vitec-system | pdf_email | Erklæring | published (x) |
| Erklæring om pantefrafall | vitec-system | pdf_email | Erklæring | published (x) |
| Selvdeklarering PEP | vitec-system | pdf_email | Erklæring | published (x) |
| Formuesverdi-fullmakt | vitec-system | pdf_email | Formuesverdi | archived (x) |
| Eierskiftemelding forretningsfører | vitec-system | pdf_email | Forretningsførerinfo | archived (x) |
| Eierskiftemelding forretningsfører (Ikke avklare forkjøpsret | kundemal | pdf_email | Forretningsførerinfo | published (x) |
| Eierskiftemelding forretningsfører (inkl. avkl. forkjøpsrett | kundemal | pdf_email | Forretningsførerinfo | published (x) |
| Eierskiftemelding forretningsfører - oppgjør | kundemal | pdf_email | Forretningsførerinfo | published (x) |
| Kjøpsfullmakt | vitec-system | pdf_email | Fullmakt kjøper | published (x) |
| Vedlegg skjøte prosjekt - erklæring boligseksjon | vitec-system | pdf_email | Fullmakt kjøper | published (x) |
| Vedlegg skjøte/hjemmelsoverføring prosjekt - fullmakt kjøper | vitec-system | pdf_email | Fullmakt kjøper | published (x) |
| Generalfullmakt (Proaktiv 01/02.26) | kundemal | pdf_email | Fullmakt selger | published (x) |
| Salgsfullmakt | vitec-system | pdf_email | Fullmakt selger | published (x) |
| Salgsfullmakt // Proaktiv: IKKE BRUK FØR QA KONTROLL | kundemal | pdf_email | Fullmakt selger | archived (x) |
| Transportfullmakt aksje | vitec-system | pdf_email | Fullmakt selger | published (x) |
| Følgebrev pantesperre/urådighet aksje | vitec-system | pdf_email | Følgebrev | published (x) |
| Følgebrev sikring | vitec-system | pdf_email | Følgebrev | published (x) |
| Følgebrev sletting av sikring | vitec-system | pdf_email | Følgebrev | archived (x) |
| Følgebrev sletting av sikring m/urådighet Proaktiv | kundemal | pdf_email | Følgebrev | published (x) |
| Følgebrev tinglysing | vitec-system | pdf_email | Følgebrev | published (x) |
| Følgebrev tinglyst pant | kundemal | pdf_email | Følgebrev | published (x) |
| Følgebrev tinglyst pantedokument | vitec-system | pdf_email | Følgebrev | archived (x) |
| Hjemmelserklæring | vitec-system | pdf_email | Hjemmelserklæring | published (x) |
| Risikoklassiffisering - Oppdragsinngåelse (Selger) // Proakt | kundemal | pdf_email | Hvitvaskingsdokument | published (x) |
| Risikoklassifisering - Fornyet vurdering (kjøper) // Proakti | kundemal | pdf_email | Hvitvaskingsdokument | published (x) |
| Risikoklassifisering Oppgjør // Proaktiv QA-1 | kundemal | pdf_email | Hvitvaskingsdokument | published (x) |
| Egenerklæring om konsesjonsfrihet (Grønt skjema) | vitec-system | pdf_email | Konsesjonsskjema | published (x) |
| Egenerklæring om konsesjonsfrihet i kommuner med nedsatt kon | vitec-system | pdf_email | Konsesjonsskjema | published (x) |
| Søknad om konsesjon (Blått skjema) | vitec-system | pdf_email | Konsesjonsskjema | published (x) |
| Kjøpekontrakt AS-IS | vitec-system | pdf_email | Kontrakt | archived (x) |
| Kjøpekontrakt Bruktbolig | kundemal | pdf_email | Kontrakt | published (x) |
| Kjøpekontrakt Bruktbolig (test kopi) | kundemal | pdf_email | Kontrakt | archived (x) |
| Kjøpekontrakt FORBRUKER | vitec-system | pdf_email | Kontrakt | archived (x) |
| Kjøpekontrakt FORBRUKER (kopi) | kundemal | pdf_email | Kontrakt | archived (x) |
| Kjøpekontrakt prosjekt (under testing) | kundemal | pdf_email | Kontrakt | published (x) |
| Kjøpekontrakt salg av AS med oppgjørsansvarlig | kundemal | pdf_email | Kontrakt | published (x) |
| Kjøpekontrakt salg av Næringseiendom med og uten oppgjørsans | kundemal | pdf_email | Kontrakt | published (x) |
| Oppdragsavtale | vitec-system | pdf_email | Oppdragsavtale | published (x) |
| Oppdragsavtale E-takst | kundemal | pdf_email | Oppdragsavtale | published (x) |
| Oppdragsavtale Næringsutleie Proaktiv | kundemal | pdf_email | Oppdragsavtale | published (x) |
| Oppdragsavtale Proaktiv | kundemal | pdf_email | Oppdragsavtale | published (x) |
| Oppdragsavtale Prosjektsalg Proaktiv | kundemal | pdf_email | Oppdragsavtale | published (x) |
| Oppdragsavtale kontraktsoppdrag | kundemal | pdf_email | Oppdragsavtale | published (x) |
| Forskuddsbetaling kjøper prosjekt | vitec-system | pdf_email | Oppgjørsdokument kjøper | published (x) |
| Følgebrev § 12-garanti kjøper | vitec-system | pdf_email | Oppgjørsdokument kjøper | published (x) |
| Inneståelseserklæring | vitec-system | pdf_email | Oppgjørsdokument kjøper | published (x) |
| Innfrielse restanse kommune | vitec-system | email | Oppgjørsdokument kjøper | archived (x) |
| Innfrielse restanse kommune Proaktiv(kopi) | kundemal | email | Oppgjørsdokument kjøper | published (x) |
| Klargjøringsbrev oppgjør kjøper | vitec-system | pdf_email | Oppgjørsdokument kjøper | published (x) |
| Oppgjørsbrev forretningsfører (sluttmelding) | vitec-system | pdf_email | Oppgjørsdokument kjøper | published (x) |
| Oppgjørsbrev kjøper prosjekt (med garanti) | vitec-system | pdf_email | Oppgjørsdokument kjøper | published (x) |
| Sluttregning kjøper prosjekt | vitec-system | pdf_email | Oppgjørsdokument kjøper | published (x) |
| Varsel om manglende § 12-garanti utbygger | vitec-system | pdf_email | Oppgjørsdokument kjøper | published (x) |
| Eierskiftemelding og restanseforespørsel kommune | vitec-system | pdf_email | Oppgjørsdokument selger | archived (x) |
| Eierskiftemelding og restanseforespørsel kommune Proaktiv | kundemal | pdf_email | Oppgjørsdokument selger | published (x) |
| Erklæring om sletting | vitec-system | pdf_email | Oppgjørsdokument selger | published (x) |
| Innfrielse lån/pant/utleggsforretning | vitec-system | email | Oppgjørsdokument selger | archived (x) |
| Innfrielse lån/pant/utleggsforretning Proaktiv(kopi) | kundemal | email | Oppgjørsdokument selger | published (x) |
| Innfrielse restanse grunneier | vitec-system | email | Oppgjørsdokument selger | published (x) |
| Innfrielsesbrev | kundemal | pdf_email | Oppgjørsdokument selger | published (x) |
| Klargjøringsbrev oppgjør selger | vitec-system | pdf_email | Oppgjørsdokument selger | published (x) |
| Oppgjørsbrev saksøkte (Tvangssalg) | vitec-system | pdf_email | Oppgjørsdokument selger | published (x) |
| Purring Innfrielse lån / pant / utleggsforretning | vitec-system | pdf_email | Oppgjørsdokument selger | published (x) |
| Restanseforespørsel forretningsfører | vitec-system | pdf_email | Oppgjørsdokument selger | archived (x) |
| Restanseforespørsel forretningsfører  Proaktiv(kopi) | kundemal | pdf_email | Oppgjørsdokument selger | published (x) |
| Restanseforespørsel grunneier | vitec-system | pdf_email | Oppgjørsdokument selger | archived (x) |
| Restanseforespørsel grunneier Proaktiv(kopi) | kundemal | pdf_email | Oppgjørsdokument selger | published (x) |
| Sletting av foreldet pant (30 år) | vitec-system | pdf_email | Oppgjørsdokument selger | published (x) |
| Oppgjørsoppstilling Kjøper | vitec-system | pdf_email | Oppgjørsoppstilling kjøper | archived (x) |
| Oppgjørsoppstilling Kjøper Proaktiv(kopi) | kundemal | pdf_email | Oppgjørsoppstilling kjøper | published (x) |
| Oppgjørsoppstilling Selger | vitec-system | pdf_email | Oppgjørsoppstilling selger | archived (x) |
| Oppgjørsoppstilling Selger Proaktiv(kopi) | kundemal | pdf_email | Oppgjørsoppstilling selger | published (x) |
| Oppgjørsskjema kjøper | vitec-system | pdf_email | Oppgjørsskjema | archived (x) |
| Oppgjørsskjema kjøper Næring | vitec-system | pdf_email | Oppgjørsskjema | archived (x) |
| Oppgjørsskjema selger | vitec-system | pdf_email | Oppgjørsskjema | archived (x) |
| Oppgjørsskjema selger Næring | vitec-system | pdf_email | Oppgjørsskjema | archived (x) |
| Pro-Contra skjema | vitec-system | pdf_email | Oppgjørsskjema | published (x) |
| Overtakelsesprotokoll | vitec-system | pdf_email | Overtakelsesprotokoll | published (x) |
| Overtakelsesprotokoll (utleie) | vitec-system | pdf_email | Overtakelsesprotokoll | published (x) |
| Pantedokument (sikring) | vitec-system | pdf_email | Pantedokument, sikring | published (x) |
| Pantefrafall | kundemal | pdf_email | Pantefrafall | published (x) |
| Pantesperre/urådighet aksje | vitec-system | pdf_email | Pantesperre | published (x) |
| Rekvisisjon info brannvesen | vitec-system | pdf_email | Rekvisisjon | published (x) |
| Rekvisisjon info e-verk | vitec-system | pdf_email | Rekvisisjon | published (x) |
| Rekvisisjon info ferdigattest | vitec-system | pdf_email | Rekvisisjon | published (x) |
| Rekvisisjon info forretningsfører | vitec-system | pdf_email | Rekvisisjon | published (x) |
| Rekvisisjon info grunneier | vitec-system | pdf_email | Rekvisisjon | published (x) |
| Rekvisisjon info kommune | vitec-system | pdf_email | Rekvisisjon | published (x) |
| Rekvisisjon info velforening | vitec-system | pdf_email | Rekvisisjon | published (x) |
| Rekvisisjon restgjeld | vitec-system | pdf_email | Rekvisisjon | published (x) |
| Restansesjekk velforening Proaktiv | kundemal | pdf_email | Rekvisisjon | published (x) |
| Saldoforespørsel Proaktiv | kundemal | pdf_email | Restgjeldsoppgave | published (x) |
| Salgsmelding til bortfester  (Proaktiv 01/02.26) | kundemal | pdf_email | Samtykke fra bortfester | published (x) |
| Salgsmelding til bortfester ved utfylling av erklæring (Proa | kundemal | pdf_email | Samtykke fra bortfester | published (x) |
| Samtykke til tinglysing | kundemal | pdf_email | Samtykke fra rettighetshaver til urådighet | published (x) |
| Seksjoneringsbegjæring | vitec-system | pdf_email | Seksjoneringsbegjæring | published (x) |
| Hjemmelsoverføring | vitec-system | pdf_email | Skjøte/hjemmelsoverf. | published (x) |
| Skjøte | vitec-system | pdf_email | Skjøte/hjemmelsoverf. | published (x) |
| Salg uten tilstandsrapport | kundemal | email | Takst | published (x) |
| Tilbudsbrev - Proaktiv (Test-epost-oppsett) (Under arbeid) | kundemal | pdf_email | Tilbud | published (x) |
| Tilbudsbrev - Proaktiv (Til Test) | kundemal | pdf_email | Tilbud | published (x) |
| Transporterklæring | vitec-system | pdf_email | Transporterklæring | published (x) |
