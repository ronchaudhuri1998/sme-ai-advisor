"""
Live Cloud Pricing Module
=========================
Fetches real-time pricing data from:
  - AWS Price List Bulk API  (no auth)
  - Azure Retail Prices API  (no auth)
  - GCP Cloud Billing Catalog API (API key, free)
  - GPU Cloud providers: Vast.ai & RunPod (API keys)
  - LLM API token pricing (curated static table)

All functions return standardised dicts and handle failures gracefully
by falling back to cached/default pricing so the app never breaks.
"""

import json
import requests
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════
# STATIC / FALLBACK PRICING DATA  (updated March 2026)
# Used when live APIs are unreachable or keys not provided
# ═══════════════════════════════════════════════════════════════════════

FALLBACK_LLM_PRICING = {
    "anthropic": {
        "claude-sonnet-4.6":  {"input_per_mtok": 3.00,  "output_per_mtok": 15.00, "context_window": "1M"},
        "claude-haiku-4.5":   {"input_per_mtok": 1.00,  "output_per_mtok": 5.00,  "context_window": "200K"},
        "claude-opus-4.6":    {"input_per_mtok": 5.00,  "output_per_mtok": 25.00, "context_window": "1M"},
    },
    "openai": {
        "gpt-4.1":            {"input_per_mtok": 2.00,  "output_per_mtok": 8.00,  "context_window": "1M"},
        "gpt-4.1-mini":       {"input_per_mtok": 0.40,  "output_per_mtok": 1.60,  "context_window": "1M"},
        "gpt-4.1-nano":       {"input_per_mtok": 0.10,  "output_per_mtok": 0.40,  "context_window": "1M"},
    },
    "google": {
        "gemini-2.5-pro":     {"input_per_mtok": 1.25,  "output_per_mtok": 10.00, "context_window": "1M"},
        "gemini-2.5-flash":   {"input_per_mtok": 0.15,  "output_per_mtok": 0.60,  "context_window": "1M"},
    },
}

FALLBACK_GPU_PRICING = {
    "nvidia_rtx_4090":  {"hourly_low": 0.29, "hourly_high": 0.74,  "vram_gb": 24,  "source": "Vast.ai / RunPod"},
    "nvidia_a100_80gb": {"hourly_low": 1.39, "hourly_high": 2.49,  "vram_gb": 80,  "source": "Lambda / RunPod"},
    "nvidia_h100_sxm":  {"hourly_low": 2.49, "hourly_high": 3.99,  "vram_gb": 80,  "source": "RunPod / Lambda"},
    "nvidia_a10g":      {"hourly_low": 0.60, "hourly_high": 1.10,  "vram_gb": 24,  "source": "AWS / RunPod"},
}

FALLBACK_CLOUD_COMPUTE = {
    "aws": {
        "g5.xlarge":    {"hourly": 1.006,  "vcpu": 4,  "ram_gb": 16,  "gpu": "A10G",    "region": "us-east-1"},
        "g5.2xlarge":   {"hourly": 1.212,  "vcpu": 8,  "ram_gb": 32,  "gpu": "A10G",    "region": "us-east-1"},
        "p4d.24xlarge": {"hourly": 32.77,  "vcpu": 96, "ram_gb": 1152,"gpu": "8xA100",  "region": "us-east-1"},
        "t3.medium":    {"hourly": 0.0416, "vcpu": 2,  "ram_gb": 4,   "gpu": "None",    "region": "us-east-1"},
    },
    "azure": {
        "Standard_NC4as_T4_v3":   {"hourly": 0.526,  "vcpu": 4,  "ram_gb": 28, "gpu": "T4",     "region": "eastus"},
        "Standard_NC24ads_A100_v4":{"hourly": 3.673, "vcpu": 24, "ram_gb": 220,"gpu": "A100",   "region": "eastus"},
        "Standard_B2s":           {"hourly": 0.0416, "vcpu": 2,  "ram_gb": 4,  "gpu": "None",   "region": "eastus"},
    },
    "gcp": {
        "g2-standard-4":  {"hourly": 0.7672, "vcpu": 4,  "ram_gb": 16, "gpu": "L4",      "region": "us-central1"},
        "a2-highgpu-1g":  {"hourly": 3.6732, "vcpu": 12, "ram_gb": 85, "gpu": "A100",    "region": "us-central1"},
        "e2-medium":      {"hourly": 0.0335, "vcpu": 2,  "ram_gb": 4,  "gpu": "None",    "region": "us-central1"},
    },
}

