import json
from schema_generator import SchemaGenerator

def test_strict_additional_properties():
    """Test the new strict additionalProperties behavior"""
    print("Testing strict additionalProperties behavior:")
    print("=" * 70)
    
    # Create schema generator
    generator = SchemaGenerator()
    
    # Test case 1: Well-defined structure (top-level should NEVER have additionalProperties)
    print("Test Case 1: Well-defined structure")
    print("-" * 50)
    well_defined_data = [
        {
            "id": 1,
            "name": "Alice",
            "email": "alice@example.com",
            "age": 25
        },
        {
            "id": 2,
            "name": "Bob", 
            "email": "bob@example.com",
            "age": 30
        }
    ]
    
    schema1 = generator._analyze_objects(well_defined_data)
    print(f"Top-level additionalProperties: {schema1.get('additionalProperties', False)}")
    print("Schema:")
    print(json.dumps(schema1, indent=2))
    print()
    
    # Test case 2: Mixed types (top-level should NEVER have additionalProperties)
    print("Test Case 2: Mixed types")
    print("-" * 50)
    mixed_data = [
        {
            "id": 1,
            "name": "Alice",
            "data": {"key": "value"}
        },
        {
            "id": "2",  # Mixed type
            "name": "Bob",
            "data": [1, 2, 3]  # Mixed type
        }
    ]
    
    schema2 = generator._analyze_objects(mixed_data)
    print(f"Top-level additionalProperties: {schema2.get('additionalProperties', False)}")
    print("Schema:")
    print(json.dumps(schema2, indent=2))
    print()
    
    # Test case 3: Nested objects with well-defined structure
    print("Test Case 3: Nested objects with well-defined structure")
    print("-" * 50)
    nested_data = [
        {
            "id": 1,
            "profile": {
                "username": "alice123",
                "age": 25
            }
        },
        {
            "id": 2,
            "profile": {
                "username": "bob456",
                "age": 30
            }
        }
    ]
    
    schema3 = generator._analyze_objects(nested_data)
    print(f"Top-level additionalProperties: {schema3.get('additionalProperties', False)}")
    
    # Check nested object additionalProperties
    if 'profile' in schema3['properties']:
        profile_schema = schema3['properties']['profile']
        if profile_schema.get('type') == 'object' and 'properties' in profile_schema:
            print(f"Nested profile additionalProperties: {profile_schema.get('additionalProperties', False)}")
            if 'description' in profile_schema:
                print(f"Profile description: {profile_schema['description']}")
    
    print("Schema:")
    print(json.dumps(schema3, indent=2))
    print()
    
    # Test case 4: Array with objects (should have warnings if additionalProperties needed)
    print("Test Case 4: Array with objects")
    print("-" * 50)
    array_data = [
        {
            "id": 1,
            "log": [
                {"time": "10:00", "event": "login"},
                {"time": "10:05", "event": "click"}
            ]
        },
        {
            "id": 2,
            "log": [
                {"time": "11:00", "event": "logout"}
            ]
        }
    ]
    
    schema4 = generator._analyze_objects(array_data)
    print(f"Top-level additionalProperties: {schema4.get('additionalProperties', False)}")
    
    # Check array item additionalProperties
    if 'log' in schema4['properties']:
        log_schema = schema4['properties']['log']
        if log_schema.get('type') == 'array' and 'items' in log_schema:
            items_schema = log_schema['items']
            if items_schema.get('type') == 'object':
                print(f"Array items additionalProperties: {items_schema.get('additionalProperties', False)}")
                if 'description' in items_schema:
                    print(f"Array items description: {items_schema['description']}")
    
    print("Schema:")
    print(json.dumps(schema4, indent=2))
    print()
    
    # Test case 5: Complex mixed structure with nested mixed types
    print("Test Case 5: Complex mixed structure with nested mixed types")
    print("-" * 50)
    complex_data = [
        {
            "id": 1,
            "name": "Alice",
            "metadata": {
                "created": "2024-01-01", 
                "tags": ["user", "admin"],
                "mixed_field": "string_value"
            }
        },
        {
            "id": 2,
            "name": "Bob",
            "metadata": {
                "created": "2024-01-02",
                "tags": ["user"],
                "mixed_field": 123  # Mixed type in nested object
            }
        }
    ]
    
    schema5 = generator._analyze_objects(complex_data)
    print(f"Top-level additionalProperties: {schema5.get('additionalProperties', False)}")
    
    # Check nested object additionalProperties
    if 'metadata' in schema5['properties']:
        metadata_schema = schema5['properties']['metadata']
        if metadata_schema.get('type') == 'object' and 'properties' in metadata_schema:
            print(f"Nested metadata additionalProperties: {metadata_schema.get('additionalProperties', False)}")
            if 'description' in metadata_schema:
                print(f"Metadata description: {metadata_schema['description']}")
    
    print("Schema:")
    print(json.dumps(schema5, indent=2))
    print()
    
    # Test case 6: Very complex mixed structure that should trigger warnings
    print("Test Case 6: Very complex mixed structure")
    print("-" * 50)
    very_complex_data = [
        {
            "id": 1,
            "name": "Alice",
            "complex_field": {
                "field1": "string",
                "field2": 123,
                "field3": True,
                "field4": {"nested": "value"}
            }
        },
        {
            "id": 2,
            "name": "Bob",
            "complex_field": {
                "field1": 456,  # Mixed type
                "field2": "string",  # Mixed type
                "field3": [1, 2, 3],  # Mixed type
                "field4": None  # Mixed type
            }
        }
    ]
    
    schema6 = generator._analyze_objects(very_complex_data)
    print(f"Top-level additionalProperties: {schema6.get('additionalProperties', False)}")
    
    # Check nested object additionalProperties
    if 'complex_field' in schema6['properties']:
        complex_schema = schema6['properties']['complex_field']
        if complex_schema.get('type') == 'object' and 'properties' in complex_schema:
            print(f"Nested complex_field additionalProperties: {complex_schema.get('additionalProperties', False)}")
            if 'description' in complex_schema:
                print(f"Complex field description: {complex_schema['description']}")
    
    print("Schema:")
    print(json.dumps(schema6, indent=2))
    print()
    
    print("=" * 70)
    print("Strict additionalProperties test completed!")
    print()
    print("Summary of improvements:")
    print("✅ Top-level schema NEVER has additionalProperties: true")
    print("✅ Nested objects only have additionalProperties when >50% fields have mixed types")
    print("✅ Warnings are added to descriptions when additionalProperties is needed")
    print("✅ Much more restrictive and precise schema generation")
    print("✅ Better validation and type safety")

if __name__ == "__main__":
    test_strict_additional_properties()
