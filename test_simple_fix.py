import requests
import json
import tempfile
import os

def test_simple_fix():
    """Test the reverted API with simple data"""
    print("Testing reverted API with simple data:")
    print("=" * 50)
    
    # API base URL
    base_url = "http://localhost:9090"
    
    # Test data from user
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
        # Test smart schema generation
        print("Testing smart schema generation...")
        with open(temp_file_path, 'rb') as f:
            files = {'file': ('test_data.ndjson', f, 'application/json')}
            response = requests.post(f"{base_url}/api/v1/schemas/smart", files=files)
        
        if response.status_code == 200:
            schema = response.json()
            print("✅ Smart schema generation successful!")
            print(f"Schema has {len(schema['schema']['properties'])} properties")
            print("Properties:", list(schema['schema']['properties'].keys()))
            
            # Check for max length constraints
            for prop_name, prop_schema in schema['schema']['properties'].items():
                if prop_schema.get('type') == 'string' and 'maxLength' in prop_schema:
                    print(f"  - {prop_name}: maxLength = {prop_schema['maxLength']}")
        else:
            print(f"❌ Smart schema generation failed: {response.status_code}")
            print(f"Error: {response.text}")
        
        # Test analysis endpoint
        print("\nTesting analysis endpoint...")
        with open(temp_file_path, 'rb') as f:
            files = {'file': ('test_data.ndjson', f, 'application/json')}
            response = requests.post(f"{base_url}/api/v1/analyze", files=files)
        
        if response.status_code == 200:
            analysis = response.json()
            print("✅ Analysis successful!")
            print(f"Analyzed {analysis['analysis']['total_objects']} objects")
            print(f"Found {analysis['analysis']['summary']['total_fields']} fields")
        else:
            print(f"❌ Analysis failed: {response.status_code}")
            print(f"Error: {response.text}")
            
    finally:
        # Clean up
        os.unlink(temp_file_path)
    
    print("\n" + "=" * 50)
    print("Test completed!")

if __name__ == "__main__":
    test_simple_fix()
