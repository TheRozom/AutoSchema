import requests
import json
import tempfile
import os

def test_api_simple():
    """Test the fixed API with simple data"""
    print("Testing fixed API with simple data:")
    print("=" * 50)
    
    # API base URL
    base_url = "http://localhost:9090"
    
    # Simple test data
    test_data = [
        {
            "id": 1,
            "name": "John",
            "email": "john@test.com",
            "age": 25,
            "active": True,
            "tags": ["user", "admin"]
        },
        {
            "id": 2,
            "name": "Jane",
            "email": "jane@test.com",
            "age": 30,
            "active": False,
            "tags": ["user"]
        }
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
        else:
            print(f"❌ Smart schema generation failed: {response.status_code}")
            print(f"Error: {response.text}")
        
        # Test flexible schema generation
        print("\nTesting flexible schema generation...")
        with open(temp_file_path, 'rb') as f:
            files = {'file': ('test_data.ndjson', f, 'application/json')}
            response = requests.post(f"{base_url}/api/v1/schemas/flexible", files=files)
        
        if response.status_code == 200:
            schema = response.json()
            print("✅ Flexible schema generation successful!")
            print(f"Schema has {len(schema['schema']['properties'])} properties")
        else:
            print(f"❌ Flexible schema generation failed: {response.status_code}")
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
    test_api_simple()
