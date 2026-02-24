# Template Library Mining Report

**Generated:** 2026-02-24 01:51
**Templates analyzed:** 234 (of 249 total, 15 skipped below size threshold)
**Vitec system:** 129 | **Kundemal:** 105

## Executive Summary

| Metric | Count |
|--------|-------|
| Templates analyzed | 234 |
| Total merge fields (instances) | 4863 |
| Unique merge field paths | 848 |
| Total vitec-if conditions | 2599 |
| Unique conditions | 431 |
| Total vitec-foreach loops | 526 |
| Unique collection paths | 49 |
| Templates with proaktiv-theme | 0 |

---

## 1. CSS Patterns

### Style Block Counts
| Blocks | Templates |
|--------|-----------|
| 0 | 38 |
| 1 | 124 |
| 2 | 67 |
| 3 | 5 |

### Article Padding Values
| Value | Templates |
|-------|-----------|
| `20px` | 7 |
| `26px` | 1 |

### H2 Margin Values
| Value | Templates |
|-------|-----------|
| `30px 0 0 -20px` | 7 |
| `25px 0 0 -1em` | 7 |
| `30px 0 0 -26px` | 1 |
| `25px 0 10px 0` | 1 |

### Font Sizes
| Element | Value | Templates |
|---------|-------|-----------|
| h1 | `14pt` | 20 |
| h1 | `18pt` | 15 |
| h1 | `22pt` | 5 |
| h1 | `16px` | 3 |
| h1 | `12pt` | 2 |
| h1 | `1.5em` | 1 |
| h1 | `16pt` | 1 |
| h2 | `11pt` | 16 |
| h2 | `14pt` | 10 |
| h2 | `12pt` | 2 |
| h2 | `1.2em` | 1 |
| h3 | `10pt` | 15 |
| h3 | `16pt` | 1 |
| h3 | `13pt` | 1 |

### CSS Feature Presence
| Feature | Templates | % |
|---------|-----------|---|
| Checkbox CSS (label.btn / svg-toggle) | 80 | 34% |
| Insert field CSS (span.insert:empty) | 97 | 41% |
| Counter CSS (counter-reset) | 16 | 7% |
| .insert-table { display: inline-table } | 99 | 42% |
| .roles-table rule | 8 | 3% |
| a.bookmark rule | 8 | 3% |
| .liste rule | 27 | 12% |
| .borders class | 19 | 8% |
| avoid-page-break / page-break-inside | 33 | 14% |
| proaktiv-theme class | 0 | 0% |

### Counter ::before Properties
| Property | Templates |
|----------|-----------|
| has `display` on ::before | 1 |
| has `width` on ::before | 1 |

### Counter Names Used
| Name | Templates |
|------|-----------|
| `section` | 7 |
| `subsection` | 7 |
| `item` | 7 |
| `none` | 7 |
| `h3` | 6 |
| `h4` | 6 |
| `article` | 4 |
| `main-counter` | 3 |
| `sub-counter` | 3 |
| `subsubsection` | 2 |
| `sub-sub-counter` | 2 |
| `row-num` | 2 |

### SVG Data URI Encoding
| Encoding | Templates |
|----------|-----------|
| utf8 | 74 |
| percent | 1 |

### Top 20 Unscoped CSS Selectors
| Selector | Templates |
|----------|-----------|
| `.svg-toggle` | 80 |
| `label.btn` | 78 |
| `.svg-toggle.checkbox` | 75 |
| `.svg-toggle.checkbox.active, .btn.active > .svg-toggle.checkbox` | 70 |
| `span.insert:empty` | 64 |
| `span.insert:empty:before` | 64 |
| `.insert-table` | 63 |
| `span.insert:empty:hover` | 63 |
| `label.btn:active, label.btn.active` | 62 |
| `.svg-toggle.radio` | 58 |
| `.svg-toggle.radio.active, .btn.active > .svg-toggle.radio` | 58 |
| `.insert-table > span, .insert-table > span.insert` | 52 |
| `.checkbox-table-one-row` | 16 |
| `.svg-toggle.large` | 16 |
| `.info-label` | 12 |
| `.insert-table>span, .insert-table>span.insert` | 11 |
| `.vitec-data-missing > span:empty:before` | 11 |
| `.vitec-data-missing` | 11 |
| `.vitec-data-missing > span:empty` | 11 |
| `.vitec-data-missing > span` | 11 |

---

## 2. Merge Fields

### Top 50 Most Common Fields
| Field | Templates | Always Required |
|-------|-----------|-----------------|
| `[[eiendom.kommunenavn]]` | 151 |  |
| `[[eiendom.gatenavnognr]]` | 148 |  |
| `[[komplettmatrikkelutvidet]]` | 135 |  |
| `[[oppdrag.nr]]` | 70 |  |
| `[[selger.navn]]` | 69 | YES |
| `[[selger.poststed]]` | 55 | YES |
| `[[selger.postnr]]` | 55 | YES |
| `[[kontrakt.overtagelse.dato]]` | 53 |  |
| `[[meglerkontor.navn]]` | 52 |  |
| `[[selger.navnutenfullmektigogkontaktperson]]` | 50 | YES |
| `[[selger.fdato_orgnr]]` | 48 | YES |
| `[[selger.gatenavnognr]]` | 48 | YES |
| `[[selger.ledetekst_fdato_orgnr]]` | 48 | YES |
| `[[kontrakt.kjopesum]]` | 43 |  |
| `[[kjoper.navn]]` | 39 | YES |
| `[[eiendom.poststed]]` | 36 |  |
| `[[eiendom.postnr]]` | 36 |  |
| `[[kjoper.emailadresse]]` | 33 | YES |
| `[[tvangssalgrefnr]]` | 33 |  |
| `[[kjoper.tlf]]` | 33 | YES |
| `[[kjoper.postnr]]` | 31 | YES |
| `[[kjoper.poststed]]` | 31 | YES |
| `[[kjoper.gatenavnognr]]` | 30 | YES |
| `[[meglerkontor.poststed]]` | 29 |  |
| `[[selger.emailadresse]]` | 29 | YES |
| `[[kjoper.navnutenfullmektigogkontaktperson]]` | 28 | YES |
| `[[operativmegler.navn]]` | 28 |  |
| `[[eiendom.adresse]]` | 28 |  |
| `[[komplettmatrikkel]]` | 27 |  |
| `[[kjoper.fdato_orgnr]]` | 25 | YES |
| `[[mottaker.navn]]` | 24 |  |
| `[[kjoper.ledetekst_fdato_orgnr]]` | 24 | YES |
| `[[meglerkontor.orgnr]]` | 23 |  |
| `[[selger.tlf]]` | 23 | YES |
| `[[kontrakt.overtagelse.klokkeslett]]` | 22 |  |
| `[[selger.idnummer]]` | 22 | YES |
| `[[dagensdato]]` | 22 |  |
| `[[meglerkontor.epost]]` | 21 |  |
| `[[pant.belop]]` | 21 | YES |
| `[[kjoper.idnummer]]` | 21 | YES |
| `[[kontrakt.dato]]` | 20 |  |
| `[[oppgjor.kontornavn]]` | 20 |  |
| `[[pant.dokumentnr]]` | 18 | YES |
| `[[pant.tinglystdato]]` | 18 | YES |
| `[[eiendom.pris]]` | 17 |  |
| `[[oppgjor.postadresse]]` | 17 |  |
| `[[saksokte.navnutenfullmektigogkontaktperson]]` | 17 | YES |
| `[[oppgjor.poststed]]` | 17 |  |
| `[[oppgjor.postnr]]` | 17 |  |
| `[[aksjeselskap.navn]]` | 16 |  |

