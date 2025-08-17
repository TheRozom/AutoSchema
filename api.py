from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
import tempfile
from schema_generator import SchemaGenerator

app = FastAPI(
    title="AutoSchema",
    description="A rule-based service that generates JSON schemas from NDJSON data",
    version="1.0.0"
)

# Initialize schema generator (no API key needed)
schema_generator = SchemaGenerator()

class SchemaResponse(BaseModel):
    """Response model for schema generation."""
    schema: Dict[str, Any]

class AnalysisResponse(BaseModel):
    """Response model for object analysis."""
    analysis: Dict[str, Any]

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "AutoSchema - Rule-based JSON Schema Generator",
        "version": "1.0.0",
        "description": "Generate JSON schemas from NDJSON data without external LLM",
        "endpoints": {
            "Smart Schema Generation": "/api/v1/schemas/smart",
            "Object Analysis": "/api/v1/analyze"
        },
        "documentation": "/docs"
    }

@app.post("/api/v1/schemas/smart", response_model=SchemaResponse)
async def generate_smart_schema(
    file: UploadFile = File(...),
    max_nested_depth: Optional[int] = 100,
    sample_size: Optional[int] = None
):
    """
    Generate a smart, hardened JSON schema that intelligently handles nested binary data,
    mixed types, and complex structures while being strict when appropriate.
    
    This is the main route for complex data with:
    - Intelligent nested binary detection
    - Smart mixed type handling
    - Strict validation where appropriate
    - Flexibility for truly mixed content
    - Configurable max nested depth (default: 100)
    """
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.ndjson') as temp_file:
            content = await file.read()
            temp_file.write(content.decode('utf-8'))
            temp_file_path = temp_file.name
        
        # Parse and analyze
        objects = schema_generator.parse_ndjson_file(temp_file_path)
        
        if sample_size and len(objects) > sample_size:
            import random
            objects = random.sample(objects, sample_size)
        
        # Generate smart schema with custom max nested depth
        schema = schema_generator.generate_smart_hardened_schema_with_depth(objects, max_nested_depth)
        
        # Clean up
        os.unlink(temp_file_path)
        
        return SchemaResponse(schema=schema)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/v1/analyze", response_model=AnalysisResponse)
async def analyze_objects(
    file: UploadFile = File(...),
    max_nested_depth: Optional[int] = 100,
    sample_size: Optional[int] = None
):
    """
    Analyze NDJSON objects to understand their structure without generating a schema.
    
    Returns detailed analysis including:
    - Field types and patterns
    - Nested structure hierarchy
    - Binary data detection
    - Mixed type analysis
    - All possible paths in nested structures
    """
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.ndjson') as temp_file:
            content = await file.read()
            temp_file.write(content.decode('utf-8'))
            temp_file_path = temp_file.name
        
        # Parse objects
        objects = schema_generator.parse_ndjson_file(temp_file_path)
        
        if sample_size and len(objects) > sample_size:
            import random
            objects = random.sample(objects, sample_size)
        
        # Analyze objects with custom max nested depth
        analysis = schema_generator.analyze_objects_with_depth(objects, max_nested_depth)
        
        # Clean up
        os.unlink(temp_file_path)
        
        return AnalysisResponse(analysis=analysis)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)
