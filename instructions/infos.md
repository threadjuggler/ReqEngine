# Against a running backend (docker compose up, or local uvicorn on port 8000):
uv --project backend run robot tests/

# Syntax/dryrun only (no live server needed):
uv --project backend run robot --dryrun tests/

# Point at a different host:
API_BASE_URL=http://my-host:8000/api uv --project backend run robot tests/

# Write results into a folder instead of the cwd:
uv --project backend run robot --outputdir tests/robot_results tests/