#!/usr/bin/env python3
"""
Example usage of the AutoSchema schema generator.
This script demonstrates how to use the SchemaGenerator class to create JSON schemas from NDJSON data.
No external LLM required - uses intelligent pattern analysis.
"""

import json
import base64
from schema_generator import SchemaGenerator

def main():
    """Main function demonstrating NDJSON schema generation."""
    
    # Sample NDJSON data with various content types including binary-like data
    ndjson_content = """{"id": 1, "name": "John Doe", "email": "john@example.com", "age": 30, "is_active": true, "binary_data": "SGVsbG8gV29ybGQ=", "mixed_content": "text content", "metadata": {"created_at": "2023-01-15T10:30:00Z", "tags": ["user", "active"]}}
{"id": 2, "name": "Jane Smith", "email": "jane@example.com", "age": 25, "is_active": false, "binary_data": null, "mixed_content": 42, "metadata": {"created_at": "2023-01-16T11:45:00Z", "tags": ["user", "inactive"]}}
{"id": 3, "name": "Bob Johnson", "email": "bob@example.com", "age": 35, "is_active": true, "binary_data": "V2VsY29tZSB0byB0aGUgd29ybGQ=", "mixed_content": ["item1", "item2", "item3", "item4"], "metadata": {"created_at": "2023-01-17T09:15:00Z", "tags": ["user", "active"]}}
{"id": 4, "name": "Alice Brown", "email": "alice@example.com", "age": 28, "is_active": true, "binary_data": "QmluYXJ5IGRhdGEgZXhhbXBsZQ==", "mixed_content": {"key": "value", "nested": {"data": "example"}}, "metadata": {"created_at": "2023-01-18T14:20:00Z", "tags": ["user", "active"]}}
{"id": 5, "name": "Charlie Wilson", "email": "charlie@example.com", "age": 32, "is_active": false, "binary_data": "QW5vdGhlciBiaW5hcnkgZXhhbXBsZQ==", "mixed_content": "another text", "metadata": {"created_at": "2023-01-19T16:30:00Z", "tags": ["user", "inactive"]}}"""

    print("🚀 AutoSchema - NDJSON Schema Generator")
    print("=" * 60)
    print("Analyzing NDJSON data with intelligent pattern analysis...")
    print("No external LLM required - uses rule-based analysis!")
    print()

    generator = SchemaGenerator()
    
    try:
        # Generate standard JSON Schema
        print("📋 Generating Standard JSON Schema...")
        json_schema = generator.analyze_ndjson(ndjson_content)
        print("✅ Standard JSON Schema generated successfully!")
        print(json.dumps(json_schema, indent=2))
        print()
        
        # Generate flexible JSON Schema
        print("🔓 Generating Flexible JSON Schema...")
        objects = generator.parse_ndjson(ndjson_content)
        flexible_schema = generator.generate_flexible_schema(objects)
        print("✅ Flexible JSON Schema generated successfully!")
        print(json.dumps(flexible_schema, indent=2))
        print()
        
        # Generate binary-aware JSON Schema
        print("🔐 Generating Binary-Aware JSON Schema...")
        binary_schema = generator.generate_binary_aware_schema(objects)
        print("✅ Binary-Aware JSON Schema generated successfully!")
        print(json.dumps(binary_schema, indent=2))
        print()
        
        # Generate flexible with types JSON Schema
        print("🎯 Generating Flexible with Types JSON Schema...")
        flexible_with_types_schema = generator.generate_flexible_with_types_schema(objects)
        print("✅ Flexible with Types JSON Schema generated successfully!")
        print(json.dumps(flexible_with_types_schema, indent=2))
        print()
        
        # Generate Pydantic Any type JSON Schema
        print("🐍 Generating Pydantic Any Type JSON Schema...")
        pydantic_any_schema = generator.generate_pydantic_model_with_any(objects)
        print("✅ Pydantic Any Type JSON Schema generated successfully!")
        print(json.dumps(pydantic_any_schema, indent=2))
        print()
        
        # Generate hardened binary JSON Schema
        print("🛡️ Generating Hardened Binary JSON Schema...")
        hardened_binary_schema = generator.generate_hardened_binary_schema(objects)
        print("✅ Hardened Binary JSON Schema generated successfully!")
        print(json.dumps(hardened_binary_schema, indent=2))
        print()
        
        # Generate smart hardened JSON Schema (main route)
        print("🧠 Generating Smart Hardened JSON Schema...")
        smart_schema = generator.generate_smart_hardened_schema(objects)
        print("✅ Smart Hardened JSON Schema generated successfully!")
        print(json.dumps(smart_schema, indent=2))
        print()
        
        # Save schemas to files
        print("💾 Saving schemas to files...")
        
        with open("generated_schema.json", "w") as f:
            json.dump(json_schema, f, indent=2)
        
        with open("flexible_schema.json", "w") as f:
            json.dump(flexible_schema, f, indent=2)
        
        with open("binary_aware_schema.json", "w") as f:
            json.dump(binary_schema, f, indent=2)
            
        with open("flexible_with_types_schema.json", "w") as f:
            json.dump(flexible_with_types_schema, f, indent=2)
            
        with open("pydantic_any_schema.json", "w") as f:
            json.dump(pydantic_any_schema, f, indent=2)
            
        with open("hardened_binary_schema.json", "w") as f:
            json.dump(hardened_binary_schema, f, indent=2)
            
        with open("smart_schema.json", "w") as f:
            json.dump(smart_schema, f, indent=2)
        
        print("✅ Schemas saved to:")
        print("   - generated_schema.json (Standard)")
        print("   - flexible_schema.json (Flexible)")
        print("   - binary_aware_schema.json (Binary-Aware)")
        print("   - flexible_with_types_schema.json (Flexible with Types)")
        print("   - pydantic_any_schema.json (Pydantic Any Type)")
        print("   - hardened_binary_schema.json (Hardened Binary)")
        print("   - smart_schema.json (Smart Hardened - Main Route)")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def test_with_file():
    """Test function with NDJSON file."""
    
    # Create a sample NDJSON file
    sample_data = [
        {
            "id": 1,
            "name": "Product A",
            "price": 99.99,
            "image_data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==",
            "description": "A great product",
            "tags": ["electronics", "gadget"],
            "metadata": {
                "created_at": "2023-01-01T00:00:00Z",
                "category": "electronics",
                "binary_attachment": "U29tZSBiaW5hcnkgZGF0YQ=="
            }
        },
        {
            "id": 2,
            "name": "Product B",
            "price": 149.99,
            "image_data": None,
            "description": "Another great product",
            "tags": ["clothing", "fashion"],
            "metadata": {
                "created_at": "2023-01-02T00:00:00Z",
                "category": "clothing",
                "binary_attachment": "TW9yZSBiaW5hcnkgZGF0YQ=="
            }
        }
    ]
    
    # Write to NDJSON file
    with open("sample_data.ndjson", "w") as f:
        for item in sample_data:
            f.write(json.dumps(item) + "\n")
    
    print("\n📁 Testing with NDJSON file...")
    print("Created sample_data.ndjson with mixed content types")
    
    generator = SchemaGenerator()
    
    try:
        # Generate schema from file
        schema = generator.analyze_ndjson_file("sample_data.ndjson")
        print("✅ Schema generated from file successfully!")
        
        # Save to file
        with open("file_generated_schema.json", "w") as f:
            json.dump(schema, f, indent=2)
        
        print("📁 File schema saved to: file_generated_schema.json")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def test_binary_data_handling():
    """Test function for binary data handling."""
    
    # Create NDJSON with various binary-like content
    binary_ndjson = """{"id": 1, "binary_field": "SGVsbG8gV29ybGQ=", "hex_field": "48656c6c6f20576f726c64", "mixed_field": "regular text"}
{"id": 2, "binary_field": "QmluYXJ5IGRhdGEgZXhhbXBsZQ==", "hex_field": "42696e6172792064617461", "mixed_field": 42}
{"id": 3, "binary_field": "VW5rbm93biBjb250ZW50IHR5cGU=", "hex_field": "556e6b6e6f776e20636f6e74656e74", "mixed_field": {"key": "value"}}"""

    print("\n🔐 Testing Binary Data Handling...")
    
    generator = SchemaGenerator()
    
    try:
        # Generate binary-aware schema
        objects = generator.parse_ndjson(binary_ndjson)
        schema = generator.generate_binary_aware_schema(objects)
        
        # Save to file
        with open("binary_test_schema.json", "w") as f:
            json.dump(schema, f, indent=2)
        
        print("✅ Binary-aware schema generated successfully!")
        print("📁 Binary schema saved to: binary_test_schema.json")
        
        # Decode and print sample binary content for verification
        print("\n🔍 Sample Binary Content Decoded:")
        sample_binary = "SGVsbG8gV29ybGQ="
        decoded = base64.b64decode(sample_binary).decode('utf-8')
        print(f"   Base64: {sample_binary}")
        print(f"   Decoded: {decoded}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
    
    # Uncomment the following lines to test additional features:
    test_with_file()
    test_binary_data_handling()
