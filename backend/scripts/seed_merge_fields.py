"""
Seed Merge Fields Script

Populates the database with all Vitec Next merge fields from the reference.
Based on .cursor/vitec-reference.md

Run with: python -m scripts.seed_merge_fields
Or remotely: python backend/scripts/seed_merge_fields.py --api-url <URL>
"""

import asyncio
import sys
import os
import argparse
import requests
from typing import List, Dict, Any

# Add parent directory to path for local execution
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# =============================================================================
# VITEC MERGE FIELDS DATA
# Based on .cursor/vitec-reference.md
# =============================================================================

MERGE_FIELDS: List[Dict[str, Any]] = [
    # ----- MEGLERKONTOR -----
    {"path": "meglerkontor.navn", "category": "Meglerkontor", "label": "Kontornavn", "data_type": "string"},
    {"path": "meglerkontor.juridisknavn", "category": "Meglerkontor", "label": "Juridisk navn", "data_type": "string"},
    {"path": "meglerkontor.kjedenavn", "category": "Meglerkontor", "label": "Kjedenavn", "data_type": "string"},
    {"path": "meglerkontor.orgnr", "category": "Meglerkontor", "label": "Organisasjonsnummer", "data_type": "string"},
    {"path": "meglerkontor.adresse", "category": "Meglerkontor", "label": "Postadresse", "data_type": "string"},
    {"path": "meglerkontor.postnr", "category": "Meglerkontor", "label": "Postnummer", "data_type": "string"},
    {"path": "meglerkontor.poststed", "category": "Meglerkontor", "label": "Poststed", "data_type": "string"},
    {"path": "meglerkontor.besoksadresse", "category": "Meglerkontor", "label": "Besoksadresse", "data_type": "string"},
    {"path": "meglerkontor.besokspostnr", "category": "Meglerkontor", "label": "Besokspostnummer", "data_type": "string"},
    {"path": "meglerkontor.besokspoststed", "category": "Meglerkontor", "label": "Besokspoststed", "data_type": "string"},
    {"path": "meglerkontor.tlf", "category": "Meglerkontor", "label": "Telefon", "data_type": "string"},
    {"path": "meglerkontor.epost", "category": "Meglerkontor", "label": "E-post", "data_type": "string"},
    {"path": "meglerkontor.firmalogourl", "category": "Meglerkontor", "label": "Logo URL", "data_type": "string"},
    {"path": "meglerkontor.webadresse", "category": "Meglerkontor", "label": "Webside", "data_type": "string"},
    
    # ----- AVSENDER -----
    {"path": "avsender.navn", "category": "Avsender", "label": "Fullt navn", "data_type": "string"},
    {"path": "avsender.fornavn", "category": "Avsender", "label": "Fornavn", "data_type": "string"},
    {"path": "avsender.etternavn", "category": "Avsender", "label": "Etternavn", "data_type": "string"},
    {"path": "avsender.tittel", "category": "Avsender", "label": "Tittel/stilling", "data_type": "string"},
    {"path": "avsender.tlf", "category": "Avsender", "label": "Telefon", "data_type": "string"},
    {"path": "avsender.mobiltlf", "category": "Avsender", "label": "Mobiltelefon", "data_type": "string"},
    {"path": "avsender.epost", "category": "Avsender", "label": "E-post", "data_type": "string"},
    {"path": "avsender.meglerkontor.navn", "category": "Avsender", "label": "Kontorets navn", "data_type": "string"},
    {"path": "avsender.meglerkontor.adresse", "category": "Avsender", "label": "Kontorets adresse", "data_type": "string"},
    {"path": "avsender.meglerkontor.postnr", "category": "Avsender", "label": "Kontorets postnummer", "data_type": "string"},
    {"path": "avsender.meglerkontor.poststed", "category": "Avsender", "label": "Kontorets poststed", "data_type": "string"},
    {"path": "avsender.meglerkontor.besoksadresse", "category": "Avsender", "label": "Besoksadresse", "data_type": "string"},
    
    # ----- MOTTAKER -----
    {"path": "mottaker.navn", "category": "Mottaker", "label": "Fullt navn", "data_type": "string"},
    {"path": "mottaker.fornavn", "category": "Mottaker", "label": "Fornavn", "data_type": "string"},
    {"path": "mottaker.etternavn", "category": "Mottaker", "label": "Etternavn", "data_type": "string"},
    {"path": "mottaker.adresse", "category": "Mottaker", "label": "Adresse", "data_type": "string"},
    {"path": "mottaker.postnr", "category": "Mottaker", "label": "Postnummer", "data_type": "string"},
    {"path": "mottaker.poststed", "category": "Mottaker", "label": "Poststed", "data_type": "string"},
    {"path": "mottaker.epost", "category": "Mottaker", "label": "E-post", "data_type": "string"},
    {"path": "mottaker.mobiltlf", "category": "Mottaker", "label": "Mobiltelefon", "data_type": "string"},
    {"path": "mottaker.tlf", "category": "Mottaker", "label": "Telefon", "data_type": "string"},
    
    # ----- EIENDOM -----
    {"path": "eiendom.adresse", "category": "Eiendom", "label": "Adresse", "data_type": "string"},
    {"path": "eiendom.postnr", "category": "Eiendom", "label": "Postnummer", "data_type": "string"},
    {"path": "eiendom.poststed", "category": "Eiendom", "label": "Poststed", "data_type": "string"},
    {"path": "eiendom.kommunenr", "category": "Eiendom", "label": "Kommunenummer", "data_type": "string"},
    {"path": "eiendom.kommunenavn", "category": "Eiendom", "label": "Kommunenavn", "data_type": "string"},
    {"path": "eiendom.gnr", "category": "Eiendom", "label": "Gardsnummer", "data_type": "number"},
    {"path": "eiendom.bnr", "category": "Eiendom", "label": "Bruksnummer", "data_type": "number"},
    {"path": "eiendom.fnr", "category": "Eiendom", "label": "Festenummer", "data_type": "number"},
    {"path": "eiendom.snr", "category": "Eiendom", "label": "Seksjonsnummer", "data_type": "number"},
    {"path": "eiendom.matrikkel", "category": "Eiendom", "label": "Full matrikkelbetegnelse", "data_type": "string"},
    {"path": "eiendom.eieform", "category": "Eiendom", "label": "Eieform", "data_type": "string", "example_value": "Eiet, Andel, Aksje"},
    {"path": "eiendom.objektstype", "category": "Eiendom", "label": "Objektstype", "data_type": "string", "example_value": "Enebolig, Leilighet"},
    {"path": "eiendom.boligareal", "category": "Eiendom", "label": "Boligareal (BOA)", "data_type": "number"},
    {"path": "eiendom.bruksareal", "category": "Eiendom", "label": "Bruksareal (BRA)", "data_type": "number"},
    {"path": "eiendom.tomteareal", "category": "Eiendom", "label": "Tomteareal", "data_type": "number"},
    {"path": "eiendom.etasje", "category": "Eiendom", "label": "Etasje", "data_type": "string"},
    {"path": "eiendom.byggeaar", "category": "Eiendom", "label": "Byggeaar", "data_type": "number"},
    {"path": "eiendom.rom", "category": "Eiendom", "label": "Antall rom", "data_type": "number"},
    {"path": "eiendom.soverom", "category": "Eiendom", "label": "Antall soverom", "data_type": "number"},
    {"path": "eiendom.bad", "category": "Eiendom", "label": "Antall bad", "data_type": "number"},
    {"path": "eiendom.garasje", "category": "Eiendom", "label": "Garasjetype", "data_type": "string"},
    {"path": "eiendom.energimerke", "category": "Eiendom", "label": "Energimerke", "data_type": "string"},
    {"path": "eiendom.oppvarming", "category": "Eiendom", "label": "Oppvarmingstype", "data_type": "string"},
    {"path": "eiendom.regulering", "category": "Eiendom", "label": "Reguleringsplan", "data_type": "string"},
    {"path": "eiendom.tinglystreferanse", "category": "Eiendom", "label": "Tinglyst referanse", "data_type": "string"},
    {"path": "eiendom.hovedbilde", "category": "Eiendom", "label": "Hovedbilde URL", "data_type": "string"},
    
    # ----- OPPDRAG -----
    {"path": "oppdrag.oppdragsnr", "category": "Oppdrag", "label": "Oppdragsnummer", "data_type": "string"},
    {"path": "oppdrag.referansenr", "category": "Oppdrag", "label": "Referansenummer", "data_type": "string"},
    {"path": "oppdrag.type", "category": "Oppdrag", "label": "Oppdragstype", "data_type": "string"},
    {"path": "oppdrag.kategori", "category": "Oppdrag", "label": "Oppdragskategori", "data_type": "string"},
    {"path": "oppdrag.status", "category": "Oppdrag", "label": "Status", "data_type": "string"},
    {"path": "oppdrag.oppdragsdato", "category": "Oppdrag", "label": "Oppdragsdato", "data_type": "date"},
    {"path": "oppdrag.utlopsdato", "category": "Oppdrag", "label": "Utlopsdato", "data_type": "date"},
    {"path": "oppdrag.prisantydning", "category": "Oppdrag", "label": "Prisantydning", "data_type": "number"},
    {"path": "oppdrag.solgtpris", "category": "Oppdrag", "label": "Solgt pris", "data_type": "number"},
    {"path": "oppdrag.salgssum", "category": "Oppdrag", "label": "Salgssum", "data_type": "number"},
    {"path": "oppdrag.fellesgjeld", "category": "Oppdrag", "label": "Fellesgjeld", "data_type": "number"},
    {"path": "oppdrag.totalpris", "category": "Oppdrag", "label": "Totalpris", "data_type": "number"},
    {"path": "oppdrag.akseptdato", "category": "Oppdrag", "label": "Akseptdato", "data_type": "date"},
    {"path": "oppdrag.kontraktsdato", "category": "Oppdrag", "label": "Kontraktsdato", "data_type": "date"},
    {"path": "oppdrag.overtakelse", "category": "Oppdrag", "label": "Overtakelsesdato", "data_type": "date"},
    {"path": "oppdrag.oppgjorsdato", "category": "Oppdrag", "label": "Oppgjorsdato", "data_type": "date"},
    
    # ----- ANSVARLIG MEGLER -----
    {"path": "ansvarligmegler.navn", "category": "Ansvarlig megler", "label": "Fullt navn", "data_type": "string"},
    {"path": "ansvarligmegler.tittel", "category": "Ansvarlig megler", "label": "Tittel", "data_type": "string"},
    {"path": "ansvarligmegler.epost", "category": "Ansvarlig megler", "label": "E-post", "data_type": "string"},
    {"path": "ansvarligmegler.tlf", "category": "Ansvarlig megler", "label": "Telefon", "data_type": "string"},
    {"path": "ansvarligmegler.mobiltlf", "category": "Ansvarlig megler", "label": "Mobil", "data_type": "string"},
    
    # ----- OPPGJORSANSVARLIG -----
    {"path": "oppgjorsansvarlig.navn", "category": "Oppgjorsansvarlig", "label": "Fullt navn", "data_type": "string"},
    {"path": "oppgjorsansvarlig.tittel", "category": "Oppgjorsansvarlig", "label": "Tittel", "data_type": "string"},
    {"path": "oppgjorsansvarlig.epost", "category": "Oppgjorsansvarlig", "label": "E-post", "data_type": "string"},
    {"path": "oppgjorsansvarlig.tlf", "category": "Oppgjorsansvarlig", "label": "Telefon", "data_type": "string"},
    
    # ----- MEGLER 1 -----
    {"path": "megler1.navn", "category": "Megler 1", "label": "Fullt navn", "data_type": "string"},
    {"path": "megler1.tittel", "category": "Megler 1", "label": "Tittel", "data_type": "string"},
    {"path": "megler1.epost", "category": "Megler 1", "label": "E-post", "data_type": "string"},
    {"path": "megler1.tlf", "category": "Megler 1", "label": "Telefon", "data_type": "string"},
    {"path": "megler1.mobiltlf", "category": "Megler 1", "label": "Mobil", "data_type": "string"},
    
    # ----- MEGLER 2 -----
    {"path": "megler2.navn", "category": "Megler 2", "label": "Fullt navn", "data_type": "string"},
    {"path": "megler2.tittel", "category": "Megler 2", "label": "Tittel", "data_type": "string"},
    {"path": "megler2.epost", "category": "Megler 2", "label": "E-post", "data_type": "string"},
    {"path": "megler2.tlf", "category": "Megler 2", "label": "Telefon", "data_type": "string"},
    {"path": "megler2.mobiltlf", "category": "Megler 2", "label": "Mobil", "data_type": "string"},
    
    # ----- MEDHJELPER -----
    {"path": "medhjelper.navn", "category": "Medhjelper", "label": "Fullt navn", "data_type": "string"},
    {"path": "medhjelper.tittel", "category": "Medhjelper", "label": "Tittel", "data_type": "string"},
    {"path": "medhjelper.epost", "category": "Medhjelper", "label": "E-post", "data_type": "string"},
    {"path": "medhjelper.tlf", "category": "Medhjelper", "label": "Telefon", "data_type": "string"},
    {"path": "medhjelper.mobiltlf", "category": "Medhjelper", "label": "Mobil", "data_type": "string"},
    
    # ----- SALGSMEGLER -----
    {"path": "salgsmegler.navn", "category": "Salgsmegler", "label": "Fullt navn", "data_type": "string"},
    {"path": "salgsmegler.tittel", "category": "Salgsmegler", "label": "Tittel", "data_type": "string"},
    {"path": "salgsmegler.epost", "category": "Salgsmegler", "label": "E-post", "data_type": "string"},
    {"path": "salgsmegler.tlf", "category": "Salgsmegler", "label": "Telefon", "data_type": "string"},
    {"path": "salgsmegler.mobiltlf", "category": "Salgsmegler", "label": "Mobil", "data_type": "string"},
    
    # ----- SELGER -----
    {"path": "selger.navn", "category": "Selger", "label": "Navn (forste selger)", "data_type": "string"},
    {"path": "selger.fornavn", "category": "Selger", "label": "Fornavn", "data_type": "string"},
    {"path": "selger.etternavn", "category": "Selger", "label": "Etternavn", "data_type": "string"},
    {"path": "selger.fodselsnr", "category": "Selger", "label": "Fodselsnummer", "data_type": "string"},
    {"path": "selger.adresse", "category": "Selger", "label": "Adresse", "data_type": "string"},
    {"path": "selger.postnr", "category": "Selger", "label": "Postnummer", "data_type": "string"},
    {"path": "selger.poststed", "category": "Selger", "label": "Poststed", "data_type": "string"},
    {"path": "selger.epost", "category": "Selger", "label": "E-post", "data_type": "string"},
    {"path": "selger.tlf", "category": "Selger", "label": "Telefon", "data_type": "string"},
    {"path": "selger.mobiltlf", "category": "Selger", "label": "Mobil", "data_type": "string"},
    {"path": "selger.bankkonto", "category": "Selger", "label": "Bankkonto", "data_type": "string"},
    {"path": "selger.bankkontonavn", "category": "Selger", "label": "Kontonavn", "data_type": "string"},
    {"path": "selger.andel", "category": "Selger", "label": "Eierandel", "data_type": "number"},
    
    # ----- SELGERE (iterable) -----
    {"path": "selgere", "category": "Selgere", "label": "Liste over selgere", "data_type": "array", "is_iterable": True, "parent_model": "Model"},
    
    # ----- KJOPER -----
    {"path": "kjoper.navn", "category": "Kjoper", "label": "Navn (forste kjoper)", "data_type": "string"},
    {"path": "kjoper.fornavn", "category": "Kjoper", "label": "Fornavn", "data_type": "string"},
    {"path": "kjoper.etternavn", "category": "Kjoper", "label": "Etternavn", "data_type": "string"},
    {"path": "kjoper.fodselsnr", "category": "Kjoper", "label": "Fodselsnummer", "data_type": "string"},
    {"path": "kjoper.adresse", "category": "Kjoper", "label": "Adresse", "data_type": "string"},
    {"path": "kjoper.postnr", "category": "Kjoper", "label": "Postnummer", "data_type": "string"},
    {"path": "kjoper.poststed", "category": "Kjoper", "label": "Poststed", "data_type": "string"},
    {"path": "kjoper.epost", "category": "Kjoper", "label": "E-post", "data_type": "string"},
    {"path": "kjoper.tlf", "category": "Kjoper", "label": "Telefon", "data_type": "string"},
    {"path": "kjoper.mobiltlf", "category": "Kjoper", "label": "Mobil", "data_type": "string"},
    {"path": "kjoper.bankkonto", "category": "Kjoper", "label": "Bankkonto", "data_type": "string"},
    {"path": "kjoper.andel", "category": "Kjoper", "label": "Kjopsandel", "data_type": "number"},
    
    # ----- KJOPERE (iterable) -----
    {"path": "kjopere", "category": "Kjopere", "label": "Liste over kjopere", "data_type": "array", "is_iterable": True, "parent_model": "Model"},
    
    # ----- OPPDRAGSPARTER -----
    {"path": "arving.navn", "category": "Arving", "label": "Navn", "data_type": "string"},
    {"path": "arving.fodselsnr", "category": "Arving", "label": "Fodselsnummer", "data_type": "string"},
    {"path": "arving.andel", "category": "Arving", "label": "Arveandel", "data_type": "number"},
    
    {"path": "grunneier.navn", "category": "Grunneier", "label": "Navn", "data_type": "string"},
    {"path": "grunneier.adresse", "category": "Grunneier", "label": "Adresse", "data_type": "string"},
    
    {"path": "hjemmelshaver.navn", "category": "Hjemmelshaver", "label": "Navn", "data_type": "string"},
    {"path": "hjemmelshaver.fodselsnr", "category": "Hjemmelshaver", "label": "Fodselsnummer", "data_type": "string"},
    
    {"path": "tidligereeierdod.navn", "category": "Tidligere eier/avdod", "label": "Navn", "data_type": "string"},
    {"path": "tidligereeierdod.dodsdato", "category": "Tidligere eier/avdod", "label": "Dodsdato", "data_type": "date"},
    
    # ----- BORETTSLAG / SAMEIE / AKSJELAG -----
    {"path": "borettslag.navn", "category": "Borettslag", "label": "Navn", "data_type": "string"},
    {"path": "borettslag.orgnr", "category": "Borettslag", "label": "Organisasjonsnummer", "data_type": "string"},
    {"path": "borettslag.adresse", "category": "Borettslag", "label": "Adresse", "data_type": "string"},
    {"path": "borettslag.postnr", "category": "Borettslag", "label": "Postnummer", "data_type": "string"},
    {"path": "borettslag.poststed", "category": "Borettslag", "label": "Poststed", "data_type": "string"},
    {"path": "borettslag.forretningsforernavn", "category": "Borettslag", "label": "Forretningsforernavn", "data_type": "string"},
    {"path": "borettslag.forretningsforertlf", "category": "Borettslag", "label": "Forretningsforer telefon", "data_type": "string"},
    {"path": "borettslag.andelsnr", "category": "Borettslag", "label": "Andelsnummer", "data_type": "string"},
    {"path": "borettslag.aksjenr", "category": "Borettslag", "label": "Aksjenummer", "data_type": "string"},
    {"path": "borettslag.seksjonsnr", "category": "Borettslag", "label": "Seksjonsnummer", "data_type": "string"},
    
    # ----- KONTRAKT -----
    {"path": "kontrakt.kontraktsdato", "category": "Kontrakt", "label": "Kontraktsdato", "data_type": "date"},
    {"path": "kontrakt.overtakelse", "category": "Kontrakt", "label": "Overtakelsesdato", "data_type": "date"},
    {"path": "kontrakt.kjoperbetalingsplan", "category": "Kontrakt", "label": "Betalingsplan kjoper", "data_type": "string"},
    {"path": "kontrakt.kjoperforbehold", "category": "Kontrakt", "label": "Forbehold kjoper", "data_type": "string"},
    {"path": "kontrakt.selgerforbehold", "category": "Kontrakt", "label": "Forbehold selger", "data_type": "string"},
    {"path": "kontrakt.tilleggsavtale", "category": "Kontrakt", "label": "Tilleggsavtaler", "data_type": "string"},
    {"path": "kontrakt.inventarliste", "category": "Kontrakt", "label": "Inventarliste", "data_type": "string"},
    
    # ----- PANT -----
    {"path": "pant.belopskr", "category": "Pant", "label": "Pantebelop (kr)", "data_type": "number"},
    {"path": "pant.belopbokstaver", "category": "Pant", "label": "Pantebelop i bokstaver", "data_type": "string"},
    {"path": "pant.panthaver", "category": "Pant", "label": "Panthavers navn", "data_type": "string"},
    {"path": "pant.prioritet", "category": "Pant", "label": "Prioritet", "data_type": "number"},
    {"path": "pant.type", "category": "Pant", "label": "Panttype", "data_type": "string"},
    {"path": "pant.dokumentnr", "category": "Pant", "label": "Dokumentnummer", "data_type": "string"},
    {"path": "pant.dokumentdato", "category": "Pant", "label": "Dokumentdato", "data_type": "date"},
    {"path": "pant.innfridd", "category": "Pant", "label": "Innfridd belop", "data_type": "number"},
    {"path": "pant.restgjeld", "category": "Pant", "label": "Restgjeld", "data_type": "number"},
    
    # ----- BUD OG BUDGIVERE -----
    {"path": "bud.budsum", "category": "Bud", "label": "Budsum", "data_type": "number"},
    {"path": "bud.budgiver", "category": "Bud", "label": "Budgivers navn", "data_type": "string"},
    {"path": "bud.buddato", "category": "Bud", "label": "Dato for bud", "data_type": "date"},
    {"path": "bud.budtid", "category": "Bud", "label": "Tidspunkt for bud", "data_type": "string"},
    {"path": "bud.akseptfrist", "category": "Bud", "label": "Akseptfrist", "data_type": "datetime"},
    {"path": "bud.finansiering", "category": "Bud", "label": "Finansiering", "data_type": "string"},
    {"path": "bud.forbehold", "category": "Bud", "label": "Forbehold", "data_type": "string"},
    
    # ----- BUDGIVERE (iterable) -----
    {"path": "budgivere", "category": "Budgivere", "label": "Liste over budgivere", "data_type": "array", "is_iterable": True, "parent_model": "Model"},
    
    # ----- VISNINGER (iterable) -----
    {"path": "visninger", "category": "Visninger", "label": "Liste over visninger", "data_type": "array", "is_iterable": True, "parent_model": "Model"},
    {"path": "visning.dato", "category": "Visning", "label": "Visningsdato", "data_type": "date"},
    {"path": "visning.tidspunkt", "category": "Visning", "label": "Tidspunkt (fra-til)", "data_type": "string"},
    {"path": "visning.startklokken", "category": "Visning", "label": "Starttid", "data_type": "string"},
    {"path": "visning.sluttklokken", "category": "Visning", "label": "Sluttid", "data_type": "string"},
    {"path": "visning.type", "category": "Visning", "label": "Visningstype", "data_type": "string"},
    {"path": "visning.ansvarlig", "category": "Visning", "label": "Visningsansvarlig", "data_type": "string"},
    
    # ----- POSTERINGER (iterable) -----
    {"path": "posteringer", "category": "Posteringer", "label": "Liste over posteringer", "data_type": "array", "is_iterable": True, "parent_model": "Model"},
    {"path": "postering.tekst", "category": "Postering", "label": "Posteringstekst", "data_type": "string"},
    {"path": "postering.belop", "category": "Postering", "label": "Belop", "data_type": "number"},
    {"path": "postering.mva", "category": "Postering", "label": "MVA", "data_type": "number"},
    {"path": "postering.kode", "category": "Postering", "label": "Posteringskode", "data_type": "string"},
    {"path": "postering.dato", "category": "Postering", "label": "Dato", "data_type": "date"},
    
    # ----- PROSJEKT -----
    {"path": "prosjekt.navn", "category": "Prosjekt", "label": "Prosjektnavn", "data_type": "string"},
    {"path": "prosjekt.byggetrinn", "category": "Prosjekt", "label": "Byggetrinn", "data_type": "string"},
    {"path": "prosjekt.utbygger", "category": "Prosjekt", "label": "Utbygger", "data_type": "string"},
    {"path": "prosjekt.adresse", "category": "Prosjekt", "label": "Prosjektadresse", "data_type": "string"},
    {"path": "prosjekt.ferdigstillelse", "category": "Prosjekt", "label": "Estimert ferdigstillelse", "data_type": "date"},
    
    # ----- TVANGSSALG -----
    {"path": "saksoker.navn", "category": "Tvangssalg", "label": "Saksokers navn", "data_type": "string"},
    {"path": "saksoker.adresse", "category": "Tvangssalg", "label": "Saksokers adresse", "data_type": "string"},
    {"path": "saksokt.navn", "category": "Tvangssalg", "label": "Saksoktes navn", "data_type": "string"},
    {"path": "saksokt.adresse", "category": "Tvangssalg", "label": "Saksoktes adresse", "data_type": "string"},
    {"path": "tvangssalg.saksnr", "category": "Tvangssalg", "label": "Saksnummer", "data_type": "string"},
    {"path": "tvangssalg.tingrett", "category": "Tvangssalg", "label": "Tingrett", "data_type": "string"},
    {"path": "tvangssalg.bostyrer", "category": "Tvangssalg", "label": "Bostyrer", "data_type": "string"},
    
    # ----- DATOER OG SIDETALL -----
    {"path": "dagsdato", "category": "System", "label": "Dagens dato", "data_type": "date"},
    {"path": "dato", "category": "System", "label": "Dato", "data_type": "date"},
    {"path": "p", "category": "Sidetall", "label": "Gjeldende sidetall", "data_type": "number"},
    {"path": "P", "category": "Sidetall", "label": "Totalt antall sider", "data_type": "number"},
]


