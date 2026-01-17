"""
Seed script for Vitec categories with vitec_id.

Populates the categories table with 97 Vitec Next document categories.

Run with: python -m scripts.seed_vitec_categories
"""

import asyncio
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.dialects.postgresql import insert as pg_insert
from app.database import async_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

# Vitec Next category definitions
# Format: (vitec_id, name, icon, description)
VITEC_CATEGORIES = [
    # Standard categories from Vitec Next
    (0, "Annet", "FileQuestion", "Andre dokumenter"),
    (1, "Akseptbrev", "FileCheck", "Akseptbrev til kjøper"),
    (2, "Akseptbrev selger", "FileCheck2", "Akseptbrev til selger"),
    (3, "AML", "Shield", "Anti-hvitvasking dokumenter"),
    (4, "Anbud", "FileText", "Anbudsdokumenter"),
    (5, "Avtaler", "FileSignature", "Avtaler og kontrakter"),
    (10, "Befaring", "Eye", "Befaringsrapporter"),
    (11, "Bud", "Gavel", "Budskjema og budrunde"),
    (12, "Budjournal", "ClipboardList", "Budjournal og budlogg"),
    (15, "Dokumenter fra kjøper", "UserCheck", "Dokumenter mottatt fra kjøper"),
    (16, "Dokumenter fra selger", "User", "Dokumenter mottatt fra selger"),
    (17, "Dokumenter fra megler", "Briefcase", "Dokumenter fra megler"),
    (20, "Egenerklæring", "ClipboardCheck", "Egenerklæringsskjema"),
    (21, "Eiendomsinformasjon", "Home", "Eiendomsinfo og prospekt"),
    (22, "E-post", "Mail", "E-postkorrespondanse"),
    (25, "Finansiering", "CreditCard", "Finansieringsdokumenter"),
    (26, "Forsikring", "ShieldCheck", "Forsikringsdokumenter"),
    (30, "Fullmakt", "FileKey", "Fullmakter"),
    (31, "Garanti", "Award", "Garantidokumenter"),
    (35, "Grunnbok", "Book", "Grunnboksutskrift"),
    (36, "Grunnboksutskrift", "BookOpen", "Grunnboksutskrift detalj"),
    (40, "HMS", "HardHat", "HMS-dokumentasjon"),
    (41, "Hovedbok", "BookMarked", "Hovedbokdokumenter"),
    (45, "Innkalling", "Calendar", "Innkallinger til møter"),
    (46, "Interessenter", "Users", "Interessentlister"),
    (50, "Kjøpekontrakt", "FileContract", "Kjøpekontrakter"),
    (51, "Kontrakt", "FileContract2", "Generelle kontrakter"),
    (52, "Kontraktsmøte", "UserSquare", "Kontraktsmøtedokumenter"),
    (55, "Korrespondanse", "MessageSquare", "Generell korrespondanse"),
    (56, "Kvittering", "Receipt", "Kvitteringer"),
    (60, "Legitimasjon", "IdCard", "Legitimasjonsdokumenter"),
    (61, "Lån", "Landmark", "Lånedokumenter"),
    (65, "Markedsføring", "Megaphone", "Markedsføringsmateriell"),
    (66, "Markedsplan", "Target", "Markedsføringsplan"),
    (70, "Megleroppgjør", "Calculator", "Megleroppgjørsdokumenter"),
    (71, "Megleroppdrag", "ClipboardSignature", "Oppdragsavtaler"),
    (75, "Næringsoppgjør", "Building", "Næringsoppgjør"),
    (76, "Notar", "Stamp", "Notardokumenter"),
    (80, "Oppdragsavtale", "FileEdit", "Oppdragsavtaler"),
    (81, "Oppgjør", "DollarSign", "Oppgjørsdokumenter"),
    (82, "Oppgjørsavtale", "FileSignature2", "Oppgjørsavtaler"),
    (85, "Oversikt", "LayoutList", "Oversiktsdokumenter"),
    (86, "Overtagelse", "Key", "Overtagelsesdokumenter"),
    (87, "Overtagelsesprotokoll", "ClipboardList2", "Overtagelsesprotokoller"),
    (90, "Pantedokumenter", "Lock", "Pantedokumenter og sikring"),
    (91, "Prospekt", "FileImage", "Salgsprospekt"),
    (95, "Rapporter", "BarChart", "Diverse rapporter"),
    (96, "Referat", "FileText2", "Møtereferat"),
    (100, "Salgsoppgave", "FileBadge", "Salgsoppgave"),
    (101, "Servitutter", "ScrollText", "Servituttdokumenter"),
    (105, "Sikring", "Shield2", "Sikringsobligasjoner"),
    (106, "Sikringsoblat", "ShieldOff", "Sikringsoblat"),
    (110, "Skjøte", "FileKey2", "Skjøte og hjemmelsdokumenter"),
    (111, "Sletting", "Trash", "Slettingsdokumenter"),
    (115, "SMS", "MessageCircle", "SMS-maler"),
    (116, "Søknad", "FileQuestion2", "Søknader"),
    (120, "Takst", "Scale", "Takstdokumenter"),
    (121, "Takstrapport", "FileScale", "Takstrapporter"),
    (125, "Tilbud", "Tag", "Tilbudsdokumenter"),
    (126, "Tilstandsrapport", "FileSearch", "Tilstandsrapporter"),
    (130, "Tinglysing", "Building2", "Tinglysingsdokumenter"),
    (131, "Tinglysingspakke", "Package", "Tinglysingspakker"),
    (135, "Utlegg", "Receipt2", "Utleggsdokumenter"),
    (136, "Utleggskvittering", "ReceiptText", "Utleggskvitteringer"),
    (140, "Varsel", "AlertCircle", "Varselbrev"),
    (141, "Vedtak", "Gavel2", "Vedtaksdokumenter"),
    (145, "Vedtekter", "Scroll", "Vedtekter og regler"),
    (146, "Visning", "Eye2", "Visningsdokumenter"),
    (150, "Økonomi", "Coins", "Økonomidokumenter"),
    (151, "Årsregnskap", "FileSpreadsheet", "Årsregnskap og rapporter"),
    # Additional categories for specialized use
    (155, "Boligkjøperforsikring", "HomeShield", "Boligkjøperforsikring"),
    (156, "Boligsalgsrapport", "HomeCheck", "Boligsalgsrapporter"),
    (160, "Felleskostnader", "Users2", "Felleskostnadsinformasjon"),
    (161, "Forretningsfører", "Briefcase2", "Forretningsførerdokumenter"),
    (165, "Kommunale avgifter", "Building3", "Kommunale avgifter og gebyrer"),
    (166, "Sameie", "Building4", "Sameiepapirer"),
    (170, "Styredokumenter", "Users3", "Styredokumenter og protokoller"),
]


async def seed_vitec_categories():
    """Seed Vitec categories using upsert."""
    from app.models.category import Category
    
    async_session = sessionmaker(
        async_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        count = 0
        for vitec_id, name, icon, description in VITEC_CATEGORIES:
            # Use PostgreSQL INSERT ... ON CONFLICT for upsert
            stmt = pg_insert(Category).values(
                name=name,
                vitec_id=vitec_id,
                icon=icon,
                description=description,
                sort_order=vitec_id,
            ).on_conflict_do_update(
                index_elements=["name"],
                set_={
                    "vitec_id": vitec_id,
                    "icon": icon,
                    "description": description,
                    "sort_order": vitec_id,
                }
            )
            await session.execute(stmt)
            count += 1
        
        await session.commit()
        print(f"Seeded {count} Vitec categories")


if __name__ == "__main__":
    asyncio.run(seed_vitec_categories())
