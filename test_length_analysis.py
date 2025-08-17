import json
from schema_generator import SchemaGenerator

def analyze_length_patterns():
    """Analyze length patterns in the test data"""
    print("Analyzing length patterns in test data...")
    
    # Create schema generator
    generator = SchemaGenerator()
    
    # Read the complex test data
    with open('test_complex_data.ndjson', 'r', encoding='utf-8') as f:
        ndjson_content = f.read()
    
    # Parse objects
    objects = generator.parse_ndjson(ndjson_content)
    
    # Analyze each field's length patterns
    field_lengths = {}
    
    for obj in objects:
        for field_name, value in obj.items():
            if isinstance(value, str):
                if field_name not in field_lengths:
                    field_lengths[field_name] = []
                field_lengths[field_name].append(len(value))
    
    print("\n📊 Length Analysis by Field:")
    print("-" * 50)
    
    for field_name, lengths in field_lengths.items():
        min_len = min(lengths)
        max_len = max(lengths)
        unique_lengths = len(set(lengths))
        
        print(f"\n{field_name}:")
        print(f"  Min length: {min_len}")
        print(f"  Max length: {max_len}")
        print(f"  Unique lengths: {unique_lengths}")
        print(f"  All lengths: {sorted(set(lengths))}")
        
        if min_len == max_len:
            print(f"  ⚠️  WARNING: Min and max are the same!")
        elif unique_lengths <= 3:
            print(f"  ⚠️  WARNING: Very few unique lengths ({unique_lengths})")
    
    # Generate schema and check min/max constraints
    print("\n" + "=" * 60)
    print("Checking generated schema for min/max length issues:")
    print("-" * 50)
    
    schema = generator.analyze_ndjson(ndjson_content)
    properties = schema.get("properties", {})
    
    problematic_fields = []
    
    for field_name, field_schema in properties.items():
        if isinstance(field_schema, dict):
            min_length = field_schema.get("minLength")
            max_length = field_schema.get("maxLength")
            
            if min_length is not None and max_length is not None:
                if min_length == max_length:
                    problematic_fields.append((field_name, min_length, max_length, "Same min/max"))
                elif max_length - min_length <= 5:
                    problematic_fields.append((field_name, min_length, max_length, "Very small range"))
    
    if problematic_fields:
        print("\n❌ Problematic fields with min/max length constraints:")
        for field_name, min_len, max_len, issue in problematic_fields:
            print(f"  {field_name}: minLength={min_len}, maxLength={max_len} ({issue})")
    else:
        print("\n✅ No problematic min/max length constraints found!")

if __name__ == "__main__":
    analyze_length_patterns()
