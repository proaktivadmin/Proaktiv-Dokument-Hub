# Vitec Next — Merge Field Registry

> Extracted from `Alle-flettekoder-25.9.md` (6,494 lines).
> This is a compact reference for template building. For the full
> reference with examples, vitec-foreach patterns, and formatting
> functions, see the original file.

---

## Aktiviteter

| Field Path | Display Name | Req |
|------------|-------------|-----|
| `[[besiktigelse.dato]]` | Befaringsdato |  |
| `[[besiktigelse.klokkeslett]]` | Befaringens klokkeslett |  |
| `[[tvangssalg.begjaringomstadfestelse.dato]]` | Begjæring om stadfestelse (Tvangssalg) |  |
| `[[tvangssalg.fordelingskjennelse.dato]]` | Fordelingskjennelsesdato (Tvangssalg) |  |
| `[[kontrakt.dato]]` | Kontraktmøtedato |  |
| `[[kontrakt.klokkeslett]]` | Kontraktmøtets klokkeslett |  |
| `[[oppdrag.tilsalgsdato]]` | Markedsføringsdato |  |
| `[[oppdrag.dato]]` | Oppdragets akseptdato |  |
| `[[oppdrag.utlopsdato]]` | Oppdragets utløpsdato |  |
| `[[kontrakt.overtagelse.dato]]` | Overtakelsesdato |  |
| `[[kontrakt.overtagelse.klokkeslett]]` | Overtakelsens klokkeslett |  |
| `[[kontrakt.oppgjor.dato]]` | Oppgjørsdato |  |
| `[[kontrakt.oppgjor.klokkeslett]]` | Oppgjørets klokkeslett |  |
| `[[tvangssalg.stadfestelseskjennelse.dato]]` | Stadfestelsesdato (Tvangssalg) |  |

## Avdelingsinformasjon (knyttet til objektet)

| Field Path | Display Name | Req |
|------------|-------------|-----|
| `[[meglerkontor.navn]]` | Navn |  |
| `[[meglerkontor.juridisknavn]]` | Juridisk navn |  |
| `[[meglerkontor.markedsforingsnavn]]` | Markedsføringsnavn |  |
| `[[meglerkontor.besoksadresse]]` | Besøksadresse |  |
| `[[meglerkontor.besokspostnr]]` | Besøksadressens postnr. |  |
| `[[meglerkontor.besokspoststed]]` | Besøksadressens poststed |  |
| `[[meglerkontor.adresse]]` | Postadresse |  |
| `[[meglerkontor.postnr]]` | Postnr. |  |
| `[[meglerkontor.poststed]]` | Poststed |  |
| `[[meglerkontor.epost]]` | E-post |  |
| `[[meglerkontor.fax]]` | Fax |  |
| `[[meglerkontor.hjemmeside]]` | Hjemmeside |  |
| `[[meglerkontor.internid]]` | Intern-ID |  |
| `[[meglerkontor.orgnr]]` | Org.nr. |  |
| `[[meglerkontor.tlf]]` | Telefon |  |
| `[[meglerkontor.dagligleder.navn]]` | Navn |  |
| `[[meglerkontor.dagligleder.kortommeg]]` | Kort om meg |  |
| `[[meglerkontor.dagligleder.tlf]]` | Telefon |  |
| `[[meglerkontor.dagligleder.arbeidtlf]]` | Telefon arbeid |  |
| `[[meglerkontor.dagligleder.mobiltlf]]` | Telefon mobil |  |
| `[[meglerkontor.dagligleder.epost]]` | E-post |  |
| `[[meglerkontor.dagligleder.brukerid]]` | Bruker-ID |  |
| `[[meglerkontor.fagansvarlig.navn]]` | Navn |  |
| `[[meglerkontor.fagansvarlig.kortommeg]]` | Kort om meg |  |
| `[[meglerkontor.fagansvarlig.tlf]]` | Telefon |  |
| `[[meglerkontor.fagansvarlig.arbeidtlf]]` | Telefon arbeid |  |
| `[[meglerkontor.fagansvarlig.mobiltlf]]` | Telefon mobil |  |
| `[[meglerkontor.fagansvarlig.epost]]` | E-post |  |
| `[[meglerkontor.fagansvarlig.brukerid]]` | Bruker-ID |  |
| `[[meglerkontor.ansattenavn]]` | Alle ansatte
			- forbedring i versjon 4.0: kun aktive |  |
| `[[meglerkontor.fullmektigenavn]]` | Alle fullmektige
			- forbedring i versjon 4.0: kun aktive |  |
| `[[oppgjor.kontornavn]]` | Navn |  |
| `[[oppgjor.besoksadresse]]` | Besøksadresse |  |
| `[[oppgjor.besokspostnr]]` | Besøksadresses postnr |  |
| `[[oppgjor.besokspoststed]]` | Besøksadresses poststed |  |
| `[[oppgjor.postadresse]]` | Postadresse |  |
| `[[oppgjor.postnr]]` | Postnr |  |
| `[[oppgjor.poststed]]` | Poststed |  |
| `[[oppgjor.kontorepost]]` | E-post |  |
| `[[oppgjor.kontorfax]]` | Fax |  |
| `[[oppgjor.hjemmeside]]` | Hjemmeside |  |
| `[[oppgjor.orgnr]]` | Org.nr. |  |
| `[[oppgjor.kontortlf]]` | Telefon |  |
| `[[rotavdeling.navn]]` | Navn |  |
| `[[rotavdeling.orgnr]]` | Org.nr. |  |

## Avsender (Benyttes i e-postsignaturer og avsendermaler)

| Field Path | Display Name | Req |
|------------|-------------|-----|
| `[[avsender.navn]]` | Navn |  |
| `[[avsender.epost]]` | E-post |  |
| `[[avsender.tlf]]` | Telefon |  |
| `[[avsender.arbeidtlf]]` | Telefon arbeid |  |
| `[[avsender.mobiltlf]]` | Telefon mobil |  |
| `[[avsender.tittel]]` | Tittel |  |
| `[[avsender.meglerkontor.navn]]` | Meglerkontorets navn |  |
| `[[avsender.meglerkontor.markedsforingsnavn]]` | Meglerkontorets markedsføringsnavn |  |
| `[[avsender.meglerkontor.besoksadresse]]` | Meglerkontorets besøksadresse |  |
| `[[avsender.meglerkontor.orgnr]]` | Meglerkontorets organisasjonsnummer |  |
| `[[avsender.meglerkontor.besokspostnr]]` | Besøksadressens postnr |  |
| `[[avsender.meglerkontor.besokspoststed]]` | Besøksadressens poststed |  |
| `[[avsender.meglerkontor.adresse]]` | Meglerkontorets postadresse |  |
| `[[avsender.meglerkontor.postnr]]` | Meglerkontorets postnr. |  |
| `[[avsender.meglerkontor.poststed]]` | Meglerkontorets poststed |  |
| `[[avsender.meglerkontor.epost]]` | Meglerkontorets epost |  |
| `[[avsender.meglerkontor.internid]]` | Meglerkontorets intern-ID |  |
| `[[avsender.meglerkontor.tlf]]` | Meglerkontorets telefon
			pri. 1) sentralbord 2) dagtid 3) mobil |  |

## Borettslag / Aksjelag / Sameie

