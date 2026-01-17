"""
Seed script for Vitec merge fields.

Populates the merge_fields table with common Vitec Next merge field definitions.

Run with: python -m scripts.seed_merge_fields
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

# Vitec merge field definitions
# Format: {path, category, label, description, example_value, data_type, is_iterable, parent_model}
VITEC_MERGE_FIELDS = [
    # ==========================================================================
    # Eiendom (Property)
    # ==========================================================================
    {
        "path": "eiendom.gatenavnognr",
        "category": "Eiendom",
        "label": "Adresse",
        "description": "Eiendommens gatenavn og husnummer",
        "example_value": "Storgata 1",
        "data_type": "string",
        "is_iterable": False,
        "parent_model": "Model.eiendom"
    },
    {
        "path": "eiendom.postnr",
        "category": "Eiendom",
        "label": "Postnummer",
        "description": "Eiendommens postnummer",
        "example_value": "0155",
        "data_type": "string",
        "is_iterable": False,
        "parent_model": "Model.eiendom"
    },
    {
        "path": "eiendom.poststed",
        "category": "Eiendom",
        "label": "Poststed",
        "description": "Eiendommens poststed",
        "example_value": "Oslo",
        "data_type": "string",
        "is_iterable": False,
        "parent_model": "Model.eiendom"
    },
    {
        "path": "eiendom.pris",
        "category": "Eiendom",
        "label": "Prisantydning",
        "description": "Eiendommens prisantydning",
        "example_value": "4 500 000",
        "data_type": "number",
        "is_iterable": False,
        "parent_model": "Model.eiendom"
    },
    {
        "path": "eiendom.eieform",
        "category": "Eiendom",
        "label": "Eieform",
        "description": "Type eierskap (Eiet, Aksje, Andel, etc.)",
        "example_value": "Eiet",
        "data_type": "string",
        "is_iterable": False,
        "parent_model": "Model.eiendom"
    },
    {
        "path": "eiendom.boligtype",
        "category": "Eiendom",
        "label": "Boligtype",
        "description": "Type bolig (Leilighet, Enebolig, etc.)",
        "example_value": "Leilighet",
        "data_type": "string",
        "is_iterable": False,
        "parent_model": "Model.eiendom"
    },
    {
        "path": "eiendom.bra",
        "category": "Eiendom",
        "label": "BRA",
        "description": "Bruksareal i kvadratmeter",
        "example_value": "85",
        "data_type": "number",
        "is_iterable": False,
        "parent_model": "Model.eiendom"
    },
    {
        "path": "eiendom.prom",
        "category": "Eiendom",
        "label": "P-ROM",
        "description": "Primærrom i kvadratmeter",
        "example_value": "78",
        "data_type": "number",
        "is_iterable": False,
        "parent_model": "Model.eiendom"
    },
    {
        "path": "komplettmatrikkelutvidet",
        "category": "Eiendom",
        "label": "Matrikkel",
        "description": "Komplett matrikkelnummer",
        "example_value": "Gnr 1 Bnr 23 Snr 4",
        "data_type": "string",
        "is_iterable": False,
        "parent_model": None
    },
    
    # ==========================================================================
    # Selger (Seller)
    # ==========================================================================
    {
        "path": "selger.navnutenfullmektigogkontaktperson",
        "category": "Selger",
        "label": "Navn (Full)",
        "description": "Selgers fulle navn uten fullmektig",
        "example_value": "Ola Nordmann",
        "data_type": "string",
        "is_iterable": True,
        "parent_model": "Model.selgere"
    },
    {
        "path": "selger.hovedgatenavnognr",
        "category": "Selger",
        "label": "Adresse",
        "description": "Selgers gateadresse",
        "example_value": "Parkveien 10",
        "data_type": "string",
        "is_iterable": True,
        "parent_model": "Model.selgere"
    },
    {
        "path": "selger.hovedpostnr",
        "category": "Selger",
        "label": "Postnummer",
        "description": "Selgers postnummer",
        "example_value": "0350",
        "data_type": "string",
        "is_iterable": True,
        "parent_model": "Model.selgere"
    },
    {
        "path": "selger.hovedpoststed",
        "category": "Selger",
        "label": "Poststed",
        "description": "Selgers poststed",
        "example_value": "Oslo",
        "data_type": "string",
        "is_iterable": True,
        "parent_model": "Model.selgere"
    },
    {
        "path": "selger.emailadresse",
        "category": "Selger",
        "label": "E-post",
        "description": "Selgers e-postadresse",
        "example_value": "ola@example.com",
        "data_type": "string",
        "is_iterable": True,
        "parent_model": "Model.selgere"
    },
    {
        "path": "selger.hovedtlf",
        "category": "Selger",
        "label": "Telefon",
        "description": "Selgers telefonnummer",
        "example_value": "912 34 567",
        "data_type": "string",
        "is_iterable": True,
        "parent_model": "Model.selgere"
    },
    {
        "path": "selger.idnummer",
        "category": "Selger",
        "label": "Fødselsnummer",
        "description": "Selgers fødselsnummer/org.nr",
        "example_value": "01018012345",
        "data_type": "string",
        "is_iterable": True,
        "parent_model": "Model.selgere"
    },
    
    # ==========================================================================
    # Kjøper (Buyer)
    # ==========================================================================
    {
        "path": "kjoper.navnutenfullmektigogkontaktperson",
        "category": "Kjøper",
        "label": "Navn (Full)",
        "description": "Kjøpers fulle navn",
        "example_value": "Kari Nordmann",
        "data_type": "string",
        "is_iterable": True,
        "parent_model": "Model.kjopere"
    },
    {
        "path": "kjoper.hovedgatenavnognr",
        "category": "Kjøper",
        "label": "Adresse",
        "description": "Kjøpers gateadresse",
        "example_value": "Strandveien 5",
        "data_type": "string",
        "is_iterable": True,
        "parent_model": "Model.kjopere"
    },
    {
        "path": "kjoper.hovedpostnr",
        "category": "Kjøper",
        "label": "Postnummer",
        "description": "Kjøpers postnummer",
        "example_value": "0252",
        "data_type": "string",
        "is_iterable": True,
        "parent_model": "Model.kjopere"
    },
    {
        "path": "kjoper.hovedpoststed",
        "category": "Kjøper",
        "label": "Poststed",
        "description": "Kjøpers poststed",
        "example_value": "Oslo",
        "data_type": "string",
        "is_iterable": True,
        "parent_model": "Model.kjopere"
    },
    {
        "path": "kjoper.emailadresse",
        "category": "Kjøper",
        "label": "E-post",
        "description": "Kjøpers e-postadresse",
        "example_value": "kari@example.com",
        "data_type": "string",
        "is_iterable": True,
        "parent_model": "Model.kjopere"
    },
    {
        "path": "kjoper.hovedtlf",
        "category": "Kjøper",
        "label": "Telefon",
        "description": "Kjøpers telefonnummer",
        "example_value": "987 65 432",
        "data_type": "string",
        "is_iterable": True,
        "parent_model": "Model.kjopere"
    },
    
    # ==========================================================================
    # Megler (Broker)
    # ==========================================================================
    {
        "path": "ansvarligmegler.navn",
        "category": "Megler",
        "label": "Ansvarlig megler",
        "description": "Ansvarlig meglers navn",
        "example_value": "Per Hansen",
        "data_type": "string",
        "is_iterable": False,
        "parent_model": "Model.ansvarligmegler"
    },
    {
        "path": "ansvarligmegler.tittel",
        "category": "Megler",
        "label": "Tittel",
        "description": "Meglers tittel",
        "example_value": "Eiendomsmegler MNEF",
        "data_type": "string",
        "is_iterable": False,
        "parent_model": "Model.ansvarligmegler"
    },
    {
        "path": "ansvarligmegler.epost",
        "category": "Megler",
        "label": "E-post",
        "description": "Meglers e-postadresse",
        "example_value": "per@meglerkontor.no",
        "data_type": "string",
        "is_iterable": False,
        "parent_model": "Model.ansvarligmegler"
    },
    {
        "path": "ansvarligmegler.telefon",
        "category": "Megler",
        "label": "Telefon",
        "description": "Meglers telefonnummer",
        "example_value": "22 33 44 55",
        "data_type": "string",
        "is_iterable": False,
        "parent_model": "Model.ansvarligmegler"
    },
    
    # ==========================================================================
    # Meglerkontor (Office)
    # ==========================================================================
    {
        "path": "meglerkontor.markedsforingsnavn",
        "category": "Megler",
        "label": "Kontor navn",
        "description": "Meglerkontorets markedsføringsnavn",
        "example_value": "Proaktiv Eiendomsmegling AS",
        "data_type": "string",
        "is_iterable": False,
        "parent_model": "Model.meglerkontor"
    },
    {
        "path": "meglerkontor.besoksadresse",
        "category": "Megler",
        "label": "Kontor adresse",
        "description": "Meglerkontorets besøksadresse",
        "example_value": "Stortingsgata 20, 0161 Oslo",
        "data_type": "string",
        "is_iterable": False,
        "parent_model": "Model.meglerkontor"
    },
    {
        "path": "meglerkontor.orgnr",
        "category": "Megler",
        "label": "Org.nr",
        "description": "Meglerkontorets organisasjonsnummer",
        "example_value": "912 345 678",
        "data_type": "string",
        "is_iterable": False,
        "parent_model": "Model.meglerkontor"
    },
    
    # ==========================================================================
    # Økonomi (Economy)
    # ==========================================================================
    {
        "path": "oppdrag.provisjonprosent",
        "category": "Økonomi",
        "label": "Provisjon %",
        "description": "Provisjonssats i prosent",
        "example_value": "2.5",
        "data_type": "number",
        "is_iterable": False,
        "parent_model": "Model.oppdrag"
    },
    {
        "path": "oppdrag.selgersamletsum",
        "category": "Økonomi",
        "label": "Samlet sum",
        "description": "Selgers samlede kostnader",
        "example_value": "125 000",
        "data_type": "number",
        "is_iterable": False,
        "parent_model": "Model.oppdrag"
    },
    {
        "path": "oppdrag.selgerutleggsum",
        "category": "Økonomi",
        "label": "Utlegg sum",
        "description": "Sum utlegg for selger",
        "example_value": "25 000",
        "data_type": "number",
        "is_iterable": False,
        "parent_model": "Model.oppdrag"
    },
    {
        "path": "oppdrag.salgssum",
        "category": "Økonomi",
        "label": "Salgssum",
        "description": "Endelig salgssum",
        "example_value": "4 750 000",
        "data_type": "number",
        "is_iterable": False,
        "parent_model": "Model.oppdrag"
    },
    
    # ==========================================================================
    # Oppgjør (Settlement)
    # ==========================================================================
    {
        "path": "oppgjor.kontornavn",
        "category": "Oppgjør",
        "label": "Oppgjør kontor",
        "description": "Oppgjørskontorets navn",
        "example_value": "Proaktiv Oppgjør AS",
        "data_type": "string",
        "is_iterable": False,
        "parent_model": "Model.oppgjor"
    },
    {
        "path": "oppdrag.overtagelse",
        "category": "Oppgjør",
        "label": "Overtagelse",
        "description": "Dato for overtagelse",
        "example_value": "01.03.2026",
        "data_type": "date",
        "is_iterable": False,
        "parent_model": "Model.oppdrag"
    },
    {
        "path": "oppdrag.kontraktsdato",
        "category": "Oppgjør",
        "label": "Kontraktsdato",
        "description": "Dato for kontraktsinngåelse",
        "example_value": "15.01.2026",
        "data_type": "date",
        "is_iterable": False,
        "parent_model": "Model.oppdrag"
    },
    
    # ==========================================================================
    # Dato (Dates)
    # ==========================================================================
    {
        "path": "dato.idag",
        "category": "Dato",
        "label": "Dagens dato",
        "description": "Dagens dato formatert",
        "example_value": "17. januar 2026",
        "data_type": "date",
        "is_iterable": False,
        "parent_model": None
    },
    
    # ==========================================================================
    # Samlinger (Collections)
    # ==========================================================================
    {
        "path": "Model.selgere",
        "category": "Samlinger",
        "label": "Selgere",
        "description": "Liste over alle selgere",
        "example_value": "[{navn: 'Ola'}, {navn: 'Kari'}]",
        "data_type": "array",
        "is_iterable": True,
        "parent_model": "Model"
    },
    {
        "path": "Model.kjopere",
        "category": "Samlinger",
        "label": "Kjøpere",
        "description": "Liste over alle kjøpere",
        "example_value": "[{navn: 'Per'}]",
        "data_type": "array",
        "is_iterable": True,
        "parent_model": "Model"
    },
    {
        "path": "Model.meglere",
        "category": "Samlinger",
        "label": "Meglere",
        "description": "Liste over alle involverte meglere",
        "example_value": "[{navn: 'Per Hansen'}]",
        "data_type": "array",
        "is_iterable": True,
        "parent_model": "Model"
    },
]


async def seed_merge_fields():
    """Seed merge fields using upsert."""
    from app.models.merge_field import MergeField
    
    async_session = sessionmaker(
        async_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        count = 0
        for field_data in VITEC_MERGE_FIELDS:
            # Use PostgreSQL INSERT ... ON CONFLICT for upsert
            stmt = pg_insert(MergeField).values(
                path=field_data["path"],
                category=field_data["category"],
                label=field_data["label"],
                description=field_data.get("description"),
                example_value=field_data.get("example_value"),
                data_type=field_data.get("data_type", "string"),
                is_iterable=field_data.get("is_iterable", False),
                parent_model=field_data.get("parent_model")
            ).on_conflict_do_update(
                index_elements=["path"],
                set_={
                    "category": field_data["category"],
                    "label": field_data["label"],
                    "description": field_data.get("description"),
                    "example_value": field_data.get("example_value"),
                    "data_type": field_data.get("data_type", "string"),
                    "is_iterable": field_data.get("is_iterable", False),
                    "parent_model": field_data.get("parent_model")
                }
            )
            await session.execute(stmt)
            count += 1
        
        await session.commit()
        print(f"Seeded {count} merge fields")


if __name__ == "__main__":
    asyncio.run(seed_merge_fields())
