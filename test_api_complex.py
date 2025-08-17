import requests
import json

def test_api_with_complex_data():
    """Test the API with complex NDJSON data"""
    print("Testing API with complex NDJSON data...")
    
    # API endpoint
    url = "http://localhost:9000/api/v1/schemas/smart"
    
    # Read the complex test data
    with open('test_complex_data.ndjson', 'rb') as f:
        files = {'file': ('test_complex_data.ndjson', f, 'application/json')}
        
        print("Sending request to API...")
        response = requests.post(url, files=files)
    
    if response.status_code == 200:
        result = response.json()
        schema = result.get('schema', {})
        
        print("✅ API call successful!")
        print(f"📄 Schema received with {len(schema.get('properties', {}))} properties")
        
        # Save the schema to file
        with open('api_generated_schema.json', 'w') as f:
            json.dump(schema, f, indent=2)
        
        print("📄 Schema saved to: api_generated_schema.json")
        
        # Show statistics
        properties = schema.get("properties", {})
        required_fields = schema.get("required", [])
        
        print(f"\n📊 Schema Statistics:")
        print(f"   Total properties: {len(properties)}")
        print(f"   Required fields: {len(required_fields)}")
        print(f"   Optional fields: {len(properties) - len(required_fields)}")
        
        # Count binary fields
        binary_fields = []
        for field_name, field_schema in properties.items():
            if isinstance(field_schema, dict) and field_schema.get("contentEncoding") == "base64":
                binary_fields.append(field_name)
        
        print(f"   Binary fields: {len(binary_fields)}")
        if binary_fields:
            print(f"   Binary field names: {', '.join(binary_fields)}")
        
        # Show a few key properties
        print(f"\n🔍 Sample Properties:")
        sample_fields = list(properties.keys())[:5]
        for field in sample_fields:
            field_schema = properties[field]
            if isinstance(field_schema, dict):
                field_type = field_schema.get("type", "mixed")
                is_binary = field_schema.get("contentEncoding") == "base64"
                is_required = field in required_fields
                print(f"   {field}: {field_type}{' (binary)' if is_binary else ''}{' (required)' if is_required else ''}")
        
        # Show the first few lines of the schema
        print(f"\n📋 Schema Preview (first 10 lines):")
        schema_str = json.dumps(schema, indent=2)
        lines = schema_str.split('\n')[:10]
        for line in lines:
            print(f"   {line}")
        if len(schema_str.split('\n')) > 10:
            print("   ...")
            
    else:
        print(f"❌ API call failed with status code: {response.status_code}")
        print(f"Error: {response.text}")

if __name__ == "__main__":
    test_api_with_complex_data()