| Field Path | Display Name | Req |
|------------|-------------|-----|
| `[[aksjeselskap.aksjenr]]` | Aksjenummer |  |
| `[[aksjeselskap.paalydende]]` | Aksjen(e)s pålydende verdi |  |
| `[[aksjeselskap.partoblnr]]` | Aksjen(e)s partialobligasjonsnr. |  |
| `[[aksjeselskap.oblbelop]]` | Aksjen(e)s partialobl. pål. verdi |  |
| `[[aksjeselskap.navn]]` | Aksjeselskapets navn1 |  |
| `[[aksjeselskap.orgnr]]` | Aksjeselskapets org.nr.1 |  |
| `[[eiendom.andelsnr]]` | Andelsnr. |  |
| `[[brl.navn]]` | Borettslagets navn1 |  |
| `[[brl.navnutenkontaktperson]]` | Borettslagets navn uten kontaktperson |  |
| `[[brl.orgnr]]` | Borettslagets org.nr.1 |  |
| `[[brl.andel]]` | Borettslagets eierandel1 |  |
| `[[eiendom.forkjopsrett]]` | Forkjøpsrett (fritekstfelt) |  |
| `[[oppdrag.forkjopsfrist]]` | Frist forkjøpsrett |  |
| `[[oppdrag.gebyrforkjopsrett]]` | Gebyr forkjøpsrett |  |
| `[[forretningsforer.adresse]]` | Forretningsførers adresse1 |  |
| `[[forretningsforer.navn]]` | Forretningsførers navn1 |  |
| `[[forretningsforer.eierskiftegebyr]]` | Forretningsførers eierskiftegebyr1 |  |
| `[[eiendom.innskudd]]` | Innskudd på brl-/aksjeboliger |  |
| `[[sameie.navn]]` | Sameiets navn1 |  |
| `[[sameie.orgnr]]` | Sameiets org.nr.1 |  |
| `[[sameie.sameiebrok]]` | Sameiebrøk1 |  |

## Brukere

| Field Path | Display Name | Req |
|------------|-------------|-----|
| `[[ansvarligmegler.navn]]` | Navn |  |
| `[[ansvarligmegler.brukerid]]` | Bruker-ID |  |
| `[[ansvarligmegler.epost]]` | E-post |  |
| `[[ansvarligmegler.kortommeg]]` | Kort om Ansvarlig megler |  |
| `[[ansvarligmegler.tlf]]` | Telefon |  |
| `[[ansvarligmegler.arbeidtlf]]` | Telefon arbeid |  |
| `[[ansvarligmegler.mobiltlf]]` | Telefon mobil |  |
| `[[ansvarligmegler.tittel]]` | Tittel |  |
| `[[oppgjor.ansvarlig.navn]]` | Navn |  |
| `[[oppgjor.ansvarlig.brukerid]]` | Bruker-ID |  |
| `[[oppgjor.ansvarlig.epost]]` | E-post |  |
| `[[oppgjor.ansvarlig.kortommeg]]` | Kort om Oppgjørsansvarlig |  |
| `[[oppgjor.ansvarlig.tlf]]` | Telefon |  |
| `[[oppgjor.ansvarlig.arbeidtlf]]` | Telefon arbeid |  |
| `[[oppgjor.ansvarlig.mobiltlf]]` | Telefon mobil |  |
| `[[megler1.navn]]` | Navn |  |
| `[[megler1.brukerid]]` | Bruker-ID |  |
| `[[megler1.epost]]` | E-post |  |
| `[[megler1.kortommeg]]` | Kort om Megler 1 |  |
| `[[megler1.tlf]]` | Telefon |  |
| `[[megler1.arbeidtlf]]` | Telefon arbeid |  |
| `[[megler1.mobiltlf]]` | Telefon mobil |  |
| `[[megler1.tittel]]` | Tittel |  |
| `[[megler1.kanvareansvarligmegler]]` | Kan være ansvarlig megler? |  |
| `[[megler2.navn]]` | Navn |  |
| `[[megler2.brukerid]]` | Bruker-ID |  |
| `[[megler2.epost]]` | E-post |  |
| `[[megler2.kortommeg]]` | Kort om Megler 2 |  |
| `[[megler2.tlf]]` | Telefon |  |
| `[[megler2.tittel]]` | Tittel |  |
| `[[medhjelper.navn]]` | Navn |  |
| `[[medhjelper.brukerid]]` | Bruker-ID |  |
| `[[medhjelper.epost]]` | E-post |  |
| `[[medhjelper.kortommeg]]` | Kort om Medhjelper |  |
| `[[medhjelper.tlf]]` | Telefon |  |
| `[[medhjelper.tittel]]` | Tittel |  |
| `[[salgsmegler.navn]]` | Navn |  |
| `[[salgsmegler.brukerid]]` | Bruker-ID |  |
| `[[salgsmegler.epost]]` | E-post |  |
| `[[salgsmegler.kortommeg]]` | Kort om salsgmegler |  |
| `[[salgsmegler.tlf]]` | Telefon |  |
| `[[salgsmegler.arbeidtlf]]` | Telefon arbeid |  |
| `[[salgsmegler.mobiltlf]]` | Telefon mobil |  |
| `[[salgsmegler.tittel]]` | Tittel |  |

## Bud og budgivere/interessenter

| Field Path | Display Name | Req |
|------------|-------------|-----|
| `[[oppdrag.antallbudgivere]]` | Antall budgivere |  |
| `[[oppdrag.antallinteressenter]]` | Antall interessenter |  |
| `[[akseptertbud.dato]]` | Akseptdato |  |
| `[[akseptertbud.akseptfrist.dato]]` | Akseptfrist dato |  |
| `[[akseptertbud.akseptfrist.klokkeslett]]` | Akseptfrist klokkeslett |  |
| `[[akseptertbud.belop]]` | Budbeløp |  |
| `[[akseptertbud.forbehold]]` | Forbehold |  |
| `[[akseptertbud.overtakelse]]` | Overtakelsesdato |  |
| `[[hoyestebud.budgiver.navn]]` | Navn (kommaseparert, evt.gruppenavn) |  |
| `[[hoyestebud.budgiver.idnummer]]` | Fødselsnummer/org.nr. |  |
| `[[hoyestebud.budgiver.ledetekst_idnummer]]` | Ledetekst ID-nummer/org.nr. |  |
| `[[hoyestebud.budgiver.fdato_orgnr]]` | Fødselsdato/org.nr. |  |
| `[[hoyestebud.budgiver.fdato_orgnr_utenpunktum]]` | Fødselsdato/org.nr. uten punktum |  |
| `[[hoyestebud.budgiver.ledetekst_fdato_orgnr]]` | Ledetekst fødselsdato/org.nr. |  |
| `[[hoyestebud.budgiver.gatenavnognr]]` | Adresse |  |
| `[[hoyestebud.budgiver.postnr]]` | Postnr. |  |
| `[[hoyestebud.budgiver.poststed]]` | Poststed |  |
| `[[hoyestebud.akseptfrist.dato]]` | Akseptfrist dato |  |
| `[[hoyestebud.akseptfrist.klokkeslett]]` | Akseptfrist klokkeslett |  |
| `[[hoyestebud.avgitt.dato]]` | Avgitt dato |  |
| `[[hoyestebud.avgitt.klokkeslett]]` | Avgitt klokkeslett |  |
| `[[hoyestebud.belop]]` | Budbeløp |  |
| `[[hoyestebud.forbehold]]` | Forbehold |  |
| `[[hoyestebud.overtakelse]]` | Overtakelsesdato |  |
| `[[hoyestebud.journalfort.dato]]` | Journalført dato |  |
| `[[hoyestebud.journalfort.klokkeslett]]` | Journalført klokkeslett |  |
| `[[hoyestebud.mottatt.dato]]` | Mottatt dato |  |
| `[[hoyestebud.mottatt.klokkeslett]]` | Mottatt klokkeslett |  |

## Diverse

| Field Path | Display Name | Req |
|------------|-------------|-----|
| `[[dagensdato]]` | Dagens dato |  |
| `[[oppdrag.diverse]]` | Diverse |  |
| `[[dokumentoutput]]` | Dokumentformat (pdf eller e-post) |  |
| `[[malkategori]]` | Malkategori |  |
| `[[malnavn]]` | Malnavn |  |
| `[[rettsgebyr.kostnad]]` | Rettsgebyr |  |

## Depotdokumenter

| Field Path | Display Name | Req |
|------------|-------------|-----|
| `[[depotdokument.rettighetshaver]]` | Rettighetshaver |  |
| `[[depotdokument.rettighetshaversorgnr]]` | Rettighetshavers orgnr. |  |
| `[[depotdokument.belop]]` | Beløp |  |
| `[[depotdokument.type]]` | Depotjournaltype |  |
| `[[depotdokument.status]]` | Status |  |

## E-signering

| Field Path | Display Name | Req |
|------------|-------------|-----|
| `[[esignering.dokumentkategori]]` | Dokumentkategori |  |
| `[[esignering.dokumentnavn]]` | Dokumentnavn |  |
| `[[esignering.lenke]]` | Lenke |  |
| `[[esignering.melding]]` | Melding |  |

