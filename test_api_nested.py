import requests
import json
import tempfile
import os

def test_api_nested():
    """Test the API with enhanced nested analysis"""
    print("Testing API with enhanced nested analysis:")
    print("=" * 60)
    
    # API base URL
    base_url = "http://localhost:9090"
    
    # Test data with complex nested structures
    test_data = [
        {"id": 1, "name": "Alice", "email": "alice@example.com"},
        {"id": 2, "name": "Bob", "phones": ["+1-555-1234", "+1-555-5678"], "active": True},
        {"id": 3, "profile": {"username": "charlie", "age": 29}, "tags": ["premium", "beta"]},
        {"id": 4, "name": "Dana", "address": {"city": "Berlin", "zip": 10115}, "preferences": None},
        {"id": 5, "meta": {"created_at": "2025-08-17T19:30:00Z"}, "score": 87.5},
        {"id": "6a", "name": "Eve", "devices": [{"type": "mobile", "os": "Android"}, {"type": "laptop"}]},
        {"id": 7, "misc": [1, "two", {"nested": True}], "active": "yes"},
        {"id": 8, "binary_data": "SGVsbG8gV29ybGQ=", "extra": {"random": 42}},
        {"id": 9, "profile": {"username": "frank"}, "tags": None, "preferences": {"theme": "dark"}},
        {"id": 10, "log": [{"time": "10:00", "event": "login"}, {"time": "10:05", "event": "click", "x": 45, "y": 60}]}
    ]
    
    # Create temporary NDJSON file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.ndjson') as temp_file:
        for obj in test_data:
            temp_file.write(json.dumps(obj) + '\n')
        temp_file_path = temp_file.name
    
    try:
        # Test smart schema generation with nested analysis
        print("Testing smart schema generation with nested analysis...")
        with open(temp_file_path, 'rb') as f:
            files = {'file': ('test_nested_data.ndjson', f, 'application/json')}
            response = requests.post(f"{base_url}/api/v1/schemas/smart", files=files)
        
        if response.status_code == 200:
            schema = response.json()
            print("✅ Smart schema generation successful!")
            print(f"Schema has {len(schema['schema']['properties'])} top-level properties")
            
            # Check for nested structures
            print("\nNested Structure Analysis:")
            print("-" * 40)
            
            for prop_name, prop_schema in schema['schema']['properties'].items():
                print(f"🔍 {prop_name}: {prop_schema.get('type', 'unknown')}")
                
                # Check for nested objects
                if prop_schema.get('type') == 'object' and 'properties' in prop_schema:
                    nested_props = list(prop_schema['properties'].keys())
                    print(f"  Nested properties: {nested_props}")
                    
                    # Show details for nested properties
                    for nested_prop, nested_schema in prop_schema['properties'].items():
                        nested_type = nested_schema.get('type', 'unknown')
                        print(f"    {nested_prop}: {nested_type}")
                        if 'minLength' in nested_schema:
                            print(f"      minLength: {nested_schema['minLength']}")
                        if 'maxLength' in nested_schema:
                            print(f"      maxLength: {nested_schema['maxLength']}")
                        if 'minimum' in nested_schema:
                            print(f"      minimum: {nested_schema['minimum']}")
                        if 'maximum' in nested_schema:
                            print(f"      maximum: {nested_schema['maximum']}")
                
                # Check for arrays with nested objects
                elif prop_schema.get('type') == 'array' and 'items' in prop_schema:
                    items_schema = prop_schema['items']
                    if items_schema.get('type') == 'object' and 'properties' in items_schema:
                        array_props = list(items_schema['properties'].keys())
                        print(f"  Array items: Object with properties: {array_props}")
                        
                        # Show details for array item properties
                        for array_prop, array_prop_schema in items_schema['properties'].items():
                            array_prop_type = array_prop_schema.get('type', 'unknown')
                            print(f"    {array_prop}: {array_prop_type}")
                            if 'minLength' in array_prop_schema:
                                print(f"      minLength: {array_prop_schema['minLength']}")
                            if 'maxLength' in array_prop_schema:
                                print(f"      maxLength: {array_prop_schema['maxLength']}")
                            if 'minimum' in array_prop_schema:
                                print(f"      minimum: {array_prop_schema['minimum']}")
                            if 'maximum' in array_prop_schema:
                                print(f"      maximum: {array_prop_schema['maximum']}")
                    elif 'oneOf' in items_schema:
                        print(f"  Array items: Multiple object types ({len(items_schema['oneOf'])} variants)")
                        for i, variant in enumerate(items_schema['oneOf']):
                            if variant.get('type') == 'object' and 'properties' in variant:
                                variant_props = list(variant['properties'].keys())
                                print(f"    Variant {i+1}: {variant_props}")
                
                print()
        else:
            print(f"❌ Smart schema generation failed: {response.status_code}")
            print(f"Error: {response.text}")
        
        # Test analysis endpoint
        print("Testing analysis endpoint...")
        with open(temp_file_path, 'rb') as f:
            files = {'file': ('test_nested_data.ndjson', f, 'application/json')}
            response = requests.post(f"{base_url}/api/v1/analyze", files=files)
        
        if response.status_code == 200:
            analysis = response.json()
            print("✅ Analysis successful!")
            print(f"Analyzed {analysis['analysis']['total_objects']} objects")
            print(f"Found {analysis['analysis']['summary']['total_fields']} fields")
            
            # Show field details
            print("\nField Details:")
            print("-" * 40)
            for field_name, field_info in analysis['analysis']['fields'].items():
                print(f"🔍 {field_name}:")
                print(f"  Types: {field_info['types']}")
                print(f"  Required: {field_info['is_required']}")
                print(f"  Null percentage: {field_info['null_percentage']:.1%}")
                print(f"  Binary: {field_info['is_binary']}")
                print(f"  Mixed types: {field_info['is_mixed']}")
                print()
        else:
            print(f"❌ Analysis failed: {response.status_code}")
            print(f"Error: {response.text}")
            
    finally:
        # Clean up
        os.unlink(temp_file_path)
    
    print("=" * 60)
    print("Enhanced nested analysis API test completed!")

if __name__ == "__main__":
    test_api_nested()