### $.UD() Wrapped Fields (monetary formatting)
| Field | Templates |
|-------|-----------|
| `$.UD([[kontrakt.kjopesum]])` | 40 |
| `$.UD([[pant.belop]])` | 19 |
| `$.UD([[eiendom.pris]])` | 16 |
| `$.UD([[eiendom.fellesgjeld]])` | 14 |
| `$.UD([[kontrakt.kjopesumogomkostn]])` | 12 |
| `$.UD([[utlegg.belop]])` | 11 |
| `$.UD([[vederlag.belop]])` | 10 |
| `$.UD([[oppdrag.provisjonberegnet]])` | 9 |
| `$.UD([[kostnad.belop]])` | 8 |
| `$.UD([[oppdrag.selgerutleggsum]])` | 8 |
| `$.UD([[oppdrag.selgervederlagmedprovsum]])` | 8 |
| `$.UD([[oppdrag.timeprisinklmva]])` | 7 |
| `$.UD([[utgift.belop]])` | 7 |
| `$.UD([[hoyestebud.belop]])` | 6 |
| `$.UD([[aksjeselskap.oblbelop]])` | 6 |
| `$.UD([[oppdrag.selgervederlagogfastprissum]])` | 6 |
| `$.UD([[oppdrag.timevederlagberegnet]])` | 6 |
| `$.UD([[oppdrag.selgersamletsum]])` | 5 |
| `$.UD([[oppdrag.selgersamletfastprissum]])` | 5 |
| `$.UD([[kontrakt.avgiftsgrunnlag]])` | 4 |
| `$.UD([[depotdokument.belop]])` | 4 |
| `$.UD([[postering.belop]])` | 4 |
| `$.UD([[oppdrag.selgerutgiftersum]])` | 4 |
| `$.UD([[oppdrag.fastpris]])` | 4 |
| `$.UD([[utgifter.belop]])` | 4 |
| `$.UD([[oppdrag.selgervederlagsum]])` | 4 |
| `$.UD([[oppdrag.selgerutleggogutgiftersum]])` | 3 |
| `$.UD([[oppdrag.timevederlagberegnetogselgerutleggogutgiftersum]])` | 3 |
| `$.UD([[eiendom.verditakst]])` | 2 |
| `$.UD([[pant.restbelop]])` | 2 |
| `$.UD([[laan.restsaldo]])` | 2 |
| `$.UD([[mottaker.kjoperspant.belop]])` | 2 |
| `$.UD([[aksjeselskap.paalydende]])` | 2 |
| `$.UD([[oppdrag.minimumsprovisjon.inklmva]])` | 2 |
| `$.UD([[eiendom.prom]])` | 1 |
| `$.UD([[akseptertbud.belop]])` | 1 |
| `$.UD([[eiendom.laanetakst]])` | 1 |
| `$.UD([[laan.renter]])` | 1 |
| `$.UD([[laan.omkostninger]])` | 1 |
| `$.UD([[laan.hovedstol]])` | 1 |
| `$.UD([[kontrakt.totaleomkostninger]])` | 1 |
| `$.UD([[eiendom.fellesutgifter]])` | 1 |
| `$.UD([[oppdrag.timepriseksmva]])` | 1 |

### Insert Field data-label Values
| Label | Templates |
|-------|-----------|
| `Sett inn tekst her...` | 79 |
| `Dato` | 35 |
| `Adresse` | 18 |
| `Navn` | 17 |
| `Beløp` | 15 |
| `dato` | 13 |
| `Ny adresse` | 11 |
| `Beskrivelse` | 8 |
| `Sted` | 8 |
| `beløp` | 8 |
| `Fødselsnummer` | 8 |
| `Telefon` | 8 |
| `Signatur` | 7 |
| `Sted/dato` | 7 |
| `Antall` | 7 |
| `Bank/finansinstitusjon` | 6 |
| `Kontoholders navn` | 6 |
| `Utbetalingsfordeling` | 6 |
| `Fra dato` | 6 |
| `Overføres til bankkontonummer` | 6 |
| `Festenr.` | 6 |
| `Gnr.` | 6 |
| `Bnr.` | 6 |
| `Fyll inn` | 6 |
| `Fødselsnr./Org.nr.` | 5 |
| `Grunneiers navn og fødselsdato` | 5 |
| `Selgers representant` | 5 |
| `Kr` | 5 |
| `Overføres samlet?` | 4 |
| `Kontaktperson/tlf/e-post` | 4 |

### Vitec Template Resources
| Resource | Templates |
|----------|-----------|
| `Vitec Stilark` | 194 |
| ` Avsender` | 108 |
| ` Mottaker` | 104 |
| ` SMS-signatur` | 11 |
| `Boligkjøperforsikring` | 2 |

### Fields Used Inside foreach Loops
| Field | Templates |
|-------|-----------|
| `[[selger.navnutenfullmektigogkontaktperson]]` | 64 |
| `[[selger.navn]]` | 61 |
| `[[selger.postnr]]` | 55 |
| `[[selger.poststed]]` | 55 |
| `[[selger.fdato_orgnr]]` | 52 |
| `[[selger.ledetekst_fdato_orgnr]]` | 51 |
| `[[selger.gatenavnognr]]` | 48 |
| `[[kjoper.navn]]` | 44 |
| `[[pant.navn]]` | 44 |
| `[[pant.type]]` | 36 |
| `[[kjoper.fdato_orgnr]]` | 35 |
| `[[kjoper.firmanavn]]` | 34 |
| `[[kjoper.tlf]]` | 33 |
| `[[kjoper.emailadresse]]` | 33 |
| `[[kjoper.postnr]]` | 31 |
| `[[kjoper.poststed]]` | 31 |
| `[[kjoper.navnutenfullmektigogkontaktperson]]` | 30 |
| `[[kjoper.gatenavnognr]]` | 30 |
| `[[selger.emailadresse]]` | 29 |
| `[[kjoper.idnummer]]` | 28 |
| `[[pant.belop]]` | 28 |
| `[[selger.firmanavn]]` | 28 |
| `[[kjoper.ledetekst_fdato_orgnr]]` | 27 |
| `[[pant.tinglystdato]]` | 26 |
| `[[selger.idnummer]]` | 25 |
| `[[pant.dokumentnr]]` | 23 |
| `[[selger.tlf]]` | 23 |
| `[[saksokte.navn]]` | 19 |
| `[[kjoper.hovedkontakt.navn]]` | 18 |
| `[[saksokte.navnutenfullmektigogkontaktperson]]` | 18 |

---

## 3. Conditional Logic

