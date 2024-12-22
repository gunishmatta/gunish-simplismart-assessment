from fastapi import HTTPException
from sqlalchemy import Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship, validates

from app.db.base_class import Base


class Cluster(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    organization_id = Column(Integer, ForeignKey("organization.id"))
    
    # Resource limits
    cpu_limit = Column(Float)
    ram_limit = Column(Float)
    gpu_limit = Column(Float)
    
    # Available resources
    cpu_available = Column(Float)
    ram_available = Column(Float)
    gpu_available = Column(Float)
    
    # Relationships
    organization = relationship("Organization", back_populates="clusters")
    deployments = relationship("Deployment", back_populates="cluster")

    def __repr__(self):
        return f"<Cluster(name={self.name}, cpu_limit={self.cpu_limit}, ram_limit={self.ram_limit}, gpu_limit={self.gpu_limit})>"


    # Validation for cpu_available
    @validates("cpu_available")
    def validate_cpu_available(self, key, value):
        if value < 0:
            raise HTTPException(status_code=400, detail="CPU available cannot be negative.")
        if value > self.cpu_limit:
            raise HTTPException(status_code=400, detail="Requested CPU exceeds the resource limit.")
        return value

    # Validation for ram_available
    @validates("ram_available")
    def validate_ram_available(self, key, value):
        if value < 0:
            raise HTTPException(status_code=400, detail="RAM available cannot be negative.")
        if value > self.ram_limit:
            raise HTTPException(status_code=400, detail="Requested RAM exceeds the resource limit.")
        return value

    # Validation for gpu_available
    @validates("gpu_available")
    def validate_gpu_available(self, key, value):
        if value < 0:
            raise HTTPException(status_code=400, detail="GPU available cannot be negative.")
        if value > self.gpu_limit:
            raise HTTPException(status_code=400, detail="Requested GPU exceeds the resource limit.")
        return value