FALLBACK_CLOUD_SERVICES = {
    "aws": {
        "bedrock_claude_sonnet": {"input_per_mtok": 3.00, "output_per_mtok": 15.00, "service": "Amazon Bedrock"},
        "sagemaker_ml_g5_xlarge": {"hourly": 1.006, "service": "SageMaker Inference"},
        "s3_standard_gb":  {"monthly_per_gb": 0.023, "service": "S3 Standard"},
    },
    "azure": {
        "openai_gpt4_turbo": {"input_per_mtok": 10.00, "output_per_mtok": 30.00, "service": "Azure OpenAI"},
        "blob_hot_gb":       {"monthly_per_gb": 0.018, "service": "Blob Storage Hot"},
    },
    "gcp": {
        "vertex_gemini_pro": {"input_per_mtok": 1.25, "output_per_mtok": 10.00, "service": "Vertex AI"},
        "gcs_standard_gb":   {"monthly_per_gb": 0.020, "service": "Cloud Storage Standard"},
    },
}


# ═══════════════════════════════════════════════════════════════════════
# AWS PRICE LIST BULK API  (no auth required)
# ═══════════════════════════════════════════════════════════════════════

def fetch_aws_pricing(service_code: str = "AmazonEC2",
                      region: str = "us-east-1",
                      timeout: int = 30) -> Optional[dict]:
    """
    Fetch pricing from AWS Price List Bulk API (public, no auth).
    Returns raw JSON offer data or None on failure.
    
    Endpoint: https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/{service}/current/{region}/index.json
    WARNING: EC2 index can be >1GB. For the prototype we fetch the smaller
    region-specific file and parse selectively.
    """
    url = (f"https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/"
           f"{service_code}/current/{region}/index.json")
    try:
        # Stream and read only first chunk for large files
        resp = requests.get(url, timeout=timeout, stream=True)
        resp.raise_for_status()
        # For very large files (EC2), we limit what we parse
        content_length = int(resp.headers.get("content-length", 0))
        if content_length > 50_000_000:  # >50MB, too large for prototype
            logger.warning(f"AWS {service_code} file too large ({content_length/1e6:.0f}MB), using fallback")
            return None
        data = resp.json()
        return data
    except Exception as e:
        logger.warning(f"AWS pricing fetch failed for {service_code}: {e}")
        return None


def get_aws_bedrock_pricing(timeout: int = 15) -> dict:
    """Fetch Amazon Bedrock pricing (smaller file, manageable size)."""
    data = fetch_aws_pricing("AmazonBedrock", "us-east-1", timeout)
    if not data:
        return FALLBACK_CLOUD_SERVICES["aws"]
    
    try:
        results = {}
        products = data.get("products", {})
        terms = data.get("terms", {}).get("OnDemand", {})
        for sku, product in products.items():
            attrs = product.get("attributes", {})
            desc = attrs.get("usagetype", "")
            if sku in terms:
                price_dims = terms[sku]
                for _, term_data in price_dims.items():
                    for _, dim in term_data.get("priceDimensions", {}).items():
                        price = float(dim.get("pricePerUnit", {}).get("USD", "0"))
                        if price > 0:
                            results[desc] = price
        return results if results else FALLBACK_CLOUD_SERVICES["aws"]
    except Exception as e:
        logger.warning(f"AWS Bedrock parse error: {e}")
        return FALLBACK_CLOUD_SERVICES["aws"]


# ═══════════════════════════════════════════════════════════════════════
# AZURE RETAIL PRICES API  (no auth required)
# ═══════════════════════════════════════════════════════════════════════

