from fastapi import Path, status


from src.stu_house_market.utils.nigeria_institutions import NIGERIA_INSTITUTION
from src.stu_house_market.core.exc import InstitutionNotRecognizedException


INSTITUTIONS = frozenset(institution.strip().lower()for institution in NIGERIA_INSTITUTION)


def validate_institution(institution: str = Path(..., max_length=3)):
    return _validate_institution(institution)

def _validate_institution(institution: str) -> str:
    normalized = institution.strip().lower()
    if normalized not in INSTITUTIONS:
        raise InstitutionNotRecognizedException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The institution is not among recognized Nigerian institutions")

    return normalized
