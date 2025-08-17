#!/usr/bin/env python3
"""
Test suite for the AutoSchema LLM schema generator.
This file contains unit tests to validate the functionality of the SchemaGenerator class.
"""

import json
import unittest
from unittest.mock import Mock, patch
from schema_generator import SchemaGenerator

class TestSchemaGenerator(unittest.TestCase):
    """Test cases for the SchemaGenerator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sample_data = [
            {
                "id": 1,
                "name": "John Doe",
                "email": "john@example.com",
                "age": 30,
                "is_active": True
            },
            {
                "id": 2,
                "name": "Jane Smith",
                "email": "jane@example.com", 
                "age": 25,
                "is_active": False
            }
        ]
        
        self.expected_json_schema = {
            "$schema": "http://json-schema.org/draft-2020-12/schema#",
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "name": {"type": "string"},
                    "email": {"type": "string", "format": "email"},
                    "age": {"type": "integer", "minimum": 0},
                    "is_active": {"type": "boolean"}
                },
                "required": ["id", "name", "email", "age", "is_active"]
            }
        }
        
        self.expected_pydantic_model = """from pydantic import BaseModel, Field, EmailStr

class User(BaseModel):
    id: int = Field(..., description="Unique identifier")
    name: str = Field(..., description="Full name")
    email: EmailStr = Field(..., description="Email address")
    age: int = Field(..., ge=0, description="Age in years")
    is_active: bool = Field(..., description="Active status")"""
        
        self.expected_sql_schema = """CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    age INTEGER NOT NULL CHECK (age >= 0),
    is_active BOOLEAN NOT NULL
);"""
    
    def test_init(self):
        """Test SchemaGenerator initialization."""
        generator = SchemaGenerator(api_key="test_key")
        self.assertEqual(generator.model, "gpt-4")
        
        generator = SchemaGenerator(api_key="test_key", model="gpt-3.5-turbo")
        self.assertEqual(generator.model, "gpt-3.5-turbo")
    
    def test_empty_data_validation(self):
        """Test that empty data raises ValueError."""
        generator = SchemaGenerator(api_key="test_key")
        with self.assertRaises(ValueError):
            generator.analyze_json_list([])
    
    @patch('schema_generator.OpenAI')
    def test_analyze_json_list_success(self, mock_openai):
        """Test successful JSON schema generation."""
        # Mock OpenAI response
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps(self.expected_json_schema)
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        generator = SchemaGenerator(api_key="test_key")
        result = generator.analyze_json_list(self.sample_data)
        
        self.assertEqual(result, self.expected_json_schema)
        mock_client.chat.completions.create.assert_called_once()
    
    @patch('schema_generator.OpenAI')
    def test_generate_pydantic_model_success(self, mock_openai):
        """Test successful Pydantic model generation."""
        # Mock OpenAI response
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = self.expected_pydantic_model
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        generator = SchemaGenerator(api_key="test_key")
        result = generator.generate_pydantic_model(self.sample_data)
        
        self.assertEqual(result, self.expected_pydantic_model)
        mock_client.chat.completions.create.assert_called_once()
    
    @patch('schema_generator.OpenAI')
    def test_generate_sql_schema_success(self, mock_openai):
        """Test successful SQL schema generation."""
        # Mock OpenAI response
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = self.expected_sql_schema
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        generator = SchemaGenerator(api_key="test_key")
        result = generator.generate_sql_schema(self.sample_data, "users")
        
        self.assertEqual(result, self.expected_sql_schema)
        mock_client.chat.completions.create.assert_called_once()
    
    @patch('schema_generator.OpenAI')
    def test_extract_schema_from_response_with_json_blocks(self, mock_openai):
        """Test schema extraction from response with JSON code blocks."""
        generator = SchemaGenerator(api_key="test_key")
        
        # Test with ```json blocks
        response_with_json_blocks = f"```json\n{json.dumps(self.expected_json_schema)}\n```"
        result = generator._extract_schema_from_response(response_with_json_blocks)
        self.assertEqual(result, self.expected_json_schema)
        
        # Test with regular ``` blocks
        response_with_blocks = f"```\n{json.dumps(self.expected_json_schema)}\n```"
        result = generator._extract_schema_from_response(response_with_blocks)
        self.assertEqual(result, self.expected_json_schema)
        
        # Test with plain JSON
        response_plain = json.dumps(self.expected_json_schema)
        result = generator._extract_schema_from_response(response_plain)
        self.assertEqual(result, self.expected_json_schema)
    
    def test_extract_schema_from_response_invalid_json(self):
        """Test schema extraction with invalid JSON."""
        generator = SchemaGenerator(api_key="test_key")
        
        with self.assertRaises(ValueError):
            generator._extract_schema_from_response("invalid json content")
    
    @patch('jsonschema.validate')
    def test_validate_schema_success(self, mock_validate):
        """Test successful schema validation."""
        generator = SchemaGenerator(api_key="test_key")
        generator._validate_schema(self.expected_json_schema, self.sample_data)
        mock_validate.assert_called()
    
    @patch('jsonschema.validate')
    def test_validate_schema_failure(self, mock_validate):
        """Test schema validation failure."""
        mock_validate.side_effect = Exception("Validation failed")
        
        generator = SchemaGenerator(api_key="test_key")
        with self.assertRaises(ValueError):
            generator._validate_schema(self.expected_json_schema, self.sample_data)
    
    def test_create_schema_prompt(self):
        """Test schema prompt creation."""
        generator = SchemaGenerator(api_key="test_key")
        json_str = json.dumps(self.sample_data, indent=2)
        prompt = generator._create_schema_prompt(json_str)
        
        self.assertIn("JSON Schema", prompt)
        self.assertIn("draft 2020-12", prompt)
        self.assertIn(json_str, prompt)
    
    @patch('schema_generator.OpenAI')
    def test_api_error_handling(self, mock_openai):
        """Test API error handling."""
        # Mock OpenAI to raise an exception
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_openai.return_value = mock_client
        
        generator = SchemaGenerator(api_key="test_key")
        with self.assertRaises(Exception):
            generator.analyze_json_list(self.sample_data)

class TestComplexDataStructures(unittest.TestCase):
    """Test cases for complex data structures."""
    
    def setUp(self):
        """Set up test fixtures for complex data."""
        self.complex_data = [
            {
                "id": 1,
                "user": {
                    "name": "John",
                    "profile": {
                        "bio": "Developer",
                        "skills": ["Python", "JavaScript"]
                    }
                },
                "orders": [
                    {"product_id": "PROD-001", "quantity": 2},
                    {"product_id": "PROD-002", "quantity": 1}
                ],
                "metadata": {
                    "created_at": "2023-01-01T00:00:00Z",
                    "tags": ["vip", "premium"]
                }
            }
        ]
    
    @patch('schema_generator.OpenAI')
    def test_complex_nested_structures(self, mock_openai):
        """Test handling of complex nested structures."""
        # Mock a response that handles nested structures
        mock_schema = {
            "$schema": "http://json-schema.org/draft-2020-12/schema#",
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "user": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "profile": {
                                "type": "object",
                                "properties": {
                                    "bio": {"type": "string"},
                                    "skills": {"type": "array", "items": {"type": "string"}}
                                }
                            }
                        }
                    },
                    "orders": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "product_id": {"type": "string"},
                                "quantity": {"type": "integer"}
                            }
                        }
                    }
                }
            }
        }
        
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps(mock_schema)
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        generator = SchemaGenerator(api_key="test_key")
        result = generator.analyze_json_list(self.complex_data)
        
        self.assertEqual(result, mock_schema)

if __name__ == "__main__":
    # Run the tests
    unittest.main(verbosity=2)