## Eiendommen

| Field Path | Display Name | Req |
|------------|-------------|-----|
| `[[eiendom.utleie]]` | Adgang til utleie |  |
| `[[eiendom.adresse]]` | Adresse |  |
| `[[eiendom.fellesformue]]` | Andel fellesformue |  |
| `[[eiendom.fellesgjeld]]` | Andel fellesgjeld |  |
| `[[eiendom.andelfellesgjelddato]]` | Andel fellesgjeld pr. dato |  |
| `[[eiendom.andelfellesgjeldaar]]` | Andel fellesgjeld år |  |
| `[[eiendom.antallrom]]` | Antall rom |  |
| `[[eiendom.antallsoverom]]` | Antall soverom |  |
| `[[eiendom.beliggenhet]]` | Beliggenhet |  |
| `[[eiendom.belaaningsgrad]]` | Belåningsgrad |  |
| `[[eiendom.tomtebeskrivelse]]` | Beskrivelse av tomt |  |
| `[[eiendom.bruksareal]]` | BRA |  |
| `[[eiendom.bruksareal_i]]` | BRA-i |  |
| `[[eiendom.bruksareal_e]]` | BRA-e |  |
| `[[eiendom.bruksareal_b]]` | BRA-b |  |
| `[[eiendom.ferdigattest]]` | Brukstillatelse og ferdigattest |  |
| `[[eiendom.bruttoareal]]` | BTA |  |
| `[[eiendom.byggear]]` | Byggeår |  |
| `[[eiendom.eieform]]` | Eieform |  |
| `[[eiendom.etasje]]` | Etasje |  |
| `[[eiendom.gatenavnognr]]` | Gatenavn og gatenummer |  |
| `[[eiendom.grunntype]]` | Grunntype objekt
			(Bolig/Fritid/Næring/Prosjekt/Tomt) |  |
| `[[eiendom.fellesutgifter]]` | Felleskostnader pr. mnd |  |
| `[[forsikring.selskap]]` | Forsikringsselskap |  |
| `[[forsikring.polisenr]]` | Forsikring polisenr. |  |
| `[[eiendom.grunnboksdato]]` | Grunnboksdato |  |
| `[[eiendom.hvitevarer]]` | Hvitevarer |  |
| `[[eiendom.hvitvasking]]` | Hvitevaskingsreglene |  |
| `[[eiendom.innhold]]` | Innhold |  |
| `[[eiendom.kommunenavn]]` | Kommune |  |
| `[[eiendom.kommunenr]]` | Kommunenr. |  |
| `[[komplettmatrikkel]]` | Komplett matrikkel |  |
| `[[komplettmatrikkeljordsameie]]` | Jordsameie |  |
| `[[komplettmatrikkelrealsameie]]` | Realsameie |  |
| `[[komplettmatrikkelpersonligsameie]]` | Personlig sameie |  |
| `[[komplettmatrikkelutvidet]]` | Komplett matrikkel, utvidet
			- forbedring i versjon 3.0:
			  inkl. matrikkelens andel |  |
| `[[komplettmatrikkelutvidetutenideellandel]]` | Komplettmatrikkel, utvidet uten ideell andel |  |
| `[[eiendom.kortomeiendommen]]` | Kort om eiendommen |  |
| `[[eiendom.leilighetsnr]]` | Leilighetsnr. |  |
| `[[eiendom.legalpant]]` | Legalpant |  |
| `[[eiendom.laanetakst]]` | Lånetakst |  |
| `[[eiendom.omraade]]` | Område |  |
| `[[eiendom.boligtype]]` | Objektstype |  |
| `[[eiendom.overskrift]]` | Overskrift |  |
| `[[eiendom.parkering]]` | Parkering |  |
| `[[eiendom.postnr]]` | Postnr. |  |
| `[[eiendom.poststed]]` | Poststed |  |
| `[[eiendom.pris]]` | Prisantydning |  |
| `[[eiendom.prisibokstaver]]` | Prisantydning i bokstaver |  |
| `[[eiendom.prom]]` | P-Rom |  |
| `[[eiendom.radonmaaling]]` | Radonmåling |  |
| `[[eiendom.regulering]]` | Regulerings- og arealplaner |  |
| `[[eiendom.standard]]` | Standard |  |
| `[[eiendom.styregodkjennelse]]` | Styregodkjennelse |  |
| `[[eiendom.rapportdato]]` | Rapportdato |  |
| `[[eiendom.bygningssakkyndig]]` | Bygningssakkyndig |  |
| `[[eiendom.rapporttype]]` | Rapporttype |  |
| `[[eiendom.heftelserogrettigheter]]` | Tinglyste heftelser og rettigheter |  |
| `[[eiendom.tomteareal]]` | Tomtestørrelse |  |
| `[[eiendom.tomtetype]]` | Tomtetype |  |
| `[[eiendom.typebolig]]` | Type bolig
			(Se innstillinger på objektstypen) |  |
| `[[eiendom.typegrunn]]` | Type grunn
			(Se innstillinger på objektstypen) |  |
| `[[eiendom.vedtekter]]` | Vedtekter/husordensregler |  |
| `[[eiendom.veivannavlop]]` | Vei, vann og avløp |  |
| `[[eiendom.velavgiftbelop]]` | Velavgift beløp |  |
| `[[eiendom.velavgiftkommentar]]` | Velavgift kommentar |  |
| `[[eiendom.verditakst]]` | Verditakst |  |
| `[[eiendom.festeavgift]]` | Årlig festeavgift |  |

## Kjøpere

| Field Path | Display Name | Req |
|------------|-------------|-----|
| `[[kjoper.navn]]` | Navn (kommaseparert, evt.gruppenavn) |  |
| `[[kjoper.fornavn]]` | Fornavn (kun et navn flettes, evt. «v/<fullmektig>») |  |
| `[[kjoper.etternavn]]` | Etternavn (kun et navn flettes, evt. «v/<fullmektig>») |  |
| `[[kjoper.navnutenfullmektigogkontaktperson]]` | Navn uten fullmektig
			(NB! Endret i versjon 5.1) |  |
| `[[kjoper.idnummer]]` | Fødselsnummer/org.nr. |  |
| `[[kjoper.ledetekst_idnummer]]` | Ledetekst ID-nummer/org.nr. |  |
| `[[kjoper.fdato_orgnr]]` | Fødselsdato/org.nr. |  |
| `[[kjoper.fdato_orgnr_uten punktum]]` | Fødselsdato/org.nr. uten punktum |  |
| `[[kjoper.ledetekst_fdato_orgnr]]` | Ledetekst fødselsdato/org.nr. |  |
| `[[kjoper.hovedgatenavnognr]]` | Adresse |  |
| `[[kjoper.adresse]]` | Adresse inkl. postnr og sted |  |
| `[[kjoper.hovedpostnr]]` | Postnr. |  |
| `[[kjoper.hovedpoststed]]` | Poststed |  |
| `[[kjoper.hovedtlf]]` | Telefon |  |
| `[[kjoper.hovedepost]]` | E-post |  |
| `[[kjoper.hovedkontonummer]]` | Kontonummer |  |
| `[[kjoper.firmanavn]]` | Firmanavn uten kontaktperson |  |
| `[[kjoper.kontaktperson.navn]]` | Firmaets kontaktperson (rolle Kontaktperson)
			(NB! Endret i versjon 4.5) |  |
| `[[kjoper.dagligleder.navn]]` | Daglig leder |  |
| `[[kjoper.signaturberettiget.navn]]` | Signaturberettiget |  |
| `[[kjoper.styreleder.navn]]` | Styreleder |  |
| `[[kjoper.fullmektig.navn]]` | Navn |  |
| `[[kjoper.fullmektig.idnummer]]` | Fødselsnummer/org.nr. |  |
| `[[kjoper.fullmektig.ledetekst_idnummer]]` | Ledetekst ID-nummer/org.nr. |  |
| `[[kjoper.fullmektig.fdato_orgnr]]` | Fødselsdato/org.nr. |  |
| `[[kjoper.fullmektig.ledetekst_fdato_orgnr]]` | Ledetekst fødselsdato/org.nr. |  |
| `[[kjoper.fullmektig.gatenavnognr]]` | Adresse |  |
| `[[kjoper.fullmektig.postnr]]` | Postnr. |  |
| `[[kjoper.fullmektig.poststed]]` | Poststed |  |
| `[[kjoper.fullmektig.tlf]]` | Telefon |  |
| `[[kjoper.fullmektig.epost]]` | E-post |  |

