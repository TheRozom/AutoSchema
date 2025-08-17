import json
from schema_generator import SchemaGenerator

def test_fixed_schema():
    """Test the fixed schema generator with flexible length constraints"""
    print("Testing fixed schema generator with flexible constraints:")
    print("=" * 60)
    
    # Create schema generator
    generator = SchemaGenerator()
    
    # Read the complex test data
    with open('test_complex_data.ndjson', 'r', encoding='utf-8') as f:
        ndjson_content = f.read()
    
    print(f"Loaded {len(ndjson_content.splitlines())} lines of NDJSON data")
    print()
    
    # Generate schema using the smart hardened method
    print("Generating smart hardened schema...")
    objects = generator.parse_ndjson(ndjson_content)
    schema = generator.generate_smart_hardened_schema(objects)
    
    # Print the schema in a readable format
    print("\nGenerated Smart Hardened Schema:")
    print("-" * 30)
    print(json.dumps(schema, indent=2))
    
    # Test with modified data that has different lengths
    print("\n" + "=" * 60)
    print("Testing with modified data (different lengths):")
    print("-" * 30)
    
    # Create test data with different lengths
    test_data = [
        {
            "id": 999,
            "name": "VeryLongNameThatExceedsOriginalLength",
            "email": "very.long.email.address@very.long.domain.com",
            "age": 99,
            "active": True,
            "binary_data": "VGhpcyBpcyBhIHZlcnkgbG9uZyBiaW5hcnkgZGF0YSBzdHJpbmcgdGhhdCBleGNlZWRzIHRoZSBvcmlnaW5hbCBsZW5ndGg=",
            "nested": {"username": "verylongusername", "preferences": {"theme": "dark", "notifications": True}},
            "tags": ["user", "premium", "very_long_tag"],
            "metadata": {"created_at": "2024-01-15T10:30:00Z", "last_login": "2024-01-20T14:22:15Z"}
        },
        {
            "id": 1,
            "name": "A",  # Very short name
            "email": "a@b.c",  # Very short email
            "age": 1,
            "active": False,
            "binary_data": "SGVsbG8=",  # Very short binary
            "nested": {"username": "a", "preferences": {"theme": "light", "notifications": False}},
            "tags": [],  # Empty array
            "metadata": {"created_at": "2024-01-01T00:00:00Z", "last_login": "2024-01-01T00:00:00Z"}
        }
    ]
    
    # Validate the test data against the generated schema
    try:
        import jsonschema
        from jsonschema import validate
        
        validation_errors = []
        for i, obj in enumerate(test_data, 1):
            try:
                validate(instance=obj, schema=schema)
                print(f"✅ Test object {i} validates successfully")
            except jsonschema.exceptions.ValidationError as e:
                validation_errors.append(f"Object {i}: {e}")
                print(f"❌ Test object {i} failed validation: {e}")
        
        if not validation_errors:
            print(f"\n🎉 All test objects validated successfully!")
            print("The schema is now flexible enough to handle varying data lengths.")
        else:
            print(f"\n❌ {len(validation_errors)} validation errors found:")
            for error in validation_errors:
                print(f"  {error}")
            
    except ImportError:
        print("⚠️  jsonschema not available, skipping validation")
    except Exception as e:
        print(f"❌ Validation failed: {e}")
    
    # Show schema statistics
    print("\n" + "=" * 60)
    print("Schema Statistics:")
    print("-" * 30)
    
    properties = schema.get("properties", {})
    required_fields = schema.get("required", [])
    
    print(f"Total properties: {len(properties)}")
    print(f"Required fields: {len(required_fields)}")
    print(f"Optional fields: {len(properties) - len(required_fields)}")
    
    # Count fields with length constraints
    length_constrained_fields = 0
    binary_fields = 0
    
    for field_name, field_schema in properties.items():
        if "minLength" in field_schema or "maxLength" in field_schema:
            length_constrained_fields += 1
        if "contentEncoding" in field_schema and field_schema["contentEncoding"] == "base64":
            binary_fields += 1
    
    print(f"Fields with length constraints: {length_constrained_fields}")
    print(f"Binary fields: {binary_fields}")
    
    # Show some examples of flexible constraints
    print("\nExamples of flexible constraints:")
    for field_name, field_schema in properties.items():
        if field_schema.get("type") == "string":
            min_len = field_schema.get("minLength", "not set")
            max_len = field_schema.get("maxLength", "not set")
            print(f"  {field_name}: minLength={min_len}, maxLength={max_len}")

if __name__ == "__main__":
    test_fixed_schema()
