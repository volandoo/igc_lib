from fastapi import FastAPI, HTTPException, Header, Depends, Request
from fastapi.responses import JSONResponse
import igc_lib
import tempfile
import shutil
import os
import igc_lib_json
import requests

app = FastAPI()
SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY environment variable must be set.")

def get_secret_key(x_secret_key: str = Header(None)):
    if x_secret_key != SECRET_KEY:
        raise HTTPException(status_code=401, detail={"success": False, "message": "Invalid or missing secret key"})

@app.post("/thermal_data")
async def thermal_data(
    request: Request,
    _: None = Depends(get_secret_key)
):
    try:
        body = await request.json()
        url = body.get("url")
        if not url:
            return JSONResponse(status_code=400, content={"success": False, "message": "Missing 'url' in request body"})
        # Download the file
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return JSONResponse(status_code=400, content={"success": False, "message": f"Failed to download file: {response.status_code}"})
        # Save to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".igc") as tmp:
            tmp.write(response.content)
            tmp_path = tmp.name
        # Parse the file
        try:
            flight = igc_lib.Flight.create_from_file(tmp_path)
            if not flight.valid:
                return JSONResponse(status_code=400, content={"success": False, "message": str(flight.notes)})
            thermals_data = []
            for thermal in flight.thermals:
                thermals_data.append({
                    "duration": thermal.time_change(),
                    "alt_change": thermal.alt_change(),
                    "vertical_velocity": thermal.vertical_velocity(),
                    "direction": thermal.direction,
                    "started": thermal.enter_fix.timestamp,
                    "time_per_circle": thermal.time_per_circle,
                    "enter": {"lat":thermal.enter_fix.lat, "lon":thermal.enter_fix.lon, "alt": thermal.enter_fix.alt},
                    "exit": {"lat":thermal.exit_fix.lat, "lon":thermal.exit_fix.lon,"alt":thermal.exit_fix.alt}
                })
            glides_data = []
            for glide in flight.glides:
                glides_data.append({
                    "duration": glide.time_change(),
                    "alt_change": glide.alt_change(),
                    "glide_ratio": glide.glide_ratio(),
                    "speed": glide.speed(),
                    "started": glide.enter_fix.timestamp,
                    "enter": {"lat":glide.enter_fix.lat, "lon":glide.enter_fix.lon, "alt": glide.enter_fix.alt},
                    "exit": {"lat":glide.exit_fix.lat, "lon":glide.exit_fix.lon,"alt":glide.exit_fix.alt}
                    })
            flight_data = {
                "thermals": thermals_data,
                "glides": glides_data
            }
        except Exception as e:
            return JSONResponse(status_code=500, content={"success": False, "message": str(e)})
        finally:
            os.remove(tmp_path)
        return {"success": True, "data": flight_data}
    except Exception as e:
        return JSONResponse(status_code=400, content={"success": False, "message": str(e)})