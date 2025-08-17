import json
from schema_generator import SchemaGenerator

def test_complex_schema():
    """Test the schema generator with complex data including binary content"""
    print("Testing schema generator with complex NDJSON data:")
    print("=" * 60)
    
    # Create schema generator
    generator = SchemaGenerator()
    
    # Read the complex test data
    with open('test_complex_data.ndjson', 'r', encoding='utf-8') as f:
        ndjson_content = f.read()
    
    print(f"Loaded {len(ndjson_content.splitlines())} lines of NDJSON data")
    print()
    
    # Generate schema
    print("Generating schema...")
    schema = generator.analyze_ndjson(ndjson_content)
    
    # Print the schema in a readable format
    print("\nGenerated Schema:")
    print("-" * 30)
    print(json.dumps(schema, indent=2))
    
    # Check for binary classifications
    print("\n" + "=" * 60)
    print("Checking for binary classifications:")
    print("-" * 30)
    
    def check_for_binary(schema_obj, path=""):
        """Recursively check for binary classifications in the schema"""
        if isinstance(schema_obj, dict):
            for key, value in schema_obj.items():
                current_path = f"{path}.{key}" if path else key
                if key == "contentEncoding" and value == "base64":
                    print(f"✅ Binary detected at: {path}")
                elif isinstance(value, dict):
                    check_for_binary(value, current_path)
                elif isinstance(value, list):
                    for i, item in enumerate(value):
                        if isinstance(item, dict):
                            check_for_binary(item, f"{current_path}[{i}]")
    
    check_for_binary(schema)
    
    # Validate the schema against the original data
    print("\n" + "=" * 60)
    print("Validating schema against original data:")
    print("-" * 30)
    
    try:
        # Parse the NDJSON data
        objects = generator.parse_ndjson(ndjson_content)
        
        # Validate each object against the schema
        import jsonschema
        from jsonschema import validate
        
        validation_errors = []
        for i, obj in enumerate(objects, 1):
            try:
                validate(instance=obj, schema=schema)
            except jsonschema.exceptions.ValidationError as e:
                validation_errors.append(f"Object {i}: {e}")
        
        if validation_errors:
            print("❌ Validation errors found:")
            for error in validation_errors:
                print(f"  {error}")
        else:
            print(f"✅ Schema validation successful for all {len(objects)} objects!")
            
    except ImportError:
        print("⚠️  jsonschema not available, skipping validation")
    except Exception as e:
        print(f"❌ Validation failed: {e}")
    
    # Show some statistics
    print("\n" + "=" * 60)
    print("Schema Statistics:")
    print("-" * 30)
    
    properties = schema.get("properties", {})
    required_fields = schema.get("required", [])
    
    print(f"Total properties: {len(properties)}")
    print(f"Required fields: {len(required_fields)}")
    print(f"Optional fields: {len(properties) - len(required_fields)}")
    
    # Count different types
    type_counts = {}
    binary_count = 0
    
    def count_types(schema_obj):
        nonlocal binary_count
        if isinstance(schema_obj, dict):
            if "contentEncoding" in schema_obj and schema_obj["contentEncoding"] == "base64":
                binary_count += 1
            if "type" in schema_obj:
                type_name = schema_obj["type"]
                type_counts[type_name] = type_counts.get(type_name, 0) + 1
            if "oneOf" in schema_obj:
                type_counts["mixed"] = type_counts.get("mixed", 0) + 1
            for value in schema_obj.values():
                if isinstance(value, (dict, list)):
                    count_types(value)
        elif isinstance(schema_obj, list):
            for item in schema_obj:
                count_types(item)
    
    count_types(properties)
    
    print(f"Binary fields: {binary_count}")
    print("Type distribution:")
    for type_name, count in type_counts.items():
        print(f"  {type_name}: {count}")

if __name__ == "__main__":
    test_complex_schema()
