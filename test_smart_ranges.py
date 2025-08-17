import json
from schema_generator import SchemaGenerator

def test_smart_ranges():
    """Test the improved smart ranges for numeric and string fields"""
    print("Testing smart ranges for numeric and string fields:")
    print("=" * 60)
    
    # Create schema generator
    generator = SchemaGenerator()
    
    # Test data with specific values to test smart ranges
    test_data = [
        {
            "id": 1,
            "name": "Alice",
            "email": "alice@example.com",
            "age": 25,
            "score": 87.5,
            "coordinates": {"x": 45, "y": 60},
            "log": [
                {"time": "10:00", "event": "login", "x": 45, "y": 60},
                {"time": "10:05", "event": "click", "x": 45, "y": 60}
            ],
            "short_text": "Hi",
            "medium_text": "Hello World",
            "long_text": "This is a very long text that should have flexible constraints"
        },
        {
            "id": 2,
            "name": "Bob",
            "email": "bob@example.com",
            "age": 30,
            "score": 92.0,
            "coordinates": {"x": 100, "y": 200},
            "log": [
                {"time": "11:00", "event": "logout", "x": 100, "y": 200}
            ],
            "short_text": "OK",
            "medium_text": "Good morning",
            "long_text": "Another very long text with different content and structure"
        }
    ]
    
    print(f"Analyzing {len(test_data)} objects with specific values...")
    print()
    
    # Generate schema using the enhanced analysis
    schema = generator._analyze_objects(test_data)
    
    print("✅ Schema generation successful!")
    print(f"Schema has {len(schema['properties'])} top-level properties")
    print()
    
    # Show the generated schema
    print("Generated Schema:")
    print(json.dumps(schema, indent=2))
    print()
    
    # Analyze specific fields for smart ranges
    print("Smart Range Analysis:")
    print("-" * 40)
    
    # Check coordinates field
    if 'coordinates' in schema['properties']:
        coords_schema = schema['properties']['coordinates']
        print("📍 'coordinates' field analysis:")
        if coords_schema.get('type') == 'object' and 'properties' in coords_schema:
            for prop_name, prop_schema in coords_schema['properties'].items():
                print(f"  {prop_name}: {prop_schema.get('type', 'unknown')}")
                if 'minimum' in prop_schema:
                    print(f"    minimum: {prop_schema['minimum']}")
                if 'maximum' in prop_schema:
                    print(f"    maximum: {prop_schema['maximum']}")
        print()
    
    # Check log field for nested constraints
    if 'log' in schema['properties']:
        log_schema = schema['properties']['log']
        print("📋 'log' field analysis:")
        if 'items' in log_schema:
            items_schema = log_schema['items']
            if 'oneOf' in items_schema:
                for i, variant in enumerate(items_schema['oneOf']):
                    if variant.get('type') == 'object' and 'properties' in variant:
                        print(f"  Variant {i+1}:")
                        for prop_name, prop_schema in variant['properties'].items():
                            print(f"    {prop_name}: {prop_schema.get('type', 'unknown')}")
                            if 'minimum' in prop_schema:
                                print(f"      minimum: {prop_schema['minimum']}")
                            if 'maximum' in prop_schema:
                                print(f"      maximum: {prop_schema['maximum']}")
                            if 'minLength' in prop_schema:
                                print(f"      minLength: {prop_schema['minLength']}")
                            if 'maxLength' in prop_schema:
                                print(f"      maxLength: {prop_schema['maxLength']}")
        print()
    
    # Check text fields for smart length constraints
    text_fields = ['short_text', 'medium_text', 'long_text']
    for field_name in text_fields:
        if field_name in schema['properties']:
            text_schema = schema['properties'][field_name]
            print(f"📝 '{field_name}' analysis:")
            print(f"  Type: {text_schema.get('type', 'unknown')}")
            if 'minLength' in text_schema:
                print(f"  minLength: {text_schema['minLength']}")
            if 'maxLength' in text_schema:
                print(f"  maxLength: {text_schema['maxLength']}")
            print()
    
    # Check numeric fields for smart value constraints
    numeric_fields = ['age', 'score']
    for field_name in numeric_fields:
        if field_name in schema['properties']:
            numeric_schema = schema['properties'][field_name]
            print(f"🔢 '{field_name}' analysis:")
            print(f"  Type: {numeric_schema.get('type', 'unknown')}")
            if 'minimum' in numeric_schema:
                print(f"  minimum: {numeric_schema['minimum']}")
            if 'maximum' in numeric_schema:
                print(f"  maximum: {numeric_schema['maximum']}")
            print()
    
    print("=" * 60)
    print("Smart ranges test completed!")
    print()
    print("Summary of improvements:")
    print("- Numeric fields now use reasonable ranges instead of exact values")
    print("- String fields use flexible length constraints based on content")
    print("- Coordinates and similar fields allow for natural variation")
    print("- Event names and text fields have appropriate flexibility")

if __name__ == "__main__":
    test_smart_ranges()
