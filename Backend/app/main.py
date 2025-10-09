from fastapi import FastAPI
from app.api.vm_controller import router as vm_router
from app.api.logs_controller import router as logs_router
from app.api.abstract_factory_controller import router as abstract_factory_router

app = FastAPI(
    title="VM Abstract Factory API", 
    version="2.0.0",
    description="API que implementa el patrón Abstract Factory para gestión completa de infraestructura cloud"
)

# Rutas principales - Abstract Factory Pattern
app.include_router(abstract_factory_router, prefix="/cloud", tags=["abstract-factory"])

# Rutas de VM (ahora usando Abstract Factory internamente)
app.include_router(vm_router, prefix="/vm", tags=["virtual-machines"])
app.include_router(logs_router, prefix="/api", tags=["logs"])

@app.get("/health")
def health():
    return {"status": "ok", "version": "2.0.0", "pattern": "Abstract Factory"}