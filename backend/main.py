from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import httpx
import boto3
import os

app = FastAPI(title="lvstack API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

MINISTACK_HOST = os.environ.get("MINISTACK_HOST", "localhost")
FLOCI_HOST = os.environ.get("FLOCI_HOST", "localhost")
ROBOTOCORE_HOST = os.environ.get("ROBOTOCORE_HOST", "localhost")

STACKS = [
    {"id": "ministack", "name": "MiniStack", "host": MINISTACK_HOST, "port": 4566, "health_path": "/_ministack/health"},
    {"id": "floci", "name": "Floci", "host": FLOCI_HOST, "port": 4566, "health_path": "/_localstack/health"},
    {"id": "robotocore", "name": "RobotoCore", "host": ROBOTOCORE_HOST, "port": 4566, "health_path": "/_robotocore/health"},
]


def _get_s3_client(stack):
    return boto3.client(
        "s3",
        endpoint_url=f"http://{stack['host']}:{stack['port']}",
        aws_access_key_id="test",
        aws_secret_access_key="test",
        region_name="us-east-1",
    )


async def _fetch_health(stack):
    url = f"http://{stack['host']}:{stack['port']}{stack['health_path']}"
    try:
        async with httpx.AsyncClient(timeout=3) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                return resp.json()
    except Exception:
        pass
    return None


@app.get("/api/stacks")
async def get_stacks():
    """Returns status of all stacks."""
    results = []
    for stack in STACKS:
        health = await _fetch_health(stack)
        results.append({
            "id": stack["id"],
            "name": stack["name"],
            "port": stack["port"],
            "online": health is not None,
            "version": health.get("version", "") if health else "",
            "edition": health.get("edition", "") if health else "",
            "serviceCount": len(health.get("services", {})) if health else 0,
        })
    return results


@app.get("/api/stacks/{stack_id}/services")
async def get_stack_services(stack_id: str):
    """Returns services for a specific stack."""
    stack = next((s for s in STACKS if s["id"] == stack_id), None)
    if not stack:
        return {"error": "Stack not found"}
    health = await _fetch_health(stack)
    if not health:
        return {"error": "Stack offline", "services": {}}
    return {
        "id": stack["id"],
        "name": stack["name"],
        "version": health.get("version", ""),
        "edition": health.get("edition", ""),
        "services": health.get("services", {}),
    }


@app.get("/api/stacks/{stack_id}/s3/buckets")
async def get_s3_buckets(stack_id: str):
    """List S3 buckets in a stack."""
    stack = next((s for s in STACKS if s["id"] == stack_id), None)
    if not stack:
        return {"error": "Stack not found"}
    try:
        s3 = _get_s3_client(stack)
        resp = s3.list_buckets()
        buckets = [{"name": b["Name"], "created": b["CreationDate"].isoformat()} for b in resp.get("Buckets", [])]
        return {"buckets": buckets}
    except Exception as e:
        return {"error": str(e), "buckets": []}