## Kontraktsinformasjon

| Field Path | Display Name | Req |
|------------|-------------|-----|
| `[[kontrakt.andreforsikringer]]` | Andre forsikringer |  |
| `[[kontrakt.avgiftsgrunnlag]]` | Avgiftsgrunnlag |  |
| `[[eiendom.dokumentavgift]]` | Dokumentavgift |  |
| `[[kontrakt.klientkonto]]` | Klientkonto |  |
| `[[kontrakt.kid]]` | KID kjøper |  |
| `[[kontrakt.kidselger]]` | KID selger |  |
| `[[kontrakt.klientkontoogkid]]` | Klientkonto og KID kjøper |  |
| `[[kontrakt.klientkontoogkidselger]]` | Klientkonto og KID selger |  |
| `[[kontrakt.kjopesum]]` | Kjøpesum |  |
| `[[kontrakt.kjopesumibokstaver]]` | Kjøpesum i bokstaver |  |
| `[[kontrakt.dato]]` | Kontraktmøtedato |  |
| `[[kontrakt.klokkeslett]]` | Kontraktmøtets klokkeslett |  |
| `[[kontrakt.lovanvendelse]]` | Lovanvendelse |  |
| `[[kontrakt.formidling.nr]]` | Omsetningsnr. |  |
| `[[kontrakt.oppgjor.dato]]` | Oppgjørsdato |  |
| `[[kontrakt.oppgjor.klokkeslett]]` | Oppgjørets klokkeslett |  |
| `[[kontrakt.overtagelse.dato]]` | Overtakelsesdato |  |
| `[[kontrakt.overtagelse.klokkeslett]]` | Overtakelsens klokkeslett |  |
| `[[kontrakt.vedleggkjopekontrakt]]` | Vedlegg til kjøpekontrakt |  |
| `[[*kostnad.beskrivelse]]` | Kjøpers bokførte kostnader (liste): | * |
| `[[*faktura.beskrivelse]]` | Sum kjøpesum og omkostninger
			kr [[kontrakt.kjopesumogomkostn]]
		
		
			 
		
		
			
			Kjøpers fakturerte omkostninger
		
		
			Kjøpers fakturerte, sendte poster poster (liste): | * |

## Kontraktsposisjon

| Field Path | Display Name | Req |
|------------|-------------|-----|
| `[[kontraktsposisjon.opprinneligavtale.andelfellesgjeld]]` | Andel fellesgjeld oppr. avtale |  |
| `[[kontraktsposisjon.opprinneligavtale.kjopesum]]` | Kjøpesum opprinnelig avtale |  |
| `[[kontraktsposisjon.opprinneligavtale.omkostninger]]` | Omkostninger opprinnelig avtale |  |
| `[[kontraktsposisjon.transportavtale.omkostninger]]` | Omkostninger transportavtale |  |
| `[[kontraktsposisjon.opprinneligavtale.tilvalg]]` | Tilvalg opprinnelig avtale |  |
| `[[kontraktsposisjon.totaleomkostninger]]` | Totale omk. for kontr.posisjon (omkostninger opprinnelig avtale + omkostninger transportavtale) |  |
| `[[kontraktsposisjon.totalpris]]` | Totalpris for kontraktsposisjon (kontr.posisjonens prisantydning + kjøpesum opprinnelig avtale + tilvalg opprinnelig avtale) |  |
| `[[kontraktsposisjon.totalprisantydninginklomk]]` | Total prisantydning for kontraktsposisjon inkl. fellesgjeld og omkostninger (kontr.posisjonens prisantydning + kjøpesum oppr. avtale + tilvalg oppr. avtale + fellesgjeld + omk. oppr. avtale + omk. kontr.posisjon) |  |
| `[[kontraktsposisjon.totalprisantydningeksklomk]]` | Total prisantydning for kontraktsposisjon ekskl. omkostninger (kontr.posisjonens prisantydning + kjøpesum oppr. avtale + tilvalg oppr. avtale + fellesgjeld) |  |

## Matrikkel

| Field Path | Display Name | Req |
|------------|-------------|-----|
| `[[komplettmatrikkel]]` | Komplett matrikkel |  |
| `[[*matrikkel.gnr]]` | Matrikler (liste): | * |
| `[[eiendom.kommunaleavgifterbelop]]` | Kommunale avgifter beløp |  |
| `[[eiendom.kommunaleavgifteraar]]` | Kommunale avgifter år |  |
| `[[eiendom.kommunenavn]]` | Kommune |  |
| `[[eiendom.kommunenr]]` | Kommunenr. |  |

## Mottaker

| Field Path | Display Name | Req |
|------------|-------------|-----|
| `[[mottaker.navn]]` | Navn |  |
| `[[mottaker.idnummer]]` | Fødselsnummer/org.nr. |  |
| `[[mottaker.adresse]]` | Adresse |  |
| `[[mottaker.postnr]]` | Postnr. |  |
| `[[mottaker.poststed]]` | Poststed |  |
| `[[mottaker.epost]]` | E-post |  |
| `[[mottaker.tlf]]` | Telefon |  |
| `[[mottaker.arbeidtlf]]` | Telefon arbeid |  |
| `[[mottaker.mobiltlf]]` | Telefon mobil |  |
| `[[mottaker.visning.dato]]` | Visning |  |
| `[[mottaker.visning.tidsrom]]` | Visning |  |

## Oppdrag

| Field Path | Display Name | Req |
|------------|-------------|-----|
| `[[oppdrag.antallfinnannonser]]` | Antall finn-annonser |  |
| `[[oppdrag.lenkefinnannonse]]` | Lenke til nyeste finn-annonse |  |
| `[[oppdrag.finnpublisertdato]]` | Publiseringsdato finn-annonse |  |
| `[[oppdrag.egenpubliseringsannonselenke]]` | URL til oppdragets nyeste annonse |  |
| `[[oppdrag.egenpubliseringdato]]` | Annonse publisert dato |  |
| `[[oppdrag.egenpubliseringsannonserantall]]` | Antall egenpubliseringsannonser |  |
| `[[oppdrag.kartverksref]]` | Kartverksreferanse |  |
| `[[oppdrag.estateid]]` | Oppdragets estate-ID |  |
| `[[oppdrag.systemid]]` | Oppdragets system-ID |  |
| `[[oppdrag.url]]` | Oppdragets URL |  |
| `[[oppdrag.bortfestertransportgebyr]]` | Transportgebyr bortfester |  |
| `[[oppdrag.hovedtype]]` | Oppdragskategori/hovedtype oppdrag
			(koblet til oppdragstype) |  |
| `[[oppdrag.type]]` | Oppdragstype |  |

## Oppdragsavtale

