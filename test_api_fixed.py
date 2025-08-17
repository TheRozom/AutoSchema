import requests
import json
import tempfile
import os

def test_api_fixed():
    """Test the fixed API with flexible schema generation"""
    print("Testing fixed API with flexible schema generation:")
    print("=" * 60)
    
    # API base URL
    base_url = "http://localhost:9000"
    
    # Test data with varying lengths
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
    
    # Create temporary NDJSON file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.ndjson') as temp_file:
        for obj in test_data:
            temp_file.write(json.dumps(obj) + '\n')
        temp_file_path = temp_file.name
    
    try:
        # Test the smart schema endpoint
        print("Testing /api/v1/schemas/smart endpoint...")
        with open(temp_file_path, 'rb') as f:
            files = {'file': ('test_data.ndjson', f, 'application/json')}
            response = requests.post(f"{base_url}/api/v1/schemas/smart", files=files)
        
        if response.status_code == 200:
            print("✅ Smart schema endpoint works!")
            schema = response.json()['schema']
            
            # Check if schema is flexible
            properties = schema.get("properties", {})
            length_constrained_fields = 0
            
            for field_name, field_schema in properties.items():
                if "minLength" in field_schema or "maxLength" in field_schema:
                    length_constrained_fields += 1
            
            print(f"Fields with length constraints: {length_constrained_fields}")
            if length_constrained_fields < len(properties) * 0.3:  # Less than 30% have constraints
                print("✅ Schema appears to be flexible (few length constraints)")
            else:
                print("⚠️  Schema may still be too restrictive")
            
        else:
            print(f"❌ Smart schema endpoint failed: {response.status_code}")
            print(f"Response: {response.text}")
        
        # Test the flexible schema endpoint
        print("\nTesting /api/v1/schemas/flexible endpoint...")
        with open(temp_file_path, 'rb') as f:
            files = {'file': ('test_data.ndjson', f, 'application/json')}
            response = requests.post(f"{base_url}/api/v1/schemas/flexible", files=files)
        
        if response.status_code == 200:
            print("✅ Flexible schema endpoint works!")
            schema = response.json()['schema']
            
            # Check if schema is very flexible
            properties = schema.get("properties", {})
            length_constrained_fields = 0
            
            for field_name, field_schema in properties.items():
                if "minLength" in field_schema or "maxLength" in field_schema:
                    length_constrained_fields += 1
            
            print(f"Fields with length constraints: {length_constrained_fields}")
            if length_constrained_fields == 0:
                print("✅ Schema is very flexible (no length constraints)")
            else:
                print(f"⚠️  Schema has {length_constrained_fields} fields with length constraints")
            
        else:
            print(f"❌ Flexible schema endpoint failed: {response.status_code}")
            print(f"Response: {response.text}")
        
        # Test the analyze endpoint
        print("\nTesting /api/v1/analyze endpoint...")
        with open(temp_file_path, 'rb') as f:
            files = {'file': ('test_data.ndjson', f, 'application/json')}
            response = requests.post(f"{base_url}/api/v1/analyze", files=files)
        
        if response.status_code == 200:
            print("✅ Analyze endpoint works!")
            analysis = response.json()['analysis']
            print(f"Analysis summary: {analysis.get('summary', {})}")
        else:
            print(f"❌ Analyze endpoint failed: {response.status_code}")
            print(f"Response: {response.text}")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API. Make sure the server is running on localhost:9000")
        print("Start the server with: python api.py")
    except Exception as e:
        print(f"❌ Test failed: {e}")
    finally:
        # Clean up
        os.unlink(temp_file_path)
    
    print("\n" + "=" * 60)
    print("Test Summary:")
    print("-" * 30)
    print("The API should now generate flexible schemas that work with varying data lengths.")
    print("If you see ✅ messages above, the fixes are working correctly!")

if __name__ == "__main__":
    test_api_fixed()
