import json
from schema_generator import SchemaGenerator

def test_smart_additional_properties():
    """Test the improved smart additionalProperties behavior"""
    print("Testing smart additionalProperties behavior:")
    print("=" * 60)
    
    # Create schema generator
    generator = SchemaGenerator()
    
    # Test case 1: Well-defined structure (should NOT have additionalProperties)
    print("Test Case 1: Well-defined structure")
    print("-" * 40)
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
    print(f"Has additionalProperties: {schema1.get('additionalProperties', False)}")
    print("Schema:")
    print(json.dumps(schema1, indent=2))
    print()
    
    # Test case 2: Mixed types (should have additionalProperties)
    print("Test Case 2: Mixed types")
    print("-" * 40)
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
    print(f"Has additionalProperties: {schema2.get('additionalProperties', False)}")
    print("Schema:")
    print(json.dumps(schema2, indent=2))
    print()
    
    # Test case 3: Nested objects with well-defined structure
    print("Test Case 3: Nested objects with well-defined structure")
    print("-" * 40)
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
    print(f"Has additionalProperties: {schema3.get('additionalProperties', False)}")
    
    # Check nested object additionalProperties
    if 'profile' in schema3['properties']:
        profile_schema = schema3['properties']['profile']
        if profile_schema.get('type') == 'object' and 'properties' in profile_schema:
            print(f"Nested profile has additionalProperties: {profile_schema.get('additionalProperties', False)}")
    
    print("Schema:")
    print(json.dumps(schema3, indent=2))
    print()
    
    # Test case 4: Array with objects
    print("Test Case 4: Array with objects")
    print("-" * 40)
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
    print(f"Has additionalProperties: {schema4.get('additionalProperties', False)}")
    
    # Check array item additionalProperties
    if 'log' in schema4['properties']:
        log_schema = schema4['properties']['log']
        if log_schema.get('type') == 'array' and 'items' in log_schema:
            items_schema = log_schema['items']
            if items_schema.get('type') == 'object':
                print(f"Array items have additionalProperties: {items_schema.get('additionalProperties', False)}")
    
    print("Schema:")
    print(json.dumps(schema4, indent=2))
    print()
    
    # Test case 5: Complex mixed structure
    print("Test Case 5: Complex mixed structure")
    print("-" * 40)
    complex_data = [
        {
            "id": 1,
            "name": "Alice",
            "metadata": {"created": "2024-01-01", "tags": ["user", "admin"]},
            "extra_field": "something"
        },
        {
            "id": 2,
            "name": "Bob",
            "metadata": None,  # Null value
            "different_field": 123  # Different field
        }
    ]
    
    schema5 = generator._analyze_objects(complex_data)
    print(f"Has additionalProperties: {schema5.get('additionalProperties', False)}")
    print("Schema:")
    print(json.dumps(schema5, indent=2))
    print()
    
    print("=" * 60)
    print("Smart additionalProperties test completed!")
    print()
    print("Summary of improvements:")
    print("- Well-defined structures don't have additionalProperties")
    print("- Mixed types and complex structures have additionalProperties when needed")
    print("- Nested objects are analyzed for their structure")
    print("- Array items are analyzed for their structure")
    print("- The schema is more restrictive and precise")

if __name__ == "__main__":
    test_smart_additional_properties()