### Foreach Collection Paths
| Collection Path | Templates |
|-----------------|-----------|
| `Model.selgere` | 138 |
| `Model.kjopere` | 82 |
| `Model.matrikler` | 47 |
| `Model.saksokteliste` | 39 |
| `Model.oppdrag.kjoperspant` | 22 |
| `pant.laan` | 20 |
| `Model.saksokere` | 18 |
| `Model.arvinger` | 14 |
| `Model.hjemmelshavere` | 14 |
| `Model.selgerutgifter.alleposter` | 13 |
| `Model.selgerutlegg.alleposter` | 12 |
| `Model.grunneiere` | 12 |
| `Model.oppdrag.mottakerspantforinnfrielse` | 12 |
| `Model.selgervederlag.alleposter` | 11 |
| `Model.oppdrag.mottakerspant` | 10 |
| `Model.kjoperskostnader.alleposter` | 7 |
| `gruppe.poster` | 6 |
| `Model.oppdrag.saksokerspant` | 5 |
| `Model.mottaker.utbetalingsposter` | 4 |
| `Model.tidligereeiere` | 3 |
| `Model.oppdrag.pantforinnfrielse` | 3 |
| `Model.oppgjorkjoper.gruppering` | 3 |
| `Model.oppgjorselger.gruppering` | 3 |
| `Model.oppdrag.pantedokumenterkjoper` | 2 |
| `GetPosteringerUtenBoligkjoperforsikring()` | 2 |
| `Model.meglerkontor.aktiveansatte` | 1 |
| `Model.hoyestebud.budgivere` | 1 |
| `kjoper.fullmektiger_hvis_gruppe` | 1 |
| `Model.kjoperskostnader.poster` | 1 |
| `Model.kjopersfakturerte.poster` | 1 |
| `Model.kjopersfakturerte.alleposter` | 1 |
| `Model.solgteoppdragiomraade` | 1 |
| `Model.selgervederlag.poster` | 1 |
| `Model.selgerutlegg.poster` | 1 |
| `Model.selgerutgifter.poster` | 1 |
| `Model.selgersfakturerte.poster` | 1 |
| `Model.selgersfakturerte.alleposter` | 1 |
| `Model.oppdrag.prosjekt.prosjektenheter` | 1 |
| `Model.oppdrag.prosjekt.utbyggersforbehold.forbehold` | 1 |
| `Model.oppdrag.prosjektenhet.parkeringsplasser` | 1 |
| `Model.oppdrag.prosjekt.vederlagpaomsetninger` | 1 |
| `selger.fullmektiger_hvis_gruppe` | 1 |
| `Model.eiendom.kommendevisninger` | 1 |
| `visning.slots` | 1 |
| `Model.eiendom.avholdtevisninger` | 1 |
| `Model.eiendom.allevisninger` | 1 |
| `Model.eiendom.avlystevisninger` | 1 |
| `Model.oppdrag.pantforinnfrielse.Take(2)` | 1 |
| `Model.oppdrag.pantforinnfrielse.Take(1)` | 1 |

### Foreach Expressions (Full)
| Expression | Templates |
|------------|-----------|
| `selger in Model.selgere` | 138 |
| `kjoper in Model.kjopere` | 82 |
| `matrikkel in Model.matrikler` | 47 |
| `saksokte in Model.saksokteliste` | 39 |
| `pant in Model.oppdrag.kjoperspant` | 22 |
| `laan in pant.laan` | 20 |
| `saksoker in Model.saksokere` | 18 |
| `arving in Model.arvinger` | 14 |
| `hjemmelshaver in Model.hjemmelshavere` | 14 |
| `utlegg in Model.selgerutlegg.alleposter` | 12 |
| `grunneier in Model.grunneiere` | 12 |
| `pant in Model.oppdrag.mottakerspantforinnfrielse` | 12 |
| `vederlag in Model.selgervederlag.alleposter` | 11 |
| `pant in Model.oppdrag.mottakerspant` | 10 |
| `utgift in Model.selgerutgifter.alleposter` | 9 |
| `kostnad in Model.kjoperskostnader.alleposter` | 7 |
| `post in gruppe.poster` | 6 |
| `pant in Model.oppdrag.saksokerspant` | 5 |
| `postering in Model.mottaker.utbetalingsposter` | 4 |
| `utgifter in Model.selgerutgifter.alleposter` | 4 |
| `tidligereeier in Model.tidligereeiere` | 3 |
| `pant in Model.oppdrag.pantforinnfrielse` | 3 |
| `gruppe in Model.oppgjorkjoper.gruppering` | 3 |
| `gruppe in Model.oppgjorselger.gruppering` | 3 |
| `depotdokument in Model.oppdrag.pantedokumenterkjoper` | 2 |
| `kostnad in GetPosteringerUtenBoligkjoperforsikring()` | 2 |
| `ansatt in Model.meglerkontor.aktiveansatte` | 1 |
| `budgiver in Model.hoyestebud.budgivere` | 1 |
| `fullmektig in kjoper.fullmektiger_hvis_gruppe` | 1 |
| `kostnad in Model.kjoperskostnader.poster` | 1 |

### Logic Feature Usage
| Feature | Templates | % |
|---------|-----------|---|
| .Count guard before foreach | 111 | 47% |
| 'Mangler data' sentinel check | 53 | 23% |
| 'not' negation (vitec-if="not ...") | 0 | 0% |
| '!' negation (vitec-if="!...") | 5 | 2% |

### Model. vs Iterator Prefix in Conditions
| Prefix Type | Total Conditions |
|-------------|-----------------|
| Model. prefix (outside foreach) | 2034 |
| Iterator prefix (inside foreach) | 557 |

### Top 50 Most Common Conditions
| Condition | Templates |
|-----------|-----------|
| `Model.selgere.Count &gt; 0` | 48 |
| `Model.kjopere.Count &gt; 1` | 39 |
| `(Model.eiendom.eieform == &quot;Aksje&quot; \|\| Model.eiendom.eieform == &quot;Obligasjonsleilighet&quot;)` | 37 |
| `Model.selgere.Count &gt; 1` | 37 |
| `Model.eiendom.eieform == &quot;Andel&quot;` | 28 |
| `Model.kjopere.Count &gt; 0` | 28 |
| `Model.kjopere.Count == 1` | 24 |
| `kjoper.emailadresse != &quot;&quot;` | 21 |
| `selger.emailadresse != &quot;&quot;` | 21 |
| `Model.selgere.Count == 1` | 17 |
| `(Model.eiendom.eieform == &quot;Selveier&quot; \|\| Model.eiendom.eieform == &quot;Sameie&quot; \|\| Model.eiendom.eieform == &quot;Andel&quot;)` | 16 |
| `Model.eiendom.eieform != &quot;Andel&quot;` | 15 |
| `Model.saksokere.Count &gt; 1` | 14 |
| `Model.eiendom.eieform == &quot;Sameie&quot;` | 14 |
| `Model.oppdrag.hovedtype != &quot;Oppgj\xF8rsoppdrag&quot;` | 13 |
| `Model.oppdrag.hovedtype == &quot;Oppgj\xF8rsoppdrag&quot;` | 13 |
| `selger.tlf != &quot;Mangler data&quot;` | 13 |
| `kjoper.tlf != &quot;Mangler data&quot;` | 13 |
| `(selger.tlf != &quot;Mangler data&quot; &amp;&amp; selger.emailadresse != &quot;&quot;)` | 13 |
| `(kjoper.tlf != &quot;Mangler data&quot; &amp;&amp; kjoper.emailadresse != &quot;&quot;)` | 13 |
| `Model.eiendom.eieform== &quot;Andel&quot;` | 11 |
| `Model.eiendom.eieform != &quot;Selveier&quot;` | 11 |
| `Model.oppdrag.erdetforkjopsfrist == true` | 11 |
| `Model.eiendom.eieform== &quot;Sameie&quot;` | 9 |
| `(Model.eiendom.eieform == &quot;Selveier&quot; \|\| Model.eiendom.eieform == &quot;Sameie&quot;)` | 9 |
| `Model.oppdrag.hovedtype == &quot;Tvangssalg&quot;` | 9 |
| `(Model.eiendom.eieform != &quot;Aksje&quot; &amp;&amp; Model.eiendom.eieform != &quot;Obligasjonsleilighet&quot;)` | 9 |
| `Model.oppdrag.vederlagtypeprovisjon == true` | 8 |
| `Model.oppdrag.vederlagtypefastpris == true` | 8 |
| `Model.ansvarligmegler.navn != &quot;Mangler data&quot;` | 8 |
| `Model.oppdrag.hovedtype != &quot;Tvangssalg&quot;` | 8 |
| `Model.kontrakt.oppgjor.dato != &quot;Mangler data&quot;` | 8 |
| `kjoper.tlf != &quot;&quot;` | 8 |
| `selger.tlf != &quot;&quot;` | 8 |
| `(kjoper.tlf != &quot;&quot; &amp;&amp; kjoper.emailadresse != &quot;&quot;)` | 8 |
| `(selger.tlf != &quot;&quot; &amp;&amp; selger.emailadresse != &quot;&quot;)` | 8 |
| `Model.aksjeselskap.partoblnr != &quot;0&quot;` | 8 |
| `(Model.ansvarligmegler.navn != &quot;Mangler data&quot; &amp;&amp; Model.operativmegler.navn != Model.ansvarligmegler.navn)` | 8 |
| `(Model.ansvarligmegler.navn == &quot;Mangler data&quot; \|\| Model.operativmegler.navn == Model.ansvarligmegler.navn)` | 8 |
| `Model.eiendom.eieform == &quot;Selveier&quot;` | 7 |
| `Model.eiendom.eieform == &quot;Aksje&quot; \|\| Model.eiendom.eieform == &quot;Obligasjonsleilighet&quot;` | 7 |
| `(Model.eiendom.eieform == &quot;Sameie&quot; \|\| Model.eiendom.eieform == &quot;Selveier&quot;)` | 7 |
| `Model.eiendom.tomtetype == &quot;festetomt&quot;` | 7 |
| `Model.oppdrag.boligselgerforsikringbestilt == true` | 6 |
| `Model.oppdrag.erdetforkjopsfrist == false` | 6 |
| `Model.oppdrag.boligselgerforsikringbestilt == false` | 6 |
| `Model.eiendom.fellesgjeld != &quot;0,00&quot;` | 6 |
| `(Model.eiendom.eieform== &quot;Selveier&quot; \|\| Model.eiendom.eieform== &quot;Sameie&quot;)` | 6 |
| `Model.hjemmelshaver.navn != &quot;Mangler data&quot;` | 6 |
| `Model.oppdrag.kjoperspant.Count == 0` | 5 |

