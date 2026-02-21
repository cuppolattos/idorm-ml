from pydantic import BaseModel, Field
from typing import Literal
from enum import Enum


class TipeKos(str, Enum):
    putra = "putra"
    putri = "putri"
    campur = "campur"


from typing import Literal, Optional

class KosRequest(BaseModel):
    luas_kamar: float = Field(..., gt=0, lt=100)
    jarak_ke_bca: Optional[float] = Field(0.0, ge=0, lt=50)

    tipe_kos: TipeKos

    is_km_dalam: Literal[0, 1]
    is_water_heater: Literal[0, 1]
    is_furnished: Literal[0, 1]
    is_listrik_free: Literal[0, 1]
    is_parkir_mobil: Literal[0, 1]
    is_mesin_cuci: Literal[0, 1]


class PredictionResponse(BaseModel):
    region: str
    predicted_price: float
    model_version: str