| Field Path | Display Name | Req |
|------------|-------------|-----|
| `[[oppdrag.dato]]` | Oppdragets akseptdato |  |
| `[[oppdrag.utlopsdato]]` | Oppdragets utløpsdato |  |
| `[[oppdrag.nr]]` | Oppdragsnr. |  |
| `[[oppdrag.pristype]]` | Pristype |  |
| `[[oppdrag.provisjonsgrunnlag]]` | Provisjonsgrunnlag |  |
| `[[oppdrag.minimumsprovisjon.inklmva]]` | Minimumsprovisjon inkl. MVA |  |
| `[[oppdrag.minimumsprovisjon.eksklmva]]` | Minimumsprovisjon ekskl. MVA |  |
| `[[oppdrag.spesielleforholdoppdragsavtale]]` | Spesielle forhold i oppdragsavtalen |  |
| `[[oppdrag.provisjonstype]]` | Vederlagstype |  |
| `[[*vederlag.beskrivelse]]` | Beskrivelse
			Beløp u/mva
			Beløp m/mva
		
		
			 
			Faktisk timebasert vederlag (beregnet av timepris og ant. pål. timer)
			kr [[oppdrag.timevederlageksmva]]
			kr [[oppdrag.timevederlaginklmva]]
		
		
			 
			Sum faktisk timebasert vederlag og andre inntekter
			kr [[oppdrag.timevederlagogselgervederlageksmvasum]]
			kr [[oppdrag.timevederlagogselgervederlagsum]]
		
		
			 
			Sum faktisk timebasert vederlag, utlegg og andre utgifter
			kr [[oppdrag.timevederlagogselgerutleggogutgiftereksmvasum]]
			kr [[oppdrag.timevederlagogselgerutleggogutgiftersum]]
		
		
			 
			Sum faktisk timebasert vederlag, andre inntekter, utlegg og andre utgifter
			kr [[oppdrag.selgersamlettimevederlageksmvasum]]
			kr [[oppdrag.selgersamlettimevederlagsum]]
		
		
			
			Fastprisavtale (JANEI):
			
			Beskrivelse
			
			Beløp u/mva
			
			Beløp m/mva
		
		
			 
			Fastpris
			kr [[oppdrag.fastpriseksmva]]
			kr [[oppdrag.fastpris]]
		
		
			 
			Sum fastpris og andre inntekter
			kr [[oppdrag.selgervederlagogfastpriseksmvasum]]
			kr [[oppdrag.selgervederlagogfastprissum]]
		
		
			 
			Sum fastpris, utlegg og andre utgifter
			kr [[oppdrag.selgerutleggogutgifterogfastpriseksmvasum]]
			kr [[oppdrag.selgerutleggogutgifterogfastprissum]]
		
		
			 
			Sum fastpris, andre inntekter, utlegg og andre utgifter
			kr [[oppdrag.selgersamletfastpriseksmvasum]]
			kr [[oppdrag.selgersamletfastprissum]]
		
		
			 
		
		
			
			Selgers omkostninger
		
		
			Selgers bokførte vederlag/andre inntekter (liste): | * |
| `[[*utlegg.beskrivelse]]` | Selgers bokførte utlegg (liste): | * |
| `[[*utgift.beskrivelse]]` | Selgers bokførte andre utgifter (liste): | * |
| `[[*faktura.beskrivelse]]` | Selgers bokførte fakturerte poster (liste): | * |

## Oppdragsparter

| Field Path | Display Name | Req |
|------------|-------------|-----|
| `[[arving.navn]]` | Navn hovedkontakt |  |
| `[[arving.navnutenfullmektigogkontaktperson]]` | Navn uten fullmektig |  |
| `[[arving.idnummer]]` | Fødselsnummer/org.nr. |  |
| `[[arving.ledetekst_idnummer]]` | Ledetekst ID-nummer/org.nr. |  |
| `[[arving.fdato_orgnr]]` | Fødselsdato/org.nr. |  |
| `[[arving.eierbrok]]` | Eierbrøk |  |
| `[[arving.ledetekst_fdato_orgnr]]` | Ledetekst fødselsdato/org.nr. |  |
| `[[arving.hovedgatenavnognr]]` | Adresse |  |
| `[[arving.hovedpostnr]]` | Postnr |  |
| `[[arving.hovedpoststed]]` | Poststed |  |
| `[[arving.hovedtlf]]` | Telefon |  |
| `[[arving.hovedepost]]` | E-post |  |
| `[[grunneier.navn]]` | Navn |  |
| `[[grunneier.navnutenfullmektigogkontaktperson]]` | Navn uten fullmektig |  |
| `[[grunneier.idnummer]]` | Fødselsnummer/org.nr. |  |
| `[[grunneier.ledetekst_idnummer]]` | Ledetekst ID-nummer/org.nr. |  |
| `[[grunneier.fdato_orgnr]]` | Fødselsdato/org.nr. |  |
| `[[grunneier.fdato_orgnr_utenpunktum]]` | Fødselsdato/org.nr. uten punktum |  |
| `[[grunneier.ledetekst_fdato_orgnr]]` | Ledetekst fødselsdato/org.nr. |  |
| `[[grunneier.gatenavnognr]]` | Adresse |  |
| `[[grunneier.postnr]]` | Postnr. |  |
| `[[grunneier.poststed]]` | Poststed |  |
| `[[grunneier.tlf]]` | Telefon |  |
| `[[grunneier.epost]]` | E-post |  |
| `[[grunneier.firmanavn]]` | Firmanavn uten kontaktperson |  |
| `[[grunneier.kontaktperson.navn]]` | Firmaets kontaktperson (rolle Kontaktperson)
			(NB! Endret i versjon 4.5) |  |
| `[[grunneier.dagligleder.navn]]` | Daglig leder |  |
| `[[grunneier.signaturberettiget.navn]]` | Signaturberettiget |  |
| `[[grunneier.styreleder.navn]]` | Styreleder |  |
| `[[hjemmelshaver.navn]]` | Navn (kommaseparert, evt.gruppenavn) |  |
| `[[hjemmelshaver.navnutenfullmektigogkontaktperson]]` | Navn uten fullmektig |  |
| `[[hjemmelshaver.firmanavn]]` | Firmanavn uten kontaktperson |  |
| `[[hjemmelshaver.eierbrok]]` | Eierbrøk |  |
| `[[hjemmelshaver.idnummer]]` | Fødselsnummer/org.nr. |  |
| `[[hjemmelshaver.ledetekst_idnummer]]` | Ledetekst ID-nummer/org.nr. |  |
| `[[hjemmelshaver.fdato_orgnr]]` | Fødselsdato/org.nr. |  |
| `[[hjemmelshaver.fdato_orgnr_utenpunktum]]` | Fødselsdato/org.nr. uten punktum |  |
| `[[hjemmelshaver.ledetekst_fdato_orgnr]]` | Ledetekst fødselsdato/org.nr. |  |
| `[[hjemmelshaver.gatenavnognr]]` | Adresse |  |
| `[[hjemmelshaver.postnr]]` | Postnr. |  |
| `[[hjemmelshaver.poststed]]` | Poststed |  |
| `[[hjemmelshaver.tlf]]` | Telefon |  |
| `[[hjemmelshaver.epost]]` | E-post |  |
| `[[tidligereeier.navn]]` | Navn hovedkontakt |  |
| `[[tidligereeier.idnummer]]` | Fødselsnummer/org.nr. |  |
| `[[tidligereeier.ledetekst_idnummer]]` | Ledetekst ID-nummer/org.nr. |  |
| `[[tidligereeier.fdato_orgnr]]` | Fødselsdato/org.nr. |  |
| `[[tidligereeier.ledetekst_fdato_orgnr]]` | Ledetekst fødselsdato/org.nr. |  |
| `[[tidligereeier.hovedgatenavnognr]]` | Adresse |  |
| `[[tidligereeier.hovedpostnr]]` | Postnr |  |
| `[[tidligereeier.hovedpoststed]]` | Poststed |  |
| `[[tidligereeier.hovedtlf]]` | Telefon |  |
| `[[tidligereeier.hovedepost]]` | E-post |  |

## Pant