### Guard Patterns (.Count checks)
| Guard | Templates |
|-------|-----------|
| `Model.selgere.Count &gt; 0` | 48 |
| `Model.kjopere.Count &gt; 1` | 39 |
| `Model.selgere.Count &gt; 1` | 37 |
| `Model.kjopere.Count &gt; 0` | 28 |
| `Model.kjopere.Count == 1` | 24 |
| `Model.selgere.Count == 1` | 17 |
| `Model.saksokere.Count &gt; 1` | 14 |
| `Model.oppdrag.kjoperspant.Count == 0` | 5 |
| `Model.oppdrag.kjoperspant.Count &gt; 0` | 5 |
| `Model.grunneiere.Count &gt; 0` | 5 |
| `Model.selgerutgifter.poster.Count &gt; 0` | 4 |
| `Model.hjemmelshavere.Count &gt; 0` | 4 |
| `Model.oppdrag.mottakerspant.Count &gt; 0` | 4 |
| `Model.grunneiere.Count == 0` | 3 |
| `Model.saksokteliste.Count &gt; 0` | 3 |
| `Model.mottaker.utbetalingsposter.Count &gt; 1` | 3 |
| `Model.mottaker.utbetalingsposter.Count == 1` | 3 |
| `Model.tidligereeiere.Count &gt; 0` | 2 |
| `Model.kjopere.Count == 0` | 2 |
| `Model.saksokteliste.Count == 0` | 2 |

---

## Appendix: Per-Template Summary

