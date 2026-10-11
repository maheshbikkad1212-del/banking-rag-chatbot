import uvicorn
import os
import sys

# Ensure UTF-8 output encoding for Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# Ensure backend root is in sys.path
sys.path.insert(0, os.path.dirname(__file__))

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🚀 Banking Smart Document RAG Backend Server Running!")
    print("👉 API Base URL:         http://127.0.0.1:8000")
    print("👉 Interactive API Docs: http://127.0.0.1:8000/docs")
    print("👉 Web UI (Frontend):    http://localhost:3000  (run 'npm run dev' in frontend/)")
    print("="*70 + "\n")
    
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)

