# AutoSchema

An intelligent rule-based JSON schema generator that analyzes NDJSON data and automatically creates comprehensive schemas that support any type of content, including binary data. **No external LLM required** - uses intelligent pattern analysis and rule-based algorithms.

## 🚀 Features

- 🧠 **Intelligent Pattern Analysis**: Uses advanced pattern recognition to analyze NDJSON data
- 📋 **6 Schema Types**: Standard, Flexible, Binary-Aware, Flexible with Types, Pydantic Any, and Hardened Binary
- 🔓 **Flexible Content Support**: Handles fields that can contain anything, including binary data and mixed types
- 🌐 **REST API**: FastAPI-based web service for easy integration
- 🛡️ **Error Handling**: Robust error handling and validation
- 📊 **NDJSON Support**: Works with Newline Delimited JSON format for streaming and large datasets
- 🔐 **Binary Detection**: Automatically detects and properly handles binary data (base64, hex patterns)
- 📁 **File Upload**: Support for uploading NDJSON files via API
- 🎯 **Type Preservation**: Maintains type information while allowing flexibility

## 📋 Schema Types

| Schema Type | Description | Use Case |
|-------------|-------------|----------|
| **Smart Hardened** | **Intelligent nested binary detection, mixed types, strict validation** | **Main route for complex data** |
| **Standard** | Balanced validation with specific types | Production APIs |
| **Flexible** | Maximum flexibility - allows ANY type for ANY field | Prototyping |
| **Binary-Aware** | Smart binary detection and handling | Binary-heavy data |
| **Flexible with Types** | Flexible but preserves detected type information | Type-aware flexibility |
| **Pydantic Any** | Uses `Any` type for binary/mixed fields (like Pydantic) | Pydantic compatibility |
| **Hardened Binary** | Ultra-strict binary validation with patterns and examples | Security-critical |

## 🛠️ Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd AutoSchema
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the example**
   ```bash
   python example.py
   ```

## 🚀 Usage

### Command Line Usage

```bash
# Generate all 6 schema types from NDJSON data
python example.py
```

This will:
- ✅ Generate 6 types of JSON schemas from NDJSON data
- ✅ Save them to files: `generated_schema.json`, `flexible_schema.json`, `binary_aware_schema.json`, etc.
- ✅ Show detailed output with pattern detection

### Python Code Example

```python
from schema_generator import SchemaGenerator

# Initialize the schema generator
generator = SchemaGenerator()

# Sample NDJSON data
ndjson_content = """{"id": 1, "name": "John Doe", "email": "john@example.com", "age": 30, "is_active": true, "binary_data": "SGVsbG8gV29ybGQ="}
{"id": 2, "name": "Jane Smith", "email": "jane@example.com", "age": 25, "is_active": false, "binary_data": null}"""

# Generate different types of schemas
objects = generator.parse_ndjson(ndjson_content)

# Standard schema
standard_schema = generator.analyze_ndjson(ndjson_content)

# Flexible schema with type preservation
flexible_with_types = generator.generate_flexible_with_types_schema(objects)

# Pydantic Any type schema
pydantic_any = generator.generate_pydantic_model_with_any(objects)

# Hardened binary schema
hardened_binary = generator.generate_hardened_binary_schema(objects)

print("Schemas generated successfully!")
```

### API Server

Start the API server:
```bash
python api.py
```

The server will be available at:
- **API Documentation**: http://localhost:8000/docs
- **API Root**: http://localhost:8000/

## 🌐 API Endpoints

### JSON List Endpoints
- `POST /generate-schema` - Generate standard JSON schema from JSON list

### Main Route (Recommended)
- `POST /api/v1/schemas/smart` - **Main route for complex data** (Smart Hardened Schema)
- `POST /ndjson/generate-smart` - Alternative smart schema endpoint

### NDJSON Content Endpoints
- `POST /ndjson/generate-schema` - Generate standard JSON schema from NDJSON
- `POST /ndjson/generate-flexible` - Generate flexible JSON schema from NDJSON
- `POST /ndjson/generate-binary-aware` - Generate binary-aware JSON schema from NDJSON
- `POST /ndjson/generate-flexible-with-types` - Generate flexible with types JSON schema from NDJSON
- `POST /ndjson/generate-pydantic-any` - Generate Pydantic Any type JSON schema from NDJSON
- `POST /ndjson/generate-hardened-binary` - Generate hardened binary JSON schema from NDJSON

### File Upload Endpoints
- `POST /upload/generate-schema` - Generate standard JSON schema from uploaded NDJSON file
- `POST /upload/generate-flexible` - Generate flexible JSON schema from uploaded NDJSON file
- `POST /upload/generate-binary-aware` - Generate binary-aware JSON schema from uploaded NDJSON file
- `POST /upload/generate-flexible-with-types` - Generate flexible with types JSON schema from uploaded NDJSON file
- `POST /upload/generate-pydantic-any` - Generate Pydantic Any type JSON schema from uploaded NDJSON file
- `POST /upload/generate-hardened-binary` - Generate hardened binary JSON schema from uploaded NDJSON file

### API Usage Examples

#### Generate Schema from NDJSON Content
```bash
curl -X POST "http://localhost:8000/ndjson/generate-schema" \
     -H "Content-Type: application/json" \
     -d '{
       "ndjson_content": "{\"id\": 1, \"name\": \"John Doe\", \"email\": \"john@example.com\"}\n{\"id\": 2, \"name\": \"Jane Smith\", \"email\": \"jane@example.com\"}",
       "sample_size": null
     }'
```

#### Generate Flexible Schema
```bash
curl -X POST "http://localhost:8000/ndjson/generate-flexible" \
     -H "Content-Type: application/json" \
     -d '{
       "ndjson_content": "{\"id\": 1, \"binary_data\": \"SGVsbG8gV29ybGQ=\", \"mixed_content\": \"text\"}\n{\"id\": 2, \"binary_data\": null, \"mixed_content\": 42}",
       "sample_size": null
     }'
```

#### Upload NDJSON File
```bash
curl -X POST "http://localhost:8000/upload/generate-binary-aware" \
     -F "file=@your_data.ndjson"
```

## 📊 Generated Schema Examples

### Standard Schema
```json
{
  "$schema": "http://json-schema.org/draft-2020-12/schema#",
  "type": "object",
  "properties": {
    "id": {
      "type": "integer",
      "minimum": 1,
      "maximum": 5
    },
    "name": {
      "type": "string",
      "minLength": 8,
      "maxLength": 14
    },
    "email": {
      "type": "string",
      "format": "email"
    }
  },
  "required": ["id", "name", "email"]
}
```

### Binary-Aware Schema
```json
{
  "$schema": "http://json-schema.org/draft-2020-12/schema#",
  "type": "object",
  "properties": {
    "binary_data": {
      "type": "string",
      "contentEncoding": "base64",
      "contentMediaType": "application/octet-stream",
      "description": "Binary data for binary_data"
    },
    "mixed_content": {
      "oneOf": [
        {"type": "string", "description": "Text content"},
        {"type": "string", "contentEncoding": "base64", "description": "Binary content"},
        {"type": "object", "additionalProperties": true, "description": "Object content"}
      ]
    }
  }
}
```

### Hardened Binary Schema
```json
{
  "$schema": "http://json-schema.org/draft-2020-12/schema#",
  "type": "object",
  "properties": {
    "binary_data": {
      "type": "string",
      "contentEncoding": "base64",
      "contentMediaType": "application/octet-stream",
      "minLength": 1,
      "pattern": "^[A-Za-z0-9+/]*={0,2}$",
      "description": "Binary data for binary_data (base64 encoded)",
      "examples": ["SGVsbG8gV29ybGQ="]
    }
  },
  "additionalProperties": false
}
```

## 🔧 Configuration

The schema generator uses intelligent pattern analysis and doesn't require any configuration files or API keys. However, you can customize the behavior by modifying the `SchemaGenerator` class:

- **Binary Detection**: Modify `binary_patterns` in `__init__` method
- **Pattern Recognition**: Update pattern matching methods like `_is_email`, `_is_url`, etc.
- **Schema Generation**: Customize schema generation methods for different use cases

## 🧪 Testing

Run the test suite:
```bash
python test_schema_generator.py
```

The tests cover:
- ✅ Schema generation for different data types
- ✅ Binary data detection and handling
- ✅ Pattern recognition (email, URL, UUID, date/time)
- ✅ Error handling and validation
- ✅ API endpoint functionality

## 📁 Project Structure

```
AutoSchema/
├── schema_generator.py    # Core schema generation logic
├── api.py                # FastAPI web service
├── example.py            # Usage examples and demonstrations
├── test_schema_generator.py  # Unit tests
├── requirements.txt      # Python dependencies
├── README.md            # This file
└── generated_schemas/   # Output directory for generated schemas
```

## 🚀 Performance Tips

- **Large Datasets**: Use `sample_size` parameter to analyze a subset of large NDJSON files
- **Memory Efficiency**: Use `stream_ndjson()` method for very large files
- **Caching**: Cache generated schemas for repeated analysis of the same data structure
- **Validation**: Disable schema validation for faster processing if not needed

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Troubleshooting

### Common Issues

**Q: Schema validation fails with "None is not of type 'string'"**
A: This happens when fields can be null. The schema generator automatically handles this by using `oneOf` with `null` type.

**Q: Binary data not detected properly**
A: Check if your binary data follows base64 or hex patterns. You can customize the detection patterns in the `SchemaGenerator` class.

**Q: API server won't start**
A: Make sure you have all dependencies installed: `pip install -r requirements.txt`

**Q: Large files cause memory issues**
A: Use the `sample_size` parameter or the `stream_ndjson()` method for memory-efficient processing.

### Getting Help

- Check the API documentation at http://localhost:8000/docs when the server is running
- Review the example code in `example.py`
- Run the test suite to verify your installation
- Check the generated schema files for examples of different schema types

## 🎯 Use Cases

- **API Development**: Generate schemas for API request/response validation
- **Data Validation**: Validate NDJSON data streams in real-time
- **Documentation**: Auto-generate schema documentation for data structures
- **Testing**: Create test data that conforms to generated schemas
- **Data Migration**: Understand data structure changes over time
- **Binary Data Handling**: Properly handle file uploads and binary content in JSON