| Template | Origin | Size | Fields | Conditions | Foreach | Style Blocks | Checkboxes | Inserts |
|----------|--------|------|--------|------------|---------|--------------|------------|---------|
| Aksept_av_oppdrag_(BoligStandard)(Proaktiv_0102.26 | kundemal | 5,183 | 1 | 0 | 0 | 0 | - | - |
| Aksept_av_oppdrag_-_Tomt_(Proaktiv_0102.26).html | kundemal | 4,376 | 1 | 0 | 0 | 0 | - | - |
| Akseptbrev_kjøper.html | vitec-system | 20,095 | 16 | 27 | 3 | 2 | Y | - |
| Akseptbrev_kjøper_Fysisk_kontraktsmøte_uten_kontra | kundemal | 8,969 | 8 | 10 | 0 | 2 | Y | - |
| Akseptbrev_kjøper_digitalt_kontraktsmøte_(Proaktiv | kundemal | 9,814 | 6 | 10 | 0 | 2 | Y | - |
| Akseptbrev_kjøper_digitalt_kontraktsmøte_uten_kont | kundemal | 9,544 | 6 | 8 | 0 | 2 | Y | - |
| Akseptbrev_kjøper_fysisk_kontraktsmøte_(Proaktiv_0 | kundemal | 8,930 | 8 | 10 | 0 | 2 | Y | - |
| Akseptbrev_kjøper_prosjekt.html | vitec-system | 22,606 | 29 | 15 | 3 | 2 | Y | - |
| Akseptbrev_kjøper_prosjekt_-_Proaktiv_(må_redigere | kundemal | 22,606 | 29 | 15 | 3 | 2 | Y | - |
| Akseptbrev_kjøper_uten_oppgjørsskjema_(e-post).htm | vitec-system | 10,306 | 8 | 21 | 0 | 2 | Y | - |
| Akseptbrev_selger.html | vitec-system | 15,559 | 16 | 26 | 3 | 2 | Y | - |
| Akseptbrev_selger_Fysisk_kontraktsmøte.html | kundemal | 7,470 | 8 | 10 | 0 | 2 | Y | - |
| Akseptbrev_selger_Fysisk_kontraktsmøte_uten_kjøpek | kundemal | 7,466 | 8 | 10 | 0 | 2 | Y | - |
| Akseptbrev_selger_digital_kontraktssignering.html | kundemal | 7,794 | 6 | 15 | 0 | 2 | Y | - |
| Akseptbrev_selger_digital_kontraktssignering_uten_ | kundemal | 6,879 | 6 | 6 | 0 | 2 | Y | - |
| Akseptbrev_selger_uten_oppgjørsskjema_(e-post).htm | vitec-system | 8,371 | 8 | 17 | 0 | 2 | Y | - |
| Aksjeeierbok_(Næring).html | vitec-system | 10,149 | 26 | 6 | 3 | 1 | - | Y |
| Alle_flettefelt_25.9.html | vitec-system | 215,315 | 0 | 0 | 0 | 0 | - | - |
| Alle_flettekoder_25.9.html | vitec-system | 357,631 | 1181 | 299 | 54 | 2 | Y | Y |
| Anbefaling_til_saksøker_om_å_begjære_bud_stadfeste | vitec-system | 3,858 | 9 | 0 | 1 | 1 | - | Y |
| Anmodning_om_beboerliste_Folkeregisteret_(Tvangssa | vitec-system | 2,980 | 6 | 0 | 1 | 1 | - | Y |
| Anmodning_om_stadfestelse_til_tingretten_(Tvangssa | vitec-system | 4,968 | 18 | 1 | 2 | 1 | - | Y |
| Anmodning_om_tilgang_til_salgsobjekt_(Tvangssalg). | vitec-system | 3,610 | 7 | 1 | 3 | 1 | - | Y |
| Anmodning_pantefrafall.html | vitec-system | 5,391 | 14 | 9 | 2 | 1 | - | Y |
| Avsender.html | vitec-system | 1,538 | 13 | 2 | 0 | 1 | - | - |
| Avsender_2.html | kundemal | 1,495 | 13 | 2 | 0 | 1 | - | - |
| BROKER_SMS_-_Melding_til_lead_om_bekreftet_kundemø | kundemal | 581 | 3 | 0 | 0 | 0 | - | - |
| BROKER_SMS_-_Melding_til_lead_om_bekreftet_påmeldi | kundemal | 719 | 8 | 0 | 0 | 0 | - | - |
| BROKER_SMS_-_Melding_til_leads_etter_de_deltok_på_ | kundemal | 533 | 3 | 0 | 0 | 0 | - | - |
| BROKER_SMS_-_Melding_til_leads_før_visning.html | kundemal | 486 | 5 | 0 | 0 | 0 | - | - |
| BROKER_SMS_-_Melding_til_selger_før_budstart.html | kundemal | 931 | 1 | 0 | 0 | 0 | - | - |
| BROKER_SMS_-_Melding_til_selger_før_visning.html | kundemal | 950 | 3 | 0 | 0 | 0 | - | - |
| Begjære_fravikelse_overfor_Saksøker.html | kundemal | 3,325 | 5 | 0 | 1 | 1 | - | Y |
| Begjæring_om_bistand_til_takst_(Tvangssalg).html | vitec-system | 4,063 | 8 | 3 | 3 | 1 | - | Y |
| Begjæring_om_stadfestelse_og_utkast_til_fordeling. | kundemal | 4,500 | 18 | 1 | 2 | 1 | - | Y |
| Begjæring_om_utstedelse_av_skjøtehjemmelsdokument_ | vitec-system | 6,359 | 8 | 13 | 4 | 1 | - | Y |
| Bekreftelse_på_mottatt_tvangssalgsoppdrag.html | vitec-system | 3,133 | 8 | 1 | 2 | 1 | - | Y |
| Bestilling_av_foto.html | kundemal | 702 | 4 | 0 | 0 | 0 | - | - |
| Boligkjøperforsikring.html | kundemal | 816 | 0 | 0 | 0 | 0 | - | - |
| Budskjema.html | vitec-system | 19,447 | 16 | 8 | 0 | 2 | Y | Y |
| E-post_signatur.html | vitec-system | 1,156 | 8 | 0 | 0 | 0 | - | - |
| E-signeringsforespørsel_e-post.html | vitec-system | 2,332 | 9 | 1 | 0 | 0 | - | - |
| E-signeringspåminnelse_e-post.html | vitec-system | 3,411 | 9 | 1 | 0 | 0 | - | - |
| Egenerklæring_om_konsesjonsfrihet_(Grønt_skjema).h | vitec-system | 86,577 | 16 | 2 | 8 | 2 | Y | - |
| Egenerklæring_om_konsesjonsfrihet_i_kommuner_med_n | vitec-system | 77,494 | 16 | 2 | 8 | 2 | Y | - |
| Eierskiftemelding_forretningsfører.html | vitec-system | 4,196 | 21 | 15 | 2 | 0 | - | - |
| Eierskiftemelding_forretningsfører_(Ikke_avklare_f | kundemal | 3,899 | 21 | 15 | 2 | 0 | - | - |
| Eierskiftemelding_forretningsfører_(inkl._avkl._fo | kundemal | 4,027 | 21 | 15 | 2 | 0 | - | - |
| Eierskiftemelding_forretningsfører_-_oppgjør.html | kundemal | 3,030 | 21 | 10 | 2 | 0 | - | - |
| Eierskiftemelding_grunneier.html | vitec-system | 9,787 | 20 | 50 | 2 | 1 | - | - |
| Eierskiftemelding_og_restanseforespørsel_kommune.h | vitec-system | 5,912 | 21 | 10 | 2 | 1 | - | Y |
| Eierskiftemelding_og_restanseforespørsel_kommune_P | kundemal | 4,653 | 21 | 10 | 2 | 1 | - | Y |
| Erklæring_fra_panthavererettighetshavere_(Tvangssa | vitec-system | 6,526 | 6 | 2 | 1 | 1 | - | - |
| Erklæring_fra_panthavererettighetshavere_(Tvangssa | kundemal | 6,526 | 6 | 2 | 1 | 1 | - | - |
| Erklæring_fra_saksøkte_(Tvangssalg).html | vitec-system | 6,768 | 9 | 0 | 1 | 2 | Y | Y |
| Erklæring_fra_saksøkte_(Tvangssalg)_Proaktiv(kopi) | kundemal | 6,768 | 9 | 0 | 1 | 2 | Y | Y |
| Erklæring_juridisk_person.html | vitec-system | 20,278 | 8 | 6 | 0 | 2 | Y | Y |
| Erklæring_om_pantefrafall.html | vitec-system | 7,080 | 11 | 4 | 1 | 1 | - | Y |
| Erklæring_om_sletting.html | vitec-system | 5,402 | 3 | 0 | 0 | 1 | - | Y |
| Foreleggelse_av_bud_og_melding_om_begjæring_av_sta | vitec-system | 5,816 | 27 | 4 | 3 | 1 | - | Y |
| Forkjøpsrett_benyttet_brev_opprinnelig_kjøper.html | vitec-system | 3,521 | 3 | 3 | 0 | 2 | - | Y |
| Formuesverdi-fullmakt.html | vitec-system | 3,403 | 17 | 1 | 2 | 1 | - | - |
| Fornyelse_av_oppdrag.html | kundemal | 2,245 | 5 | 1 | 1 | 1 | - | Y |
| Forskuddsbetaling_kjøper_prosjekt.html | vitec-system | 2,474 | 8 | 6 | 0 | 1 | - | Y |
| Forslag_til_fordelingskjennelse_(Tvangssalg).html | vitec-system | 43,449 | 80 | 26 | 15 | 1 | - | Y |
| Fravikelsesbegjæring_fra_kjøper_etter_overtakelse_ | vitec-system | 3,448 | 8 | 1 | 3 | 1 | - | Y |
| Følgebrev_-_Tinglyst_pantedokument_til_kjøpers_ban | kundemal | 4,404 | 12 | 0 | 1 | 1 | Y | - |
| Følgebrev__12-garanti_kjøper.html | vitec-system | 3,728 | 4 | 12 | 0 | 1 | - | Y |
| Følgebrev_pantesperreurådighet_aksje.html | vitec-system | 2,541 | 14 | 1 | 1 | 1 | - | Y |
| Følgebrev_selger_prospekt_(e-post).html | vitec-system | 2,598 | 4 | 0 | 0 | 1 | - | Y |
| Følgebrev_sikring.html | vitec-system | 3,695 | 21 | 6 | 2 | 1 | - | Y |
| Følgebrev_sletting_av_sikring.html | vitec-system | 2,282 | 3 | 0 | 0 | 1 | - | - |
| Følgebrev_sletting_av_sikring_murådighet_Proaktiv. | kundemal | 2,390 | 7 | 0 | 0 | 1 | - | - |
| Følgebrev_tinglysing.html | vitec-system | 4,806 | 15 | 4 | 4 | 1 | - | Y |
| Følgebrev_tinglyst_pant.html | kundemal | 3,279 | 6 | 2 | 0 | 1 | - | Y |
| Følgebrev_tinglyst_pantedokument.html | vitec-system | 3,400 | 5 | 2 | 0 | 1 | - | Y |
| Generalfullmakt_(Proaktiv_0102.26).html | kundemal | 9,398 | 7 | 2 | 1 | 1 | Y | - |
| Gevinstbeskatning.html | kundemal | 1,471 | 0 | 0 | 0 | 0 | - | - |
| Gevinstbeskatning_fritidseiendom.html | kundemal | 1,858 | 0 | 0 | 0 | 0 | - | - |
| Gevinstbeskatning_kontraktsposisjon.html | kundemal | 1,800 | 0 | 0 | 0 | 0 | - | - |
| Gjeldsbrev_med_urådighetssperre_(Proaktiv_0102.26) | kundemal | 4,959 | 13 | 0 | 2 | 1 | Y | - |
| Godkjenning_av_salgsoppgave_(E-post)_(Proaktiv_010 | kundemal | 2,920 | 3 | 0 | 0 | 1 | Y | - |
| Grunnlag_brevmal_generell.html | vitec-system | 1,474 | 3 | 0 | 0 | 1 | - | Y |
| Grunnlag_brevmal_kjøper.html | vitec-system | 2,923 | 14 | 6 | 2 | 1 | - | Y |
| Grunnlag_brevmal_selger.html | vitec-system | 2,907 | 14 | 6 | 2 | 1 | - | Y |
| Grunnlag_brevmal_selger_og_kjøper.html | vitec-system | 4,317 | 25 | 12 | 4 | 1 | - | Y |
| Grunnlag_brevmal_tabell.html | vitec-system | 3,264 | 3 | 0 | 0 | 1 | - | Y |
| Hjemmelserklæring.html | vitec-system | 33,250 | 25 | 26 | 14 | 2 | Y | - |
| Hjemmelsoverføring.html | vitec-system | 25,873 | 28 | 12 | 15 | 2 | Y | - |
| Informasjon_etter_signering_av_kontrakt_-_prosjekt | kundemal | 823 | 1 | 0 | 0 | 0 | - | - |
| Informasjon_fra_styreleder.html | kundemal | 740 | 6 | 0 | 0 | 0 | - | - |
| Informasjon_frem_mot_overtakelsen_(etter_kontrakts | kundemal | 1,717 | 2 | 0 | 0 | 0 | - | - |
| Informasjon_frem_mot_overtakelsen_(etter_kontrakts | kundemal | 2,515 | 8 | 0 | 0 | 0 | - | - |
| Informasjon_om_Off-Market_salg_(selger)_(Proaktiv_ | kundemal | 3,322 | 5 | 0 | 0 | 0 | - | - |
| Informasjonsbrev_til_selger_etter_oppdragsinngåels | kundemal | 9,228 | 4 | 0 | 0 | 1 | Y | - |
| Inneståelseserklæring.html | vitec-system | 4,347 | 8 | 0 | 0 | 1 | - | Y |
| Innfrielse_lånpantutleggsforretning.html | vitec-system | 8,163 | 19 | 16 | 6 | 2 | - | Y |
| Innfrielse_lånpantutleggsforretning_Proaktiv(kopi) | kundemal | 6,821 | 19 | 16 | 6 | 2 | - | Y |
| Innfrielse_restanse_grunneier.html | vitec-system | 4,040 | 10 | 0 | 1 | 2 | - | Y |
| Innfrielse_restanse_kommune.html | vitec-system | 4,010 | 9 | 0 | 1 | 2 | - | Y |
| Innfrielse_restanse_kommune_Proaktiv(kopi).html | kundemal | 3,612 | 9 | 0 | 1 | 2 | - | Y |
| Innfrielsesbrev.html | kundemal | 7,691 | 21 | 17 | 9 | 2 | - | Y |
| Innhenting_av_opplysninger_-_Bortfester_(Proaktiv_ | kundemal | 7,183 | 4 | 0 | 0 | 1 | Y | - |
| Innhenting_av_opplysninger_-_sameiebrl.html | kundemal | 13,020 | 6 | 4 | 0 | 1 | Y | - |
| Innhenting_av_opplysninger_borettslag_Proaktiv_QA_ | kundemal | 9,861 | 6 | 0 | 0 | 1 | Y | - |
| Innhenting_av_opplysninger_fra_foreningveilag_(Pro | kundemal | 4,497 | 3 | 0 | 0 | 1 | Y | - |
| Innkreving_av_kjøpesum_fra_kjøper_(Tvangssalg).htm | vitec-system | 6,641 | 15 | 16 | 1 | 1 | - | Y |
| Innkreving_av_kjøpesum_fra_kjøper_(Tvangssalg)_Pro | kundemal | 6,641 | 15 | 16 | 1 | 1 | - | Y |
| Innkreving_av_kjøpesum_fra_kjøper_ved_anke.html | vitec-system | 9,081 | 14 | 23 | 1 | 1 | - | Y |
| Kjennelse_stadfestelse.html | vitec-system | 11,059 | 22 | 1 | 2 | 3 | - | Y |
| Kjennelse_ved_fordeling_av_kjøpesum_etter_tvangssa | vitec-system | 21,027 | 24 | 6 | 7 | 3 | - | Y |
| Kjøpekontrakt_AS-IS.html | vitec-system | 88,921 | 65 | 153 | 9 | 2 | Y | Y |
| Kjøpekontrakt_Bruktbolig.html | kundemal | 100,989 | 77 | 173 | 9 | 2 | Y | Y |
| Kjøpekontrakt_Bruktbolig_(test_kopi).html | kundemal | 101,021 | 77 | 173 | 9 | 2 | Y | Y |
| Kjøpekontrakt_FORBRUKER.html | vitec-system | 95,658 | 65 | 151 | 9 | 2 | Y | Y |
| Kjøpekontrakt_FORBRUKER_(kopi).html | kundemal | 95,658 | 65 | 151 | 9 | 2 | Y | Y |
| Kjøpekontrakt_prosjekt_(under_testing).html | kundemal | 53,371 | 46 | 53 | 4 | 1 | Y | Y |
| Kjøpekontrakt_salg_av_AS_med_oppgjørsansvarlig.htm | kundemal | 154,606 | 171 | 58 | 12 | 2 | - | Y |
| Kjøpekontrakt_salg_av_Næringseiendom_med_og_uten_o | kundemal | 120,351 | 136 | 46 | 8 | 1 | - | Y |
| Kjøpetilbud_prosjekt.html | vitec-system | 15,491 | 17 | 3 | 0 | 2 | Y | Y |
| Kjøpsfullmakt.html | vitec-system | 6,207 | 11 | 4 | 2 | 1 | - | - |
| Klargjøringsbrev_oppgjør_kjøper.html | vitec-system | 4,598 | 3 | 10 | 0 | 1 | - | - |
| Klargjøringsbrev_oppgjør_selger.html | vitec-system | 4,225 | 3 | 7 | 0 | 1 | - | - |
| Kundeopplysningsskjema_kjøper.html | vitec-system | 28,407 | 9 | 2 | 1 | 2 | Y | Y |
| Kundeopplysningsskjema_selger.html | vitec-system | 28,384 | 9 | 2 | 1 | 2 | Y | Y |
| Mottaker.html | vitec-system | 891 | 7 | 1 | 0 | 1 | - | - |
| Notering_av_gjeldsbrev_med_urådighetssperre_(Proak | kundemal | 2,493 | 8 | 0 | 0 | 1 | - | - |
| Oppdragsavtale.html | vitec-system | 68,810 | 93 | 42 | 7 | 2 | Y | Y |
| Oppdragsavtale_E-takst.html | kundemal | 13,301 | 11 | 0 | 0 | 1 | - | - |
| Oppdragsavtale_Næring_(under_arbeid).html | kundemal | 38,398 | 33 | 4 | 1 | 3 | Y | Y |
| Oppdragsavtale_Næringsutleie_Proaktiv.html | kundemal | 34,365 | 25 | 2 | 1 | 3 | Y | Y |
| Oppdragsavtale_Proaktiv.html | kundemal | 81,032 | 88 | 49 | 7 | 2 | Y | Y |
| Oppdragsavtale_Prosjektsalg_Proaktiv.html | kundemal | 78,802 | 89 | 51 | 4 | 3 | Y | Y |
| Oppdragsavtale_kontraktsoppdrag.html | kundemal | 73,465 | 87 | 48 | 7 | 2 | Y | Y |
| Oppgjørsbrev_forretningsfører_(sluttmelding).html | vitec-system | 7,618 | 24 | 16 | 3 | 2 | - | Y |
| Oppgjørsbrev_kjøper.html | vitec-system | 2,093 | 3 | 8 | 0 | 1 | - | - |
| Oppgjørsbrev_kjøper_prosjekt_(med_garanti).html | vitec-system | 2,008 | 4 | 5 | 0 | 1 | - | - |
| Oppgjørsbrev_saksøkte_(Tvangssalg).html | vitec-system | 3,438 | 7 | 1 | 1 | 1 | - | Y |
| Oppgjørsbrev_selger.html | vitec-system | 2,875 | 8 | 12 | 1 | 1 | - | - |
| Oppgjørsoppstilling_Kjøper.html | vitec-system | 4,067 | 21 | 6 | 3 | 1 | - | - |
| Oppgjørsoppstilling_Kjøper_Proaktiv(kopi).html | kundemal | 3,859 | 21 | 6 | 3 | 1 | - | - |
| Oppgjørsoppstilling_Selger.html | vitec-system | 6,400 | 31 | 12 | 3 | 1 | - | - |
| Oppgjørsoppstilling_Selger_Proaktiv(kopi).html | kundemal | 6,245 | 31 | 12 | 3 | 1 | - | - |
| Oppgjørsskjema_kjøper.html | vitec-system | 16,626 | 8 | 6 | 3 | 2 | Y | - |
| Oppgjørsskjema_kjøper_Næring.html | vitec-system | 11,573 | 7 | 1 | 0 | 2 | Y | - |
| Oppgjørsskjema_selger.html | vitec-system | 12,219 | 8 | 9 | 3 | 2 | Y | - |
| Oppgjørsskjema_selger_Næring.html | vitec-system | 12,722 | 7 | 1 | 0 | 2 | Y | - |
| Oversendelse_av_kontraktsutkast_(Digitalt)_(Proakt | kundemal | 1,903 | 3 | 0 | 0 | 1 | Y | - |
| Oversendelse_av_kontraktsutkast_(Fysisk)(Proaktiv_ | kundemal | 2,058 | 4 | 0 | 0 | 1 | - | - |
| Overtakelsesprotokoll.html | vitec-system | 20,613 | 9 | 0 | 4 | 2 | Y | - |
| Overtakelsesprotokoll_(utleie).html | vitec-system | 17,431 | 3 | 1 | 0 | 2 | Y | Y |
| Pantedokument_(sikring).html | vitec-system | 32,487 | 33 | 21 | 15 | 2 | Y | - |
| Pantefrafall.html | kundemal | 4,248 | 13 | 5 | 2 | 1 | - | Y |
| Pantesperreurådighet_aksje.html | vitec-system | 12,834 | 17 | 1 | 2 | 2 | Y | Y |
| Parallellavklaring_forkjøpsrett_(Andel)_(Proaktiv_ | kundemal | 3,214 | 14 | 0 | 0 | 1 | - | - |
| Pro-Contra_skjema.html | vitec-system | 7,261 | 8 | 0 | 1 | 2 | Y | - |
| Proaktiv_-_Restgjeldsforespørsel_ved_oppgjør.html | kundemal | 4,109 | 15 | 7 | 2 | 1 | - | Y |
| Proaktiv_e-post_signatur_(uten_bilde).html | kundemal | 3,811 | 9 | 0 | 0 | 0 | - | - |
| Purring_Innfrielse_lån_pant_utleggsforretning.html | vitec-system | 4,386 | 14 | 10 | 5 | 1 | - | Y |
| Rekvisisjon_info_brannvesen.html | vitec-system | 10,755 | 11 | 1 | 1 | 2 | Y | - |
| Rekvisisjon_info_e-verk.html | vitec-system | 7,561 | 11 | 1 | 1 | 2 | Y | - |
| Rekvisisjon_info_ferdigattest.html | vitec-system | 7,378 | 11 | 1 | 1 | 2 | Y | - |
| Rekvisisjon_info_forretningsfører.html | vitec-system | 38,561 | 11 | 71 | 1 | 2 | Y | - |
| Rekvisisjon_info_grunneier.html | vitec-system | 8,784 | 11 | 1 | 1 | 2 | Y | - |
| Rekvisisjon_info_kommune.html | vitec-system | 8,586 | 11 | 1 | 1 | 2 | Y | - |
| Rekvisisjon_info_velforening.html | vitec-system | 9,680 | 11 | 1 | 1 | 2 | Y | - |
| Rekvisisjon_restgjeld.html | vitec-system | 9,976 | 14 | 5 | 2 | 2 | Y | Y |
| Restanseforespørsel_forretningsfører.html | vitec-system | 3,825 | 21 | 13 | 2 | 1 | - | - |
| Restanseforespørsel_forretningsfører_Proaktiv(kopi | kundemal | 3,825 | 21 | 13 | 2 | 1 | - | - |
| Restanseforespørsel_grunneier.html | vitec-system | 4,424 | 21 | 10 | 2 | 1 | - | Y |
| Restanseforespørsel_grunneier_Proaktiv(kopi).html | kundemal | 4,424 | 21 | 10 | 2 | 1 | - | Y |
| Restansesjekk_velforening_Proaktiv.html | kundemal | 6,419 | 11 | 1 | 1 | 2 | Y | - |
| Restgjeldsforespørsel_ved_oppgjør.html | vitec-system | 4,351 | 15 | 7 | 2 | 1 | - | Y |
| Restgjeldsforespørsel_ved_oppgjør_Tvangssalg.html | vitec-system | 4,219 | 11 | 3 | 1 | 1 | - | Y |
| Risikoklassiffisering_-_Oppdragsinngåelse_(Selger) | kundemal | 39,578 | 3 | 0 | 0 | 1 | Y | Y |
| Risikoklassifisering_-_Fornyet_vurdering_(kjøper)_ | kundemal | 24,481 | 4 | 0 | 0 | 1 | Y | - |
| Risikoklassifisering_Oppgjør_Proaktiv_QA-1.html | kundemal | 18,911 | 4 | 0 | 0 | 1 | Y | - |
| SMS_-_Fullt_oppgjør_innbetalt_-_Alle_parter.html | kundemal | 536 | 1 | 0 | 0 | 0 | - | - |
| SMS_-_Melding_etter_visning_med_budportal_link.htm | kundemal | 792 | 3 | 0 | 0 | 0 | - | - |
| SMS_-_Melding_til_selger_når_boligen_er_publisert. | kundemal | 729 | 4 | 0 | 0 | 0 | - | - |
| SMS_-_Melding_til_styreleder_i_sameiet_vedr._resta | kundemal | 521 | 5 | 0 | 0 | 0 | - | - |
| Saldoforespørsel.html | vitec-system | 7,837 | 27 | 7 | 3 | 1 | - | Y |
| Saldoforespørsel_(Tvangssalg).html | vitec-system | 4,718 | 6 | 4 | 2 | 1 | - | Y |
| Saldoforespørsel_Proaktiv.html | kundemal | 7,358 | 27 | 7 | 3 | 1 | - | Y |
| Saldoforespørsel_Proaktiv_(system).html | kundemal | 7,358 | 27 | 7 | 3 | 1 | - | Y |
| Salg_uten_tilstandsrapport.html | kundemal | 903 | 0 | 0 | 0 | 0 | - | - |
| Salgsfullmakt.html | vitec-system | 7,695 | 11 | 5 | 2 | 1 | - | Y |
| Salgsfullmakt_Proaktiv_IKKE_BRUK_FØR_QA_KONTROLL.h | kundemal | 8,837 | 7 | 2 | 1 | 1 | Y | - |
| Salgsmelding_til_bortfester_(Proaktiv_0102.26).htm | kundemal | 3,374 | 14 | 0 | 2 | 1 | Y | - |
| Salgsmelding_til_bortfester_ved_utfylling_av_erklæ | kundemal | 3,294 | 14 | 0 | 2 | 1 | - | - |
| Salgsmelding_til_forretningsfører_uten_forkjøpsret | kundemal | 3,956 | 17 | 0 | 2 | 1 | Y | - |
| Salgsmelding_til_forretningsfører_ved_forkjøpsrett | kundemal | 5,005 | 19 | 0 | 2 | 1 | Y | - |
| Salgsmelding_til_forretningsfører_ved_forkjøpsrett | kundemal | 4,476 | 23 | 0 | 2 | 1 | - | - |
| Salgsmelding_til_forretningsfører_ved_forkjøpsrett | kundemal | 4,033 | 17 | 0 | 2 | 1 | Y | - |
| Samtykke_til_overdragelse_-_Bortfester_(Proaktiv_0 | kundemal | 3,345 | 10 | 3 | 2 | 1 | - | - |
| Samtykke_til_tinglysing.html | kundemal | 3,044 | 13 | 0 | 0 | 1 | - | - |
| Seksjoneringsbegjæring.html | vitec-system | 81,327 | 22 | 1 | 12 | 2 | Y | - |
| Selvdeklarering_PEP.html | vitec-system | 15,266 | 3 | 0 | 1 | 2 | Y | - |
| Skjema_for_risikovurdering_av_kunde_og_oppdrag_(Næ | vitec-system | 29,674 | 12 | 2 | 2 | 2 | Y | - |
| Skjøte.html | vitec-system | 55,005 | 42 | 32 | 31 | 2 | Y | - |
| Sletting_av_foreldet_pant_(30_år).html | vitec-system | 2,444 | 4 | 0 | 0 | 1 | - | Y |
| Sluttregning_kjøper_prosjekt.html | vitec-system | 4,728 | 13 | 3 | 0 | 1 | - | Y |
| Søknad_om_konsesjon_(Blått_skjema).html | vitec-system | 66,249 | 12 | 4 | 1 | 2 | Y | - |
| Testmal_e-post.html | kundemal | 794 | 3 | 0 | 0 | 0 | - | - |
| Tilbudsbrev.html | vitec-system | 15,248 | 35 | 26 | 3 | 1 | - | - |
| Tilbudsbrev_-_Proaktiv.html | kundemal | 12,697 | 35 | 26 | 3 | 1 | - | - |
| Tilbudsbrev_-_Proaktiv_(Test-epost-oppsett)_(Under | kundemal | 57,820 | 29 | 1 | 4 | 1 | - | - |
| Tilbudsbrev_-_Proaktiv_(Til_Test).html | kundemal | 55,440 | 27 | 0 | 3 | 1 | - | Y |
| Tilbudsbrev_Næring.html | kundemal | 7,974 | 25 | 22 | 3 | 1 | - | - |
| Transport_av_aksjeleilighet_(Proaktiv_0102.26).htm | kundemal | 4,784 | 20 | 0 | 2 | 1 | Y | - |
| Transporterklæring.html | vitec-system | 5,456 | 17 | 3 | 2 | 1 | - | - |
| Transportfullmakt_aksje.html | vitec-system | 7,357 | 24 | 2 | 3 | 1 | - | - |
| Utsendelse_salgsoppgave_(e-post).html | vitec-system | 794 | 3 | 0 | 0 | 0 | - | - |
| Varsel_om_heving_av_tvangssalg.html | vitec-system | 6,419 | 15 | 2 | 4 | 2 | - | Y |
| Varsel_om_manglende__12-garanti_utbygger.html | vitec-system | 4,480 | 10 | 6 | 4 | 1 | - | Y |
| Varsel_om_tvangssalg_til_panthaverrettighetshaver. | vitec-system | 4,200 | 9 | 0 | 1 | 1 | - | Y |
| Varsel_om_tvangssalg_til_panthaverrettighetshaver_ | kundemal | 4,200 | 9 | 0 | 1 | 1 | - | Y |
| Varsel_om_tvangssalg_til_saksøker.html | vitec-system | 2,984 | 6 | 0 | 1 | 1 | - | Y |
| Varsel_om_tvangssalg_til_saksøkte.html | vitec-system | 6,737 | 13 | 5 | 2 | 1 | - | Y |
| Varsel_om_tvangssalg_til_saksøkte_Proaktiv.html | kundemal | 6,487 | 13 | 5 | 2 | 1 | - | Y |
| Varsel_om_tvangssalg_til_saksøktes_husstand.html | vitec-system | 2,869 | 6 | 1 | 1 | 1 | - | Y |
| Varsel_til_kjøper_ved_forsinket_betaling_(Tvangssa | vitec-system | 3,320 | 6 | 8 | 0 | 1 | - | Y |
| Vedlegg_skjøte_prosjekt_-_erklæring_boligseksjon.h | vitec-system | 4,759 | 7 | 2 | 2 | 1 | - | - |
| Vedlegg_skjøtehjemmelsoverføring_prosjekt_-_fullma | vitec-system | 6,152 | 20 | 6 | 2 | 1 | - | - |
| Vitec_Bunntekst.html | vitec-system | 984 | 10 | 0 | 0 | 0 | - | - |
| Vitec_Bunntekst_Fremleiekontrakt.html | vitec-system | 907 | 2 | 0 | 0 | 0 | - | - |
| Vitec_Bunntekst_Kontrakt.html | vitec-system | 1,020 | 2 | 4 | 0 | 0 | - | - |
| Vitec_Bunntekst_Oppdragsavtale.html | vitec-system | 1,549 | 9 | 0 | 0 | 1 | - | - |
| Vitec_Bunntekst_Oppdragsavtale_2.html | kundemal | 1,012 | 8 | 0 | 0 | 1 | - | - |
| Vitec_Bunntekst_Sidetall.html | vitec-system | 837 | 2 | 0 | 0 | 1 | - | - |
| Vitec_Bunntekst_Sikring.html | vitec-system | 1,897 | 2 | 2 | 0 | 1 | - | - |
| Vitec_Bunntekst_Skjøte.html | vitec-system | 1,707 | 2 | 0 | 0 | 1 | - | - |
| Vitec_Stilark.html | vitec-system | 1,885 | 0 | 0 | 0 | 1 | - | - |
| sms_til_selger_vedr._energimerking.html | kundemal | 509 | 0 | 0 | 0 | 0 | - | - |
