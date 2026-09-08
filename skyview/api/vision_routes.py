"""
Snapdragon® AI Hub & Vision Routes
Optimized for Snapdragon-Powered HP PCs

Endpoints:
  POST /api/vision/crop-disease      — Analyze crop image using Qualcomm AI Hub vision model on Hexagon NPU
  GET  /api/vision/models            — List Qualcomm AI Hub models deployed on device
  GET  /api/vision/npu-telemetry     — Hexagon NPU performance, TOPS, and power metrics
"""

from datetime import datetime
from typing import Any, Dict, Optional
from fastapi import APIRouter, File, UploadFile, Form, Query
from pydantic import BaseModel

from skyview.agents.snapdragon_ai_hub import get_ai_hub_runner
from skyview.utils.logger import get_logger

router = APIRouter(prefix="/api/vision", tags=["Qualcomm AI Hub — Snapdragon Vision"])
logger = get_logger(__name__)


class VisionInferenceRequest(BaseModel):
    image_url: Optional[str] = None
    sample_name: Optional[str] = "tomato_early_blight_sample.jpg"
    include_telemetry_fusion: bool = True
    temperature: Optional[float] = 28.5
    humidity: Optional[float] = 82.0
    soil_moisture: Optional[float] = 45.0
    fpga_rain_prob: Optional[float] = 65.0


@router.get("/models")
async def list_ai_hub_models():
    """Returns Qualcomm AI Hub models available on this Snapdragon HP PC."""
    runner = get_ai_hub_runner()
    return {
        "device": "Snapdragon-powered HP PC (Snapdragon X Elite)",
        "npu_accelerator": "Qualcomm Hexagon NPU (45 TOPS)",
        "models": [
            {
                "id": "mobilenet_v4_crop_disease_qnn",
                "name": "MobileNetV4 — Agricultural Leaf Disease & Pest Classifier",
                "framework": "Qualcomm AI Hub (QNN ONNX Runtime)",
                "target_silicon": "Qualcomm Hexagon NPU",
                "quantization": "INT8 / W8A8",
                "latency_ms": 4.8,
                "top1_accuracy": "96.2%"
            },
            {
                "id": "llama_3.2_1b_snapdragon_npu",
                "name": "Llama 3.2-1B Multilingual Farm Advisor",
                "framework": "Qualcomm AI Engine Direct / QNN",
                "target_silicon": "Qualcomm Hexagon NPU + Adreno GPU",
                "quantization": "INT4 AWQ",
                "tokens_per_sec": 26.4
            },
            {
                "id": "whisper_base_ai_hub",
                "name": "Whisper Multilingual Speech-to-Text",
                "framework": "Qualcomm AI Hub",
                "target_silicon": "Qualcomm Hexagon NPU",
                "latency_per_sec_audio_ms": 68.0
            }
        ]
    }


@router.get("/npu-telemetry")
async def npu_telemetry():
    """Real-time performance and telemetry of the Snapdragon Hexagon NPU."""
    runner = get_ai_hub_runner()
    return runner.get_hardware_status()


@router.post("/crop-disease")
async def analyze_crop_disease(
    file: Optional[UploadFile] = File(None),
    sample_name: Optional[str] = Form("tomato_early_blight.jpg"),
    temperature: Optional[float] = Form(28.0),
    humidity: Optional[float] = Form(78.0),
    soil_moisture: Optional[float] = Form(38.0),
    fpga_rain_prob: Optional[float] = Form(65.0)
):
    """
    Submits a crop leaf or pest image for classification on the
    Qualcomm Hexagon NPU using a Qualcomm AI Hub optimized model.
    Fuses inference with live field telemetry.
    """
    runner = get_ai_hub_runner()

    image_bytes = None
    name = sample_name
    if file:
        image_bytes = await file.read()
        name = file.filename

    telemetry_ctx = {
        "temperature": temperature,
        "humidity": humidity,
        "soil_moisture": soil_moisture,
        "fpga_rain_prob": fpga_rain_prob
    }

    result = runner.predict_crop_disease(
        image_bytes=image_bytes,
        image_name=name,
        telemetry_context=telemetry_ctx
    )
    return result
