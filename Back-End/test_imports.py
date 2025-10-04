#!/usr/bin/env python3

print("Testing imports...")

try:
    from app.modules.patients.routes import router as patients_router
    print("✓ Patient router imported successfully")
    print(f"  Router type: {type(patients_router)}")
    print(f"  Router routes: {len(patients_router.routes)} routes")
    for route in patients_router.routes:
        print(f"    - {route.methods} {route.path}")
except Exception as e:
    print(f"✗ Error importing patient router: {e}")

try:
    from app.api.v1.router import api_router
    print("✓ API router imported successfully")
    print(f"  API Router type: {type(api_router)}")
    print(f"  API Router routes: {len(api_router.routes)} routes")
    for route in api_router.routes:
        print(f"    - {route.methods} {route.path}")
except Exception as e:
    print(f"✗ Error importing API router: {e}")

try:
    from app.main import app
    print("✓ Main app imported successfully")
    print(f"  App type: {type(app)}")
    print(f"  App routes: {len(app.routes)} routes")
    for route in app.routes:
        print(f"    - {route.path}")
except Exception as e:
    print(f"✗ Error importing main app: {e}")

print("Import test completed.")