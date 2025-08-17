import json
from schema_generator import SchemaGenerator

def show_complete_schema():
    """Show the complete generated schema"""
    print("Generating schema from complex NDJSON data...")
    
    # Create schema generator
    generator = SchemaGenerator()
    
    # Read the complex test data
    with open('test_complex_data.ndjson', 'r', encoding='utf-8') as f:
        ndjson_content = f.read()
    
    # Generate schema
    schema = generator.analyze_ndjson(ndjson_content)
    
    # Save schema to file for easy viewing
    with open('generated_schema.json', 'w') as f:
        json.dump(schema, f, indent=2)
    
    print("✅ Schema generated successfully!")
    print(f"📄 Complete schema saved to: generated_schema.json")
    
    # Show key statistics
    properties = schema.get("properties", {})
    required_fields = schema.get("required", [])
    
    print(f"\n📊 Schema Statistics:")
    print(f"   Total properties: {len(properties)}")
    print(f"   Required fields: {len(required_fields)}")
    print(f"   Optional fields: {len(properties) - len(required_fields)}")
    
    # Count binary fields
    binary_fields = []
    for field_name, field_schema in properties.items():
        if isinstance(field_schema, dict) and field_schema.get("contentEncoding") == "base64":
            binary_fields.append(field_name)
    
    print(f"   Binary fields: {len(binary_fields)}")
    if binary_fields:
        print(f"   Binary field names: {', '.join(binary_fields)}")
    
    # Show a few key properties
    print(f"\n🔍 Sample Properties:")
    sample_fields = list(properties.keys())[:5]
    for field in sample_fields:
        field_schema = properties[field]
        if isinstance(field_schema, dict):
            field_type = field_schema.get("type", "mixed")
            is_binary = field_schema.get("contentEncoding") == "base64"
            is_required = field in required_fields
            print(f"   {field}: {field_type}{' (binary)' if is_binary else ''}{' (required)' if is_required else ''}")

if __name__ == "__main__":
    show_complete_schema()