| Field Path | Display Name | Req |
|------------|-------------|-----|
| `[[kjoperspant.navn]]` | Panthavers navn |  |
| `[[kjoperspant.panthaverorgnr]]` | Panthavers org.nr. |  |
| `[[kjoperspant.type]]` | Pantetype |  |
| `[[kjoperspant.belop]]` | Pålyende verdi |  |
| `[[kjoperspant.dokumentnr]]` | Dokumentnummer |  |
| `[[kjoperspant.tinglystdato]]` | Tinglyst dato |  |
| `[[kjoperspant.dokumentaar]]` | Tinglyst år |  |
| `[[mottaker.kjoperspant.navn]]` | Panthavers navn |  |
| `[[mottaker.kjoperspant.panthaverorgnr]]` | Panthavers org.nr. |  |
| `[[mottaker.kjoperspant.belop]]` | Pålydende verdi |  |
| `[[mottaker.kjoperspant.tinglystdato]]` | Tinglyst dato |  |
| `[[pant.navn]]` | Panthavers navn |  |
| `[[pant.panthaverorgnr]]` | Panthavers org.nr. |  |
| `[[pant.type]]` | Pantetype |  |
| `[[pant.prioritet]]` | Prioritet |  |
| `[[pant.belop]]` | Pålydende verdi |  |
| `[[pant.prosessfullmektignavn]]` | Prosessfullmektig |  |
| `[[pant.prosessfullmektigorgnr]]` | Prosessfullmektiges org.nr. |  |
| `[[pant.restbelop]]` | Restbeløp ikke innfridde lån |  |
| `[[pant.totalrestsaldo]]` | Total restsaldo alle lån, også innfridde |  |
| `[[laan.restsaldo]]` | Restsaldo lån |  |
| `[[laan.restsaldodato]]` | Dato for restsaldo |  |
| `[[laan.kontaktperson]]` | Kontaktperson på pantets lån |  |
| `[[pant.dagboknr]]` | Dokumentnummer (tidl. Dagboksnr.) |  |
| `[[pant.dokumentnr]]` | Dokumentnummer (tidl. Dagboksnr.) |  |
| `[[pant.tinglystdato]]` | Tinglyst dato |  |
| `[[pant.dagbokaar]]` | Tinglyst år (tidl. Dagboksår) |  |
| `[[pant.dokumentaar]]` | Tinglyst år (tidl. Dagboksår) |  |

## Posteringer

| Field Path | Display Name | Req |
|------------|-------------|-----|
| `[[postering.beskrivelse]]` | Beskrivelse |  |
| `[[postering.belop]]` | Beløp |  |
| `[[postering.laannr]]` | Lånnr. |  |
| `[[postering.utbetalingskontonr]]` | Overført til konto |  |
| `[[postering.referanse]]` | Melding/KID |  |
| `[[oppgjorkjoper.sumdebet]]` | Sum debet |  |
| `[[oppgjorkjoper.sumkredit]]` | Sum kredit |  |
| `[[oppgjorkjoper.summva]]` | Sum mva |  |
| `[[oppgjorkjoper.saldo]]` | Saldo kjøper/differanse |  |
| `[[oppgjorselger.sumdebet]]` | Sum debet |  |
| `[[oppgjorselger.sumkredit]]` | Sum kredit |  |
| `[[oppgjorselger.summva]]` | Sum mva |  |
| `[[oppgjorselger.saldo]]` | Saldo selger/differanse |  |

## Prosjekt

| Field Path | Display Name | Req |
|------------|-------------|-----|
| `[[eiendom.prosjektnavn]]` | Prosjektets navn |  |
| `[[eiendom.alfanavn]]` | Alfanavn
			Prosjektenhetens navn |  |
| `[[akseptertbud.belop]]` | Akseptert kjøpetilbud |  |
| `[[akseptertbud.dato]]` | Akseptdato kjøpetilbud |  |
| `[[eiendom.ettaarsbefaring.dato]]` | Ettårsbefaring dato |  |
| `[[eiendom.ettaarsbefaring.klokkeslett]]` | Ettårsbefaring klokkeslett |  |
| `[[eiendom.forhaandsbefaring.dato]]` | Forhåndsbefaring dato |  |
| `[[eiendom.forhaandsbefaring.klokkeslett]]` | Forhåndsbefaring klokkeslett |  |
| `[[oppdrag.prosjekt.antallledigeenheter]]` | Antall ledige enheter |  |
| `[[oppdrag.prosjekt.antallreserverteenheter]]` | Antall reserverte enheter |  |
| `[[oppdrag.prosjekt.antallsolgteenheter]]` | Antall solgte enheter |  |
| `[[oppdrag.prosjekt.antallenheter]]` | Totalt antall enheter |  |
| `[[oppdrag.prosjekt.antallledigemcplasser]]` | Antall ledige MC-plasser |  |
| `[[oppdrag.prosjekt.antallreservertemcplasser]]` | Antall reserverte MC-plasser |  |
| `[[oppdrag.prosjekt.antallsolgtemcplasser]]` | Antall solgte MC-plasser |  |
| `[[oppdrag.prosjekt.totaltantallmcplasser]]` | Totalt antall MC-plasser |  |
| `[[oppdrag.prosjekt.betalingsbetingelser]]` | Betalingsbetingelser |  |
| `[[oppdrag.prosjekt.forbeholdfrautbygger]]` | Forbehold fra utbygger |  |
| `[[oppdrag.prosjekt.prisinformasjon]]` | Prisinformasjon |  |
| `[[oppdrag.prosjekt.tilvalgogendringer]]` | Tilvalg og endringer |  |
| `[[oppdrag.prosjekt.utbyggersforbehold.type]]` | Type forbehold (kommaseparert) |  |
| `[[*forbehold.type]]` | Liste over forbehold | * |
| `[[oppdrag.prosjekt.utbyggersforbehold.fristdato]]` | Forbehold frist dato |  |
| `[[oppdrag.prosjekt.utbyggersforbehold.oppfyltdato]]` | Forbehold oppfylt dato |  |
| `[[oppdrag.prosjekt.utbyggersforbehold.kommentar]]` | Kommentar |  |
| `[[oppdrag.prosjekt.antallledigepplasser]]` | Antall ledige p-plasser |  |
| `[[oppdrag.prosjekt.antallreservertepplasser]]` | Antall reserverte p-plasser |  |
| `[[oppdrag.prosjekt.antallsolgtepplasser]]` | Antall solgte p-plasser |  |
| `[[oppdrag.prosjekt.totaltantallpplasser]]` | Totalt antall p-plasser |  |
| `[[oppdrag.prosjektenhet.antallgarasjeplasser]]` | Antall garasjeplasser |  |
| `[[oppdrag.prosjektenhet.antallbiloppstillingsplasser]]` | Antall biloppstillingsplasser |  |
| `[[oppdrag.prosjektenhet.antallgateparkeringer]]` | Antall gateparkeringer |  |
| `[[oppdrag.prosjektenhet.totaltantallpplasser]]` | Totalt antall p-plasser |  |
| `[[oppdrag.prosjektenhet.antallmcplasser]]` | Antall MC-plasser |  |
| `[[oppdrag.prosjektenhet.totaltantallplasser]]` | Totalt antall plasser (p-plasser og MC-plasser) |  |
| `[[oppdrag.prosjektenhet.parkeringspris]]` | Pris p-plass/totalpris alle p-plasser |  |
| `[[eiendom.utleie]]` | Adgang til utleie |  |
| `[[oppdrag.prosjekt.andreavtaler]]` | Andre avtaler |  |
| `[[oppdrag.prosjekt.andreoppholdsrom]]` | Andre oppholdsrom |  |
| `[[oppdrag.prosjekt.arealberegninger]]` | Arealberegninger |  |
| `[[oppdrag.prosjekt.avbestillinger]]` | Avbestillinger |  |
| `[[oppdrag.prosjekt.avdragsfriperiode]]` | Avdragsfri periode |  |
| `[[oppdrag.prosjekt.bad]]` | Bad |  |
| `[[oppdrag.prosjekt.boder]]` | Boder |  |
| `[[eiendom.ferdigattest]]` | Brukstillatelse og ferdigattest |  |
| `[[oppdrag.prosjekt.diverse]]` | Diverse |  |
| `[[oppdrag.prosjekt.fellesareal]]` | Fellesareal/utomhus/infrastruktur |  |
| `[[oppdrag.prosjekt.felleskostnaderetteravgiftsfriperiode]]` | Felleskostnader etter avgiftsfri periode |  |
| `[[oppdrag.prosjekt.finansieringskontroll]]` | Finansieringskontroll |  |
| `[[oppdrag.prosjekt.forsikringsselskap]]` | Forsikringsselskap |  |
| `[[oppdrag.prosjekt.fremdriftsplanogferdigstillelse]]` | Fremdriftsplan og ferdigstillelse |  |
| `[[oppdrag.prosjekt.garasjeparkering]]` | Garasje/parkering |  |
| `[[oppdrag.prosjekt.garderobe]]` | Garderobe-fasiliteter |  |
| `[[oppdrag.prosjekt.orientering]]` | Generell orientering |  |
| `[[eiendom.hvitvasking]]` | Hvitvaskingsloven |  |
| `[[oppdrag.prosjekt.eiendomsskatt]]` | Info eiendomsskatt |  |
| `[[oppdrag.prosjekt.kommunaleavgifter]]` | Info kommunale avgifter |  |
| `[[oppdrag.prosjekt.formuesverdi]]` | Info om formuesverdi |  |
| `[[oppdrag.prosjekt.vannavgift]]` | Info om vannavgift |  |
| `[[oppdrag.prosjekt.kjokken]]` | Kjøkken |  |
| `[[oppdrag.prosjekt.kjopekontrakt]]` | Kjøpekontrakt |  |
| `[[eiendom.legalpant]]` | Legalpant |  |
| `[[oppdrag.prosjekt.laanebetingelserfellesgjeld]]` | Lånebetingelser fellesgjeld |  |
| `[[oppdrag.prosjekt.omprosjektet]]` | Om prosjektet |  |
| `[[oppdrag.prosjekt.omkostninger]]` | Omkostninger |  |
| `[[oppdrag.prosjekt.organisasjonsform]]` | Organisasjonsform |  |
| `[[eiendom.radonmaaling]]` | Radonmåling |  |
| `[[eiendom.regulering]]` | Reguleringsplan og rammeavtale |  |
| `[[oppdrag.prosjekt.salgavkontraktsposisjoner]]` | Salg av kontraktsposisjoner |  |
| `[[oppdrag.prosjekt.salgsbetingelser]]` | Salgsbetingelser og kjøpetilbud |  |
| `[[oppdrag.prosjekt.stipuleringavfellesgjeld]]` | Stipulering av fellesgjeld |  |
| `[[oppdrag.prosjekt.stipuleringavfellesutgifter]]` | Stipulering av fellesutgifter |  |
| `[[oppdrag.prosjekt.stipulertovertakelse]]` | Stipulert overtakelse |  |
| `[[oppdrag.prosjekt.stipulertovertakelsekommentar]]` | Stipulert overtakelse kommentar |  |
| `[[oppdrag.prosjekt.saerskilteavtaler]]` | Særskilte avtaler |  |
| `[[oppdrag.prosjekt.laanefinansiering]]` | Tilbud på lånefinansiering |  |
| `[[eiendom.vedtekter]]` | Vedtekter/husordensregler |  |
| `[[eiendom.veivannavlop]]` | Vei, vann og avløp |  |
| `[[eiendom.velavgiftkommentar]]` | Velavgift kommentar |  |
| `[[oppdrag.prosjekt.velforening]]` | Velforening |  |
| `[[oppdrag.prosjekt.viktiginformasjon]]` | Viktig informasjon |  |
| `[[oppdrag.prosjekt.vederlagenhetssalg]]` | Ledetekst for enhetssalg
			«Til og med salg nr. X» |  |