def fetch_azure_pricing(service_name: str = "Virtual Machines",
                        region: str = "eastus",
                        max_results: int = 50,
                        timeout: int = 15) -> list:
    """
    Fetch pricing from Azure Retail Prices API (public, no auth).
    Endpoint: https://prices.azure.com/api/retail/prices
    """
    url = "https://prices.azure.com/api/retail/prices"
    params = {
        "api-version": "2023-01-01-preview",
        "$filter": (f"serviceName eq '{service_name}' "
                    f"and armRegionName eq '{region}' "
                    f"and priceType eq 'Consumption'"),
        "$top": max_results,
    }
    try:
        resp = requests.get(url, params=params, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
        return data.get("Items", [])
    except Exception as e:
        logger.warning(f"Azure pricing fetch failed for {service_name}: {e}")
        return []


def get_azure_vm_pricing(region: str = "eastus") -> dict:
    """Get Azure VM pricing for common GPU and general instances."""
    items = fetch_azure_pricing("Virtual Machines", region, max_results=100)
    if not items:
        return FALLBACK_CLOUD_COMPUTE["azure"]
    
    results = {}
    target_skus = ["Standard_NC4as_T4_v3", "Standard_NC24ads_A100_v4", "Standard_B2s",
                   "Standard_NC6s_v3", "Standard_NV6ads_A10_v5"]
    for item in items:
        sku = item.get("armSkuName", "")
        if sku in target_skus and item.get("unitPrice", 0) > 0:
            results[sku] = {
                "hourly": item["unitPrice"],
                "meter": item.get("meterName", ""),
                "sku": sku,
                "region": region,
            }
    return results if results else FALLBACK_CLOUD_COMPUTE["azure"]


def get_azure_ai_pricing(region: str = "eastus") -> dict:
    """Get Azure OpenAI / AI services pricing."""
    items = fetch_azure_pricing("Azure OpenAI", region, max_results=50)
    results = {}
    for item in items:
        if item.get("unitPrice", 0) > 0:
            results[item.get("meterName", "unknown")] = {
                "price": item["unitPrice"],
                "unit": item.get("unitOfMeasure", ""),
                "product": item.get("productName", ""),
            }
    return results if results else FALLBACK_CLOUD_SERVICES["azure"]


# ═══════════════════════════════════════════════════════════════════════
# GCP CLOUD BILLING CATALOG API  (requires API key)
# ═══════════════════════════════════════════════════════════════════════

def fetch_gcp_pricing(service_id: str, gcp_api_key: str,
                      timeout: int = 15) -> list:
    """
    Fetch SKU pricing from GCP Cloud Billing Catalog API.
    Endpoint: https://cloudbilling.googleapis.com/v1/services/{id}/skus
    Requires a GCP API key (free to create).
    """
    if not gcp_api_key:
        return []
    url = f"https://cloudbilling.googleapis.com/v1/services/{service_id}/skus"
    params = {"key": gcp_api_key}
    try:
        resp = requests.get(url, params=params, timeout=timeout)
        resp.raise_for_status()
        return resp.json().get("skus", [])
    except Exception as e:
        logger.warning(f"GCP pricing fetch failed for service {service_id}: {e}")
        return []


def get_gcp_compute_pricing(gcp_api_key: str = "") -> dict:
    """Get GCP Compute Engine pricing. Service ID for Compute Engine: 6F81-5844-456A"""
    skus = fetch_gcp_pricing("6F81-5844-456A", gcp_api_key)
    if not skus:
        return FALLBACK_CLOUD_COMPUTE["gcp"]
    
    results = {}
    for sku in skus[:200]:  # limit parsing
        desc = sku.get("description", "")
        pricing_info = sku.get("pricingInfo", [])
        if pricing_info:
            tiers = pricing_info[0].get("pricingExpression", {}).get("tieredRates", [])
            if tiers:
                nanos = tiers[0].get("unitPrice", {}).get("nanos", 0)
                units = int(tiers[0].get("unitPrice", {}).get("units", "0") or "0")
                price = units + nanos / 1e9
                if price > 0:
                    results[desc[:80]] = {"price": round(price, 6), "unit": "hour"}
    return results if results else FALLBACK_CLOUD_COMPUTE["gcp"]


# ═══════════════════════════════════════════════════════════════════════
# GPU CLOUD PROVIDERS  (Vast.ai & RunPod)
# ═══════════════════════════════════════════════════════════════════════

def fetch_vastai_pricing(api_key: str = "", timeout: int = 15) -> list:
    """
    Fetch GPU offers from Vast.ai REST API.
    Endpoint: https://console.vast.ai/api/v0/bundles/
    """
    if not api_key:
        return []
    url = "https://console.vast.ai/api/v0/bundles/"
    headers = {"Accept": "application/json"}
    params = {"api_key": api_key, "limit": 50}
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=timeout)
        resp.raise_for_status()
        return resp.json().get("offers", [])
    except Exception as e:
        logger.warning(f"Vast.ai pricing fetch failed: {e}")
        return []


