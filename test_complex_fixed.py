import requests
import json

def test_complex_data():
    """Test the fixed API with complex data"""
    print("Testing fixed API with complex data:")
    print("=" * 50)
    
    # API base URL
    base_url = "http://localhost:9090"
    
    # Test with the complex data file
    try:
        # Test smart schema generation with complex data
        print("Testing smart schema generation with complex data...")
        with open('test_complex_data.ndjson', 'rb') as f:
            files = {'file': ('test_complex_data.ndjson', f, 'application/json')}
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
        
        # Test analysis with complex data
        print("\nTesting analysis with complex data...")
        with open('test_complex_data.ndjson', 'rb') as f:
            files = {'file': ('test_complex_data.ndjson', f, 'application/json')}
            response = requests.post(f"{base_url}/api/v1/analyze", files=files)
        
        if response.status_code == 200:
            analysis = response.json()
            print("✅ Analysis successful!")
            print(f"Analyzed {analysis['analysis']['total_objects']} objects")
            print(f"Found {analysis['analysis']['summary']['total_fields']} fields")
            print(f"Fields with binary: {analysis['analysis']['summary']['fields_with_binary']}")
            print(f"Fields with mixed types: {analysis['analysis']['summary']['fields_with_mixed_types']}")
        else:
            print(f"❌ Analysis failed: {response.status_code}")
            print(f"Error: {response.text}")
            
    except FileNotFoundError:
        print("❌ test_complex_data.ndjson file not found")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("Test completed!")

if __name__ == "__main__":
    test_complex_data()
