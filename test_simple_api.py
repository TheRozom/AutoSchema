#!/usr/bin/env python3
"""
Simple test script for the new simplified API with just 2 routes:
1. Smart schema generation with configurable max nested depth
2. Object analysis without schema generation
"""

import json
from schema_generator import SchemaGenerator

def test_smart_schema_with_depth():
    """Test smart schema generation with different max nested depths."""
    
    print("🧪 Testing Smart Schema Generation with Configurable Depth")
    print("=" * 70)
    
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
    
    # Test with different max depths
    for max_depth in [3, 5, 8, 100]:
        print(f"\n📋 Testing with max_depth = {max_depth}")
        
        try:
            # Generate smart schema with custom depth
            schema = generator.generate_smart_hardened_schema_with_depth(test_data, max_depth)
            
            print(f"✅ Schema generated successfully with max_depth = {max_depth}")
            
            # Save to file
            filename = f"smart_schema_depth_{max_depth}.json"
            with open(filename, "w") as f:
                json.dump(schema, f, indent=2)
            
            print(f"💾 Schema saved to: {filename}")
            
            # Show schema description
            print(f"📝 Schema description: {schema.get('description', 'No description')}")
            
        except Exception as e:
            print(f"❌ Error with max_depth = {max_depth}: {e}")

def test_object_analysis():
    """Test object analysis without schema generation."""
    
    print("\n🧪 Testing Object Analysis")
    print("=" * 70)
    
    # Test data with complex nested structures
    test_data = [
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
    
    # Test analysis with different max depths
    for max_depth in [3, 5, 10]:
        print(f"\n📊 Testing analysis with max_depth = {max_depth}")
        
        try:
            # Analyze objects with custom depth
            analysis = generator.analyze_objects_with_depth(test_data, max_depth)
            
            print(f"✅ Analysis completed successfully with max_depth = {max_depth}")
            
            # Save to file
            filename = f"object_analysis_depth_{max_depth}.json"
            with open(filename, "w") as f:
                json.dump(analysis, f, indent=2)
            
            print(f"💾 Analysis saved to: {filename}")
            
            # Show summary
            summary = analysis.get('summary', {})
            print(f"📈 Summary:")
            print(f"   - Total objects: {analysis.get('total_objects', 0)}")
            print(f"   - Total fields: {summary.get('total_fields', 0)}")
            print(f"   - Fields with nesting: {summary.get('fields_with_nesting', 0)}")
            print(f"   - Fields with binary: {summary.get('fields_with_binary', 0)}")
            print(f"   - Fields with mixed types: {summary.get('fields_with_mixed_types', 0)}")
            print(f"   - Max nested depth found: {summary.get('max_nested_depth_found', 0)}")
            
            # Show field details
            print(f"🔍 Field Details:")
            for field_name, field_info in analysis.get('fields', {}).items():
                print(f"   - {field_name}: {field_info.get('types', [])}")
                if 'nested_structure' in field_info:
                    nested = field_info['nested_structure']
                    print(f"     Nested depth: {nested.get('max_depth', 0)}")
                    print(f"     Possible paths: {len(nested.get('all_possible_paths', []))}")
            
        except Exception as e:
            print(f"❌ Error with max_depth = {max_depth}: {e}")

def test_api_endpoints():
    """Test the API endpoints."""
    
    print("\n🌐 Testing API Endpoints")
    print("=" * 70)
    
    print("📋 Available endpoints:")
    print("   - POST /api/v1/schemas/smart")
    print("     Parameters: file (NDJSON), max_nested_depth (default: 100), sample_size (optional)")
    print("     Returns: JSON schema")
    print()
    print("   - POST /api/v1/analyze")
    print("     Parameters: file (NDJSON), max_nested_depth (default: 100), sample_size (optional)")
    print("     Returns: Object analysis (no schema)")
    print()
    print("🚀 To start the API server:")
    print("   python api.py")
    print()
    print("📖 API documentation will be available at:")
    print("   http://localhost:9000/docs")

if __name__ == "__main__":
    test_smart_schema_with_depth()
    test_object_analysis()
    test_api_endpoints()
    
    print("\n🎉 Testing completed!")
    print("Check the generated files to see the results.")
