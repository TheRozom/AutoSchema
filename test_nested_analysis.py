import json
from schema_generator import SchemaGenerator

def test_nested_analysis():
    """Test the enhanced nested analysis with complex data structures"""
    print("Testing enhanced nested analysis:")
    print("=" * 60)
    
    # Create schema generator
    generator = SchemaGenerator()
    
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
    
    print(f"Analyzing {len(test_data)} objects with complex nested structures...")
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
    
    # Analyze specific nested structures
    print("Nested Structure Analysis:")
    print("-" * 40)
    
    # Analyze the 'log' field specifically
    if 'log' in schema['properties']:
        log_schema = schema['properties']['log']
        print("📋 'log' field analysis:")
        print(f"  Type: {log_schema.get('type', 'unknown')}")
        
        if 'items' in log_schema:
            items_schema = log_schema['items']
            if 'oneOf' in items_schema:
                print(f"  Items: Multiple object types ({len(items_schema['oneOf'])} variants)")
                for i, variant in enumerate(items_schema['oneOf']):
                    if variant.get('type') == 'object' and 'properties' in variant:
                        props = list(variant['properties'].keys())
                        print(f"    Variant {i+1}: {props}")
            elif items_schema.get('type') == 'object' and 'properties' in items_schema:
                props = list(items_schema['properties'].keys())
                print(f"  Items: Object with properties: {props}")
        
        print()
    
    # Analyze the 'profile' field
    if 'profile' in schema['properties']:
        profile_schema = schema['properties']['profile']
        print("👤 'profile' field analysis:")
        print(f"  Type: {profile_schema.get('type', 'unknown')}")
        
        if profile_schema.get('type') == 'object' and 'properties' in profile_schema:
            props = list(profile_schema['properties'].keys())
            print(f"  Properties: {props}")
            
            # Show details for each property
            for prop_name, prop_schema in profile_schema['properties'].items():
                prop_type = prop_schema.get('type', 'unknown')
                print(f"    {prop_name}: {prop_type}")
                if 'minLength' in prop_schema:
                    print(f"      minLength: {prop_schema['minLength']}")
                if 'maxLength' in prop_schema:
                    print(f"      maxLength: {prop_schema['maxLength']}")
                if 'minimum' in prop_schema:
                    print(f"      minimum: {prop_schema['minimum']}")
                if 'maximum' in prop_schema:
                    print(f"      maximum: {prop_schema['maximum']}")
        
        print()
    
    # Analyze the 'devices' field
    if 'devices' in schema['properties']:
        devices_schema = schema['properties']['devices']
        print("📱 'devices' field analysis:")
        print(f"  Type: {devices_schema.get('type', 'unknown')}")
        
        if 'items' in devices_schema:
            items_schema = devices_schema['items']
            if items_schema.get('type') == 'object' and 'properties' in items_schema:
                props = list(items_schema['properties'].keys())
                print(f"  Items: Object with properties: {props}")
                
                # Show details for each property
                for prop_name, prop_schema in items_schema['properties'].items():
                    prop_type = prop_schema.get('type', 'unknown')
                    print(f"    {prop_name}: {prop_type}")
        
        print()
    
    # Show field analysis details
    print("Field Analysis Details:")
    print("-" * 40)
    
    # Get the field analysis to show what was detected
    field_analysis = generator._analyze_fields(test_data)
    
    for field_name, analysis in field_analysis.items():
        print(f"🔍 {field_name}:")
        print(f"  Types: {list(analysis['types'])}")
        print(f"  Required: {analysis.get('required', False)}")
        print(f"  Null percentage: {analysis.get('null_percentage', 0):.1%}")
        
        # Show nested structure info if available
        if 'nested_structure' in analysis:
            nested = analysis['nested_structure']
            print(f"  Nested fields: {list(nested['fields'])}")
            for field, types in nested['field_types'].items():
                print(f"    {field}: {list(types)}")
        
        # Show array structure info if available
        if 'array_structure' in analysis:
            array_struct = analysis['array_structure']
            print(f"  Array item types: {list(array_struct['item_types'])}")
            if array_struct['nested_objects']:
                print(f"  Contains nested objects: {len(array_struct['item_schemas'])} different structures")
                for keys, schema_info in array_struct['item_schemas'].items():
                    print(f"    Structure {keys}: {list(schema_info['fields'])} (count: {schema_info['count']})")
        
        print()
    
    print("=" * 60)
    print("Enhanced nested analysis test completed!")

if __name__ == "__main__":
    test_nested_analysis()
