from app.main import app

for route in app.routes:
    # Look for APIRoute objects
    if hasattr(route, "path"):
        print(f"Path: {route.path} | Name: {getattr(route, 'name', 'N/A')} | Methods: {getattr(route, 'methods', 'N/A')}")
