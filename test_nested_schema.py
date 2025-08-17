#!/usr/bin/env python3
"""
Test script for improved nested structure handling.
This demonstrates the new recursive analysis that can handle deeply nested structures up to 100 levels.
"""

import json
from schema_generator import SchemaGenerator

def test_nested_structures():
    """Test the improved nested structure handling."""
    
    print("🧪 Testing Improved Nested Structure Handling")
    print("=" * 60)
    
    # Test data with deeply nested structures
    test_data = [
    {"level1": {"value": "a"}},
    {"level1": {"level2": {"value": "b"}}},
    {"level1": {"level2": {"level3": {"value": "c"}}}},
    {"level1": {"level2": {"level3": {"level4": {"value": "d"}}}}},
    {"level1": {"level2": {"level3": {"level4": {"level5": {"value": "e"}}}}}},
    {"level1": {"level2": {"level3": {"level4": {"level5": {"level6": {"value": "f"}}}}}}},
    {"level1": {"level2": {"level3": {"level4": {"level5": {"level6": {"level7": {"value": "g"}}}}}}}},
    {"level1": {"level2": {"level3": {"level4": {"level5": {"level6": {"level7": {"level8": {"value": "h"}}}}}}}}}
]

    
    generator = SchemaGenerator()
    
    try:
        # Generate smart hardened schema
        print("📋 Generating Smart Hardened Schema for nested structures...")
        smart_schema = generator.generate_smart_hardened_schema(test_data)
        
        print("✅ Smart Hardened Schema generated successfully!")
        print("\n📊 Generated Schema:")
        print(json.dumps(smart_schema, indent=2))
        
        # Save to file
        with open("nested_test_schema.json", "w") as f:
            json.dump(smart_schema, f, indent=2)
        
        print("\n💾 Schema saved to: nested_test_schema.json")
        
        # Test with NDJSON file
        print("\n📁 Testing with NDJSON file...")
        
        # Create NDJSON file
        with open("test_nested.ndjson", "w") as f:
            for item in test_data:
                f.write(json.dumps(item) + "\n")
        
        # Generate schema from file
        file_schema = generator.analyze_ndjson_file("test_nested.ndjson")
        
        print("✅ Schema generated from NDJSON file successfully!")
        
        # Save file schema
        with open("nested_file_schema.json", "w") as f:
            json.dump(file_schema, f, indent=2)
        
        print("💾 File schema saved to: nested_file_schema.json")
        
        # Show analysis details
        print("\n🔍 Analysis Details:")
        field_analysis = generator._analyze_fields_deep(test_data)
        
        for field_name, analysis in field_analysis.items():
            print(f"\nField: {field_name}")
            print(f"  Types: {analysis.get('types', set())}")
            print(f"  Max Depth Found: {analysis.get('max_depth_found', 0)}")
            print(f"  All Possible Paths: {len(analysis.get('all_possible_paths', set()))}")
            
            if 'structure_hierarchy' in analysis:
                hierarchy = analysis['structure_hierarchy']
                print(f"  Structure Hierarchy:")
                for depth, level_info in hierarchy.items():
                    print(f"    Depth {depth}: {len(level_info.get('fields', set()))} fields")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def test_complex_nested():
    """Test with more complex nested structures."""
    
    print("\n🧪 Testing Complex Nested Structures")
    print("=" * 60)
    
    # More complex test data
    complex_data = [
        {
            "user": {
                "profile": {
                    "personal": {
                        "name": "John",
                        "age": 30,
                        "preferences": {
                            "theme": "dark",
                            "notifications": {
                                "email": True,
                                "push": False,
                                "settings": {
                                    "frequency": "daily",
                                    "types": ["news", "updates"]
                                }
                            }
                        }
                    }
                }
            }
        },
        {
            "user": {
                "profile": {
                    "personal": {
                        "name": "Jane",
                        "age": 25
                    },
                    "work": {
                        "company": "Tech Corp",
                        "department": {
                            "name": "Engineering",
                            "team": {
                                "lead": "Bob",
                                "members": ["Alice", "Charlie"]
                            }
                        }
                    }
                }
            }
        }
    ]
    
    generator = SchemaGenerator()
    
    try:
        print("📋 Generating schema for complex nested structures...")
        schema = generator.generate_smart_hardened_schema(complex_data)
        
        print("✅ Complex nested schema generated successfully!")
        
        # Save to file
        with open("complex_nested_schema.json", "w") as f:
            json.dump(schema, f, indent=2)
        
        print("💾 Complex nested schema saved to: complex_nested_schema.json")
        
        # Show the schema
        print("\n📊 Complex Nested Schema:")
        print(json.dumps(schema, indent=2))
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_nested_structures()
    test_complex_nested()
    
    print("\n🎉 Testing completed!")
    print("Check the generated schema files to see the improved nested structure handling.")