def fetch_runpod_pricing(api_key: str = "", timeout: int = 15) -> dict:
    """
    Fetch GPU pricing from RunPod GraphQL API.
    Endpoint: https://api.runpod.io/graphql
    """
    if not api_key:
        return {}
    url = "https://api.runpod.io/graphql"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    query = """
    query {
        gpuTypes {
            id
            displayName
            memoryInGb
            securePrice
            communityPrice
        }
    }
    """
    try:
        resp = requests.post(url, headers=headers, json={"query": query}, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
        return data.get("data", {}).get("gpuTypes", [])
    except Exception as e:
        logger.warning(f"RunPod pricing fetch failed: {e}")
        return {}


def get_gpu_cloud_pricing(vastai_key: str = "", runpod_key: str = "") -> dict:
    """Aggregate GPU pricing from Vast.ai and RunPod, with fallback."""
    results = {}

    # Try Vast.ai
    vastai_offers = fetch_vastai_pricing(vastai_key)
    if vastai_offers:
        for offer in vastai_offers[:30]:
            gpu = offer.get("gpu_name", "unknown")
            price = offer.get("dph_total", 0)
            vram = offer.get("gpu_ram", 0)
            if gpu not in results or price < results[gpu].get("hourly_low", 999):
                results[gpu] = {
                    "hourly_low": round(price, 3),
                    "hourly_high": round(price * 1.3, 3),
                    "vram_gb": round(vram / 1024) if vram > 100 else vram,
                    "source": "Vast.ai",
                }

    # Try RunPod
    runpod_gpus = fetch_runpod_pricing(runpod_key)
    if runpod_gpus:
        for gpu in runpod_gpus:
            name = gpu.get("displayName", "unknown")
            secure = gpu.get("securePrice", 0)
            community = gpu.get("communityPrice", 0)
            vram = gpu.get("memoryInGb", 0)
            if secure and secure > 0:
                results[f"{name} (RunPod)"] = {
                    "hourly_low": round(community, 3) if community else round(secure * 0.7, 3),
                    "hourly_high": round(secure, 3),
                    "vram_gb": vram,
                    "source": "RunPod",
                }

    return results if results else FALLBACK_GPU_PRICING


# ═══════════════════════════════════════════════════════════════════════
# LLM API PRICING  (static lookup, updated periodically)
# ═══════════════════════════════════════════════════════════════════════

def get_llm_pricing() -> dict:
    """Return current LLM API token pricing across providers."""
    return FALLBACK_LLM_PRICING


# ═══════════════════════════════════════════════════════════════════════
# MASTER FUNCTION — collects everything into one dict
# ═══════════════════════════════════════════════════════════════════════

def collect_all_pricing(gcp_api_key: str = "",
                        vastai_key: str = "",
                        runpod_key: str = "") -> dict:
    """
    Fetch pricing from all available sources.
    Returns a single dict with all pricing data + metadata.
    Falls back gracefully for any source that fails.
    """
    pricing = {
        "fetched_at": datetime.now().isoformat(),
        "sources_live": [],
        "sources_fallback": [],
    }

    # --- AWS ---
    aws_bedrock = get_aws_bedrock_pricing()
    if aws_bedrock != FALLBACK_CLOUD_SERVICES["aws"]:
        pricing["sources_live"].append("AWS Price List API")
    else:
        pricing["sources_fallback"].append("AWS (cached)")
    pricing["aws_services"] = FALLBACK_CLOUD_SERVICES["aws"]
    pricing["aws_compute"] = FALLBACK_CLOUD_COMPUTE["aws"]

    # --- Azure ---
    azure_vms = get_azure_vm_pricing()
    azure_ai = get_azure_ai_pricing()
    if azure_vms != FALLBACK_CLOUD_COMPUTE["azure"]:
        pricing["sources_live"].append("Azure Retail Prices API")
        pricing["azure_compute"] = azure_vms
    else:
        pricing["sources_fallback"].append("Azure (cached)")
        pricing["azure_compute"] = FALLBACK_CLOUD_COMPUTE["azure"]
    pricing["azure_services"] = FALLBACK_CLOUD_SERVICES["azure"]

    # --- GCP ---
    gcp_compute = get_gcp_compute_pricing(gcp_api_key)
    if gcp_compute != FALLBACK_CLOUD_COMPUTE["gcp"]:
        pricing["sources_live"].append("GCP Billing Catalog API")
        pricing["gcp_compute"] = gcp_compute
    else:
        pricing["sources_fallback"].append("GCP (cached)")
        pricing["gcp_compute"] = FALLBACK_CLOUD_COMPUTE["gcp"]
    pricing["gcp_services"] = FALLBACK_CLOUD_SERVICES["gcp"]

    # --- GPU Cloud ---
    gpu_pricing = get_gpu_cloud_pricing(vastai_key, runpod_key)
    if gpu_pricing != FALLBACK_GPU_PRICING:
        pricing["sources_live"].append("GPU Cloud (Vast.ai/RunPod)")
    else:
        pricing["sources_fallback"].append("GPU Cloud (cached)")
    pricing["gpu_cloud"] = gpu_pricing

    # --- LLM APIs ---
    pricing["llm_apis"] = get_llm_pricing()
    pricing["sources_fallback"].append("LLM API pricing (curated)")

    return pricing


def format_pricing_for_prompt(pricing: dict) -> str:
    """
    Format collected pricing data as a concise text block
    to inject into the Claude prompt for grounded cost estimates.
    """
    lines = []
    lines.append("=== LIVE CLOUD PRICING DATA (use these for cost estimates) ===")
    lines.append(f"Fetched: {pricing.get('fetched_at', 'unknown')}")
    lines.append(f"Live sources: {', '.join(pricing.get('sources_live', ['none']))}")
    lines.append(f"Fallback sources: {', '.join(pricing.get('sources_fallback', []))}")
    lines.append("")

    # LLM pricing
    lines.append("--- LLM API Token Pricing (per million tokens, USD) ---")
    for provider, models in pricing.get("llm_apis", {}).items():
        for model, info in models.items():
            lines.append(f"  {provider}/{model}: ${info['input_per_mtok']} input, "
                         f"${info['output_per_mtok']} output")
    lines.append("")

    # Cloud compute
    lines.append("--- Cloud Compute (hourly USD) ---")
    for provider in ["aws", "azure", "gcp"]:
        key = f"{provider}_compute"
        if key in pricing:
            lines.append(f"  [{provider.upper()}]")
            compute = pricing[key]
            for name, info in list(compute.items())[:5]:
                if isinstance(info, dict) and "hourly" in info:
                    gpu_str = info.get("gpu", "")
                    lines.append(f"    {name}: ${info['hourly']:.4f}/hr "
                                 f"({info.get('vcpu', '?')} vCPU, {info.get('ram_gb', '?')}GB RAM"
                                 f"{', GPU: ' + gpu_str if gpu_str and gpu_str != 'None' else ''})")
    lines.append("")

    # Cloud AI services
    lines.append("--- Cloud AI Services ---")
    for provider in ["aws", "azure", "gcp"]:
        key = f"{provider}_services"
        if key in pricing:
            lines.append(f"  [{provider.upper()}]")
            for name, info in pricing[key].items():
                if "input_per_mtok" in info:
                    lines.append(f"    {info.get('service', name)}: "
                                 f"${info['input_per_mtok']} input, "
                                 f"${info['output_per_mtok']} output /MTok")
                elif "monthly_per_gb" in info:
                    lines.append(f"    {info.get('service', name)}: "
                                 f"${info['monthly_per_gb']}/GB/month")
                elif "hourly" in info:
                    lines.append(f"    {info.get('service', name)}: "
                                 f"${info['hourly']}/hr")
    lines.append("")

    # GPU cloud
    lines.append("--- GPU Cloud (self-hosted AI, hourly USD) ---")
    for gpu, info in pricing.get("gpu_cloud", {}).items():
        lines.append(f"  {gpu}: ${info['hourly_low']:.2f}-${info['hourly_high']:.2f}/hr "
                     f"({info['vram_gb']}GB VRAM) [{info['source']}]")

    return "\n".join(lines)