| `[[oppdrag.prosjekt.provisjonstype]]` | Type vederlag |  |
| `[[oppdrag.prosjekt.provisjonprosent]]` | Prosentsats inkl. mva (for provisjon) |  |
| `[[oppdrag.prosjekt.provisjonprosenteksmva]]` | Prosentsats ekskl. mva (for provisjon) |  |
| `[[oppdrag.prosjekt.fastpris]]` | Fastpris beløp inkl. mva (for fastpris) |  |
| `[[oppdrag.prosjekt.fastpriseksmva]]` | Fastpris beløp ekskl. mva (for fastpris) |  |

## Selgere

| Field Path | Display Name | Req |
|------------|-------------|-----|
| `[[selger.navn]]` | Navn (kommaseparert, evt.gruppenavn) |  |
| `[[selger.fornavn]]` | Fornavn (kun et navn flettes, evt. «v/<fullmektig>») |  |
| `[[selger.etternavn]]` | Etternavn (kun et navn flettes, evt. «v/<fullmektig>») |  |
| `[[selger.navnutenfullmektigogkontaktperson]]` | Navn uten fullmektig
			(NB! Endret i versjon 5.1) |  |
| `[[selger.idnummer]]` | Fødselsnummer/org.nr. |  |
| `[[selger.ledetekst_idnummer]]` | Ledetekst ID-nummer/org.nr. |  |
| `[[selger.fdato_orgnr]]` | Fødselsdato/org.nr. |  |
| `[[selger.fdato_orgnr_uten punktum]]` | Fødselsdato/org.nr. uten punktum |  |
| `[[selger.ledetekst_fdato_orgnr]]` | Ledetekst fødselsdato/org.nr. |  |
| `[[selger.hovedgatenavnognr]]` | Adresse |  |
| `[[selger.adresse]]` | Adresse inkl. postnr og sted |  |
| `[[selger.hovedpostnr]]` | Postnr. |  |
| `[[selger.hovedpoststed]]` | Poststed |  |
| `[[selger.hovedtlf]]` | Telefon |  |
| `[[selger.hovedepost]]` | E-post |  |
| `[[selger.hovedkontonummer]]` | Kontonummer |  |
| `[[selger.ergift]]` | Er selger gift? |  |
| `[[selger.selgersektefelle.navn]]` | Ektefelles navn |  |
| `[[selger.selgersektefelle.navnutenfullmektig]]` | Ektefelles navn uten fullmektig |  |
| `[[selger.selgersektefelle.ledetekst_idnummer]]` | Ektefelles ledetekst ID-nummer |  |
| `[[selger.selgersektefelle.idnummer]]` | Ektefelles ID-nummer |  |
| `[[selger.selgersektefelle.ledetekst_fdato]]` | Ektefelles ledetekst fødselsdato |  |
| `[[selger.selgersektefelle.fdato]]` | Ektefelles fødselsdato |  |
| `[[selger.selgersektefelle.gatenavnognr]]` | Ektefelles gatenavn og nummer |  |
| `[[selger.selgersektefelle.postnr]]` | Ektefelles postnummer |  |
| `[[selger.selgersektefelle.poststed]]` | Ektefelles poststed |  |
| `[[selger.selgersektefelle.tlf]]` | Ektefelles telefon |  |
| `[[selger.selgersektefelle.epost]]` | Ektefelles e-post |  |
| `[[selger.fullmektig.navn]]` | Navn |  |
| `[[selger.fullmektig.idnummer]]` | Fødselsnummer/org.nr. |  |
| `[[selger.fullmektig.ledetekst_idnummer]]` | Ledetekst ID-nummer/org.nr. |  |
| `[[selger.fullmektig.fdato_orgnr]]` | Fødselsdato/org.nr. |  |
| `[[selger.fullmektig.ledetekst_fdato_orgnr]]` | Ledetekst fødselsdato/org.nr. |  |
| `[[selger.fullmektig.gatenavnognr]]` | Adresse |  |
| `[[selger.fullmektig.postnr]]` | Postnr. |  |
| `[[selger.fullmektig.poststed]]` | Poststed |  |
| `[[selger.fullmektig.tlf]]` | Telefon |  |
| `[[selger.fullmektig.epost]]` | E-post |  |
| `[[selger.firmanavn]]` | Firmanavn uten kontaktperson |  |
| `[[selger.kontaktperson.navn]]` | Firmaets kontaktperson (rolle Kontaktperson)
			(NB! Endret i versjon 4.5) |  |
| `[[selger.dagligleder.navn]]` | Daglig leder |  |
| `[[selger.signaturberettiget.navn]]` | Signaturberettiget |  |
| `[[selger.signaturberettiget.idnummer]]` | Signaturberettigets fødselsnummer |  |
| `[[selger.styreleder.navn]]` | Styreleder |  |

## Skjemamaler (skjøte/sikring/hjemmelserklæring) Se innstillinger i Admin-menyen

| Field Path | Display Name | Req |
|------------|-------------|-----|
| `[[skjema.innsender.navn]]` | Innsenders navn |  |
| `[[skjema.innsender.orgnr]]` | Innsenders org.nr |  |
| `[[skjema.innsender.adresse]]` | Innsenders adresse |  |
| `[[skjema.innsender.postnr]]` | Innsenders postnr |  |
| `[[skjema.innsender.poststed]]` | Innsenders poststed |  |
| `[[skjema.pantsetter.navn]]` | Pantsetters navn |  |
| `[[skjema.pantsetter.orgnr]]` | Pantsetters org.nr |  |
| `[[skjema.referansenr]]` | Referansenummer for skjemaet |  |