async def seed_merge_fields_local():
    """Seed merge fields to local database."""
    from sqlalchemy.ext.asyncio import AsyncSession
    from app.database import async_session_factory
    from app.services.merge_field_service import MergeFieldService
    
    print("Seeding merge fields to local database...")
    
    async with async_session_factory() as db:
        created = 0
        skipped = 0
        
        for field_data in MERGE_FIELDS:
            try:
                await MergeFieldService.create(db, **field_data)
                created += 1
                print(f"  [OK] Created: {field_data['path']}")
            except ValueError as e:
                if "already exists" in str(e).lower():
                    skipped += 1
                    print(f"  [--] Exists: {field_data['path']}")
                else:
                    print(f"  [ERROR] {field_data['path']}: {e}")
            except Exception as e:
                print(f"  [ERROR] {field_data['path']}: {e}")
        
        await db.commit()
        print(f"\nDone! Created {created}, Skipped {skipped}")


def seed_merge_fields_remote(api_url: str):
    """Seed merge fields to remote API."""
    endpoint = f"{api_url.rstrip('/')}/api/merge-fields"
    print(f"Seeding merge fields to {endpoint}...")
    
    created = 0
    skipped = 0
    errors = 0
    
    for field_data in MERGE_FIELDS:
        try:
            response = requests.post(endpoint, json=field_data, timeout=30)
            if response.status_code == 201:
                created += 1
                print(f"  [OK] Created: {field_data['path']}")
            elif response.status_code == 400 and "exists" in response.text.lower():
                skipped += 1
                print(f"  [--] Exists: {field_data['path']}")
            else:
                errors += 1
                print(f"  [ERROR] {field_data['path']}: {response.status_code} - {response.text[:100]}")
        except Exception as e:
            errors += 1
            print(f"  [ERROR] {field_data['path']}: {e}")
    
    print(f"\nDone! Created {created}, Skipped {skipped}, Errors {errors}")


def main():
    parser = argparse.ArgumentParser(description='Seed Vitec merge fields to database')
    parser.add_argument('--api-url', help='Remote API URL (if not provided, uses local database)')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be seeded')
    
    args = parser.parse_args()
    
    if args.dry_run:
        print(f"Would seed {len(MERGE_FIELDS)} merge fields:")
        categories = {}
        for f in MERGE_FIELDS:
            cat = f['category']
            categories[cat] = categories.get(cat, 0) + 1
        for cat, count in sorted(categories.items()):
            print(f"  {cat}: {count} fields")
        return
    
    if args.api_url:
        seed_merge_fields_remote(args.api_url)
    else:
        asyncio.run(seed_merge_fields_local())


if __name__ == "__main__":
    main()
