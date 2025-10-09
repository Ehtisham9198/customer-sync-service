from fastapi import APIRouter

router = APIRouter()


@router.get("/{name}")
def get_name(name:str):
    return name