## Tvangssalg

| Field Path | Display Name | Req |
|------------|-------------|-----|
| `[[tvangssalg.begjaringomstadfestelse.dato]]` | Begjæring om stadfestelse |  |
| `[[tvangssalg.fordelingskjennelse.dato]]` | Fordelingskjennelsesdato |  |
| `[[tvangssalgrefnr]]` | Saksnummer tvangssalg |  |
| `[[tvangssalg.stadfestelseskjennelse.dato]]` | Stadfestelsesdato |  |
| `[[saksoker.navn]]` | Navn |  |
| `[[saksoker.navnutenfullmektigogkontaktperson]]` | Navn uten fullmektig |  |
| `[[saksoker.idnummer]]` | Fødselsnummer/org.nr. |  |
| `[[saksoker.ledetekst_idnummer]]` | Ledetekst ID-nummer/org.nr. |  |
| `[[saksoker.fdato_orgnr]]` | Fødselsdato/org.nr. |  |
| `[[saksoker.fdato_orgnr_utenpunktum]]` | Fødselsdato/org.nr. uten punktum |  |
| `[[saksoker.ledetekst_fdato_orgnr]]` | Ledetekst fødselsdato/org.nr. |  |
| `[[saksoker.gatenavnognr]]` | Adresse |  |
| `[[saksoker.postnr]]` | Postnr. |  |
| `[[saksoker.poststed]]` | Poststed |  |
| `[[saksoker.prosessfullmektignavn]]` | Prosessfullmektiges navn |  |
| `[[saksoker.prosessfullmektigorgnr]]` | Prosessfullmektiges org.nr. |  |
| `[[saksoker.firmanavn]]` | Firmanavn uten kontaktperson |  |
| `[[saksoker.kontaktperson.navn]]` | Firmaets kontaktperson (rolle Kontaktperson)
			(NB! Endret i versjon 4.5) |  |
| `[[saksoker.dagligleder.navn]]` | Daglig leder |  |
| `[[saksoker.signaturberettiget.navn]]` | Signaturberettiget |  |
| `[[saksoker.styreleder.navn]]` | Styreleder |  |
| `[[saksoker.pant.type]]` | Pantetype |  |
| `[[saksoker.pant.prioritet]]` | Prioritet |  |
| `[[saksoker.pant.belop]]` | Pålydende verdi |  |
| `[[saksoker.pant.restbelop]]` | Restbeløp ikke innfridde lån |  |
| `[[saksoker.pant.totalrestsaldo]]` | Total restsaldo alle lån |  |
| `[[saksoker.pant.dokumentnr]]` | Dokumentnummer |  |
| `[[saksoker.pant.tinglystdato]]` | Tinglyst dato |  |
| `[[saksoker.pant.dokumentaar]]` | Tinglyst år |  |
| `[[saksoker.laan.restsaldodato]]` | Dato for restsaldo lån |  |
| `[[saksoker.laan.kontaktperson]]` | Kontaktperson lån |  |
| `[[saksokte.navn]]` | Navn |  |
| `[[saksokte.navnutenfullmektigogkontaktperson]]` | Navn uten fullmektig |  |
| `[[saksokte.idnummer]]` | Fødselsnummer/org.nr. |  |
| `[[saksokte.ledetekst_idnummer]]` | Ledetekst ID-nummer/org.nr. |  |
| `[[saksokte.fdato_orgnr]]` | Fødselsdato/org.nr. |  |
| `[[saksokte.fdato_orgnr_utenpunktum]]` | Fødselsdato/org.nr. uten punktum |  |
| `[[saksokte.ledetekst_fdato_orgnr]]` | Ledetekst fødselsdato/org.nr. |  |
| `[[saksokte.gatenavnognr]]` | Adresse |  |
| `[[saksokte.postnr]]` | Postnr. |  |
| `[[saksokte.poststed]]` | Poststed |  |
| `[[saksokte.tlf]]` | Telefon |  |
| `[[saksokte.epost]]` | E-post |  |
| `[[saksokte.firmanavn]]` | Firmanavn uten kontaktperson |  |
| `[[saksokte.kontaktperson.navn]]` | Firmaets kontaktperson (rolle Kontaktperson)
			(NB! Endret i versjon 4.5) |  |
| `[[saksokte.dagligleder.navn]]` | Daglig leder |  |
| `[[saksokte.signaturberettiget.navn]]` | Signaturberettiget |  |
| `[[saksokte.styreleder.navn]]` | Styreleder |  |

## Visninger

| Field Path | Display Name | Req |
|------------|-------------|-----|
| `[[oppdrag.antallvisninger]]` | Antall visninger |  |
| `[[eiendom.nestevisning.formaterttekst]]` | Førstkommende visning
			(fra tidspunktet dokumentet ble produsert) |  |
| `[[eiendom.nestefellesvisning.formaterttekst]]` | Førstkommende fellesvisning
			(fra tidspunktet dokumentet ble produsert) |  |
| `[[eiendom.nesteprivatvisning.formaterttekst]]` | Førstkommende privatvisning
			(fra tidspunktet dokumentet ble produsert) |  |
| `[[*visning.type]]` | Type visning | * |
| `[[*visning.antallinteressenter]]` | Antall interessenter (hele visningen) | * |
| `[[*visning.formaterttekst]]` | Visningstid | * |
| `[[*slot.tidsrom]]` | Klokkeslett fra og til | * |
| `[[*slot.klokkeslettfra]]` | Klokkeslett fra | * |
| `[[*slot.klokkesletttil]]` | Klokkeslett til | * |

## Klikkbare sjekklister og radioknapper / skjemaoppsett

| Field Path | Display Name | Req |
|------------|-------------|-----|
| `[[eiendom.gatenavnognr]]` | Skjema |  |

## Formatering

| Field Path | Display Name | Req |
|------------|-------------|-----|
| `[[eiendom.pris]]` | Beløp uten desimaler |  |
| `[[oppgjorkjoper.saldo]]` | Beløp uten minustegn foran |  |
| `[[eiendom.prom]]` | Areal uten desimaler |  |

## Kalkulering

| Field Path | Display Name | Req |
|------------|-------------|-----|
| `[[oppdrag.timeprisinklmva]]` | Divisjon
			Benytt komma eller punktum i desimaltall |  |
| `[[oppdrag.timebudsjettantall]]` | Summering av timer |  |
| `[[timer.budsjett.visning]]` | Multiplikasjon med timer |  |

## Beløp som bokstaver

| Field Path | Display Name | Req |
|------------|-------------|-----|
| `[[kontraktsposisjon.totalpris]]` | Beløp som bokstaver |  |
| `[[eiendom.pris]]` | Kalkulering som bokstaver |  |
| `[[eiendom.fellesgjeld]]` | Kalkulering som bokstaver |  |

## Ulike spørringer

| Field Path | Display Name | Req |
|------------|-------------|-----|
| `[[*kostnad.belop]]` | Pris for parkeringsplass(ene): | * |
| `[[eiendom.grunntype]]` | Liten æ
			Stor Æ 
			
			Eks: Objektets grunntype = Næring? |  |
| `[[oppdrag.hovedtype]]` | Liten ø
			Stor Ø 
			
			Eks: Oppdragskategori = Oppgjør? |  |
| `[[eiendom.poststed]]` | Liten å
			Stor Å 
			
			Eks: Objektets poststed = Årnes? |  |
| `[[meglerkontor.internid]]` | MeglerkontorID starter med "2"? |  |
| `[[operativmegler.navn]]` | Meglers ID starter med "J"? |  |
| `[[eiendom.gatenavnognr]]` | Adressen inneholder "veien"? |  |
| `[[oppdrag.antallvisninger]]` | Har dette oppdraget hatt visninger? |  |
| `[[oppdrag.prosjektenhet.antallgarasjeplasser]]` | Har denne prosjektenheten 3 eller færre garasjeplasser? |  |
| `[[*pant.prioritet]]` | Hva er det to første pantene? | * |

---

**Total unique fields: 668**

For fields not listed here, search `Alle-flettekoder-25.9.md` directly.
