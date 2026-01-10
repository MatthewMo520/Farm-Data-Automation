"""
bioTrack+ Animal Schema Configuration
Based on Add-Animals.pdf documentation
"""
from typing import Dict, List, Optional
from enum import Enum


class AnimalCategory(str, Enum):
    """Animal category options"""
    NEWBORN = "Newborn Animal"
    MATURE = "Mature Animal"
    PURCHASE_LEASE = "Purchase/Lease"


class Species(str, Enum):
    """Animal species options"""
    BEEF_CATTLE = "Beef Cattle"
    SHEEP = "Sheep"
    GOAT = "Goat"
    BISON = "Bison"


class Sex(str, Enum):
    """Animal sex options"""
    BULL = "Bull"
    STEER = "Steer"
    COW = "Cow"
    HEIFER = "Heifer"
    RAM = "Ram"
    WETHER = "Wether"
    EWE = "Ewe"
    EWE_LAMB = "Ewe Lamb"


class BornAs(str, Enum):
    """Birth type options"""
    SINGLE = "Single"
    TWIN = "Twin"
    TRIPLET = "Triplet"
    EMBRYO_TRANSFER = "Embryo-Transfer"


class RaisedAs(str, Enum):
    """Rearing type options"""
    SINGLE = "Single"
    TWIN = "Twin"
    TRIPLET = "Triplet"
    FOSTER = "Foster"
    ORPHAN = "Orphan"
    BOTTLE_FED = "Bottle-Fed"


class BirthingEase(str, Enum):
    """Birthing ease classification"""
    UNASSISTED = "Unassisted"
    EASY_PULL = "Easy Pull"
    HARD_PULL = "Hard Pull"
    MALPRESENTATION = "Malpresentation"
    SURGICAL = "Surgical"


# bioTrack+ Animal Required Fields Configuration
BIOTRACK_REQUIRED_FIELDS = {
    # Always required fields (marked with * in bioTrack)
    "category": {
        "type": "string",
        "required": True,
        "description": "Animal category",
        "options": [e.value for e in AnimalCategory]
    },
    "species": {
        "type": "string",
        "required": True,
        "description": "Animal species",
        "options": [e.value for e in Species]
    },
    "birth_date": {
        "type": "date",
        "required": True,
        "description": "Animal's birth date (required, use best guess if unknown)"
    },
    "sex": {
        "type": "string",
        "required": True,
        "description": "Animal's sex",
        "options": [e.value for e in Sex]
    },
    "breed_composition": {
        "type": "object",
        "required": True,
        "description": "Breed composition (must sum to 100%)",
        "validation": "sum_to_100"
    },

    # Conditionally required fields
    "ear_tag": {
        "type": "string",
        "required": "conditional",
        "condition": "if Bio ID is primary ID type",
        "description": "Animal's ear tag (must be unique)",
        "unique": True
    },
    "rfid": {
        "type": "string",
        "required": "conditional",
        "condition": "if RFID is primary ID type",
        "description": "Animal's RFID (15-20 digit number)",
        "pattern": r"^\d{15,20}$"
    },
    "herd_letter": {
        "type": "string",
        "required": "conditional",
        "condition": "if Bio ID is primary ID type and not using one-time herd letter",
        "description": "Herd letter from account"
    },
    "one_time_herd_letter": {
        "type": "string",
        "required": "conditional",
        "condition": "if Bio ID is primary ID type and animal not in ownership",
        "description": "One-time herd letter for purchased animals"
    },
    "birth_season": {
        "type": "string",
        "required": "conditional",
        "condition": "for newborn animals",
        "description": "Birth season (e.g., 2022 or January 2022)"
    },
    "location": {
        "type": "string",
        "required": True,
        "description": "Current location of the animal"
    },

    # Optional but commonly used fields
    "registration_name": {
        "type": "string",
        "required": False,
        "description": "Registration name (must be unique if provided)",
        "unique": True
    },
    "registration_id": {
        "type": "string",
        "required": False,
        "description": "Registration ID (must be unique if provided)",
        "unique": True
    },
    "born_as": {
        "type": "string",
        "required": False,
        "description": "Birth type",
        "options": [e.value for e in BornAs]
    },
    "raised_as": {
        "type": "string",
        "required": False,
        "description": "Rearing type",
        "options": [e.value for e in RaisedAs]
    },
    "birthing_ease": {
        "type": "string",
        "required": False,
        "description": "Birth difficulty classification",
        "options": [e.value for e in BirthingEase]
    },
    "birth_weight": {
        "type": "float",
        "required": False,
        "description": "Weight at birth"
    },
    "birth_weight_uom": {
        "type": "string",
        "required": "conditional",
        "condition": "if birth_weight is provided",
        "description": "Unit of measure for birth weight",
        "options": ["kg", "lbs"]
    },
    "dam_id": {
        "type": "string",
        "required": False,
        "description": "ID of the animal's dam (mother)"
    },
    "sire_id": {
        "type": "string",
        "required": False,
        "description": "ID of the animal's sire (father)"
    },
    "colour": {
        "type": "string",
        "required": False,
        "description": "Animal's colour"
    },
    "animal_comments": {
        "type": "string",
        "required": False,
        "description": "General comments about the animal"
    }
}


# Detection keywords for bioTrack animal entity
BIOTRACK_DETECTION_KEYWORDS = [
    "animal", "cow", "cattle", "bull", "heifer", "steer",
    "sheep", "lamb", "ewe", "ram",
    "goat", "kid", "doe", "buck",
    "bison", "buffalo",
    "ear tag", "rfid", "tag number",
    "birth", "born", "calving", "lambing"
]


def get_missing_required_fields(extracted_data: Dict, category: str = None) -> List[str]:
    """
    Identify which required fields are missing from extracted data

    Args:
        extracted_data: Data extracted from transcription
        category: Animal category (if known)

    Returns:
        List of missing required field names
    """
    missing_fields = []

    for field_name, field_config in BIOTRACK_REQUIRED_FIELDS.items():
        # Check always required fields
        if field_config.get("required") is True:
            if field_name not in extracted_data or not extracted_data[field_name]:
                missing_fields.append(field_name)

        # Check conditionally required fields
        elif field_config.get("required") == "conditional":
            condition = field_config.get("condition", "")

            # Birth season required for newborn animals
            if "newborn" in condition.lower() and category == AnimalCategory.NEWBORN.value:
                if field_name not in extracted_data or not extracted_data[field_name]:
                    missing_fields.append(field_name)

            # Birth weight UoM required if birth weight provided
            if "birth_weight" in condition.lower() and "birth_weight" in extracted_data:
                if field_name not in extracted_data or not extracted_data[field_name]:
                    missing_fields.append(field_name)

    return missing_fields


def format_missing_fields_prompt(missing_fields: List[str]) -> str:
    """
    Create a user-friendly prompt for missing required fields

    Args:
        missing_fields: List of missing field names

    Returns:
        Formatted prompt string
    """
    if not missing_fields:
        return ""

    field_descriptions = []
    for field_name in missing_fields:
        field_config = BIOTRACK_REQUIRED_FIELDS.get(field_name, {})
        description = field_config.get("description", field_name)
        field_descriptions.append(f"- {description}")

    prompt = "The following required information is missing from your recording:\n\n"
    prompt += "\n".join(field_descriptions)
    prompt += "\n\nPlease provide these details."

    return prompt
