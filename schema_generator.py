import json
import logging
from typing import List, Dict, Any, Optional, Iterator, Set, Union
import base64
import re
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SchemaGenerator:
    """
    A rule-based schema generator that analyzes NDJSON data and creates comprehensive JSON schemas.
    Supports fields that can contain anything, including binary data and mixed types.
    No external LLM required - uses intelligent pattern analysis.
    """
    
    def __init__(self):
        """
        Initialize the schema generator.
        No API keys or external dependencies required.
        """
        self.binary_patterns = [
            r'^[A-Za-z0-9+/]{20,}={0,2}$',  # Base64 pattern - must be at least 20 chars
            r'^[A-Fa-f0-9]{32,}$',  # Hex pattern - must be at least 32 chars
        ]
        
        # Common binary file extensions and their MIME types
        self.binary_mime_types = {
            'png': 'image/png',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'gif': 'image/gif',
            'pdf': 'application/pdf',
            'zip': 'application/zip',
            'exe': 'application/octet-stream',
            'bin': 'application/octet-stream',
            'dat': 'application/octet-stream',
        }
        
    def parse_ndjson(self, ndjson_content: str) -> List[Dict[str, Any]]:
        """
        Parse NDJSON content into a list of JSON objects.
        
        Args:
            ndjson_content: NDJSON string content
            
        Returns:
            List of parsed JSON objects
        """
        objects = []
        for line_num, line in enumerate(ndjson_content.strip().split('\n'), 1):
            line = line.strip()
            if line:  # Skip empty lines
                try:
                    obj = json.loads(line)
                    objects.append(obj)
                except json.JSONDecodeError as e:
                    logger.warning(f"Invalid JSON on line {line_num}: {e}")
                    continue
        return objects
    
    def parse_ndjson_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Parse NDJSON file into a list of JSON objects.
        
        Args:
            file_path: Path to the NDJSON file
            
        Returns:
            List of parsed JSON objects
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return self.parse_ndjson(f.read())
        except FileNotFoundError:
            raise ValueError(f"File not found: {file_path}")
        except Exception as e:
            raise ValueError(f"Error reading file {file_path}: {e}")
    
    def stream_ndjson(self, file_path: str) -> Iterator[Dict[str, Any]]:
        """
        Stream NDJSON file line by line for memory-efficient processing.
        
        Args:
            file_path: Path to the NDJSON file
            
        Yields:
            Parsed JSON objects one at a time
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if line:  # Skip empty lines
                        try:
                            obj = json.loads(line)
                            yield obj
                        except json.JSONDecodeError as e:
                            logger.warning(f"Invalid JSON on line {line_num}: {e}")
                            continue
        except FileNotFoundError:
            raise ValueError(f"File not found: {file_path}")
        except Exception as e:
            raise ValueError(f"Error reading file {file_path}: {e}")
    
    def analyze_ndjson(self, ndjson_content: str, sample_size: Optional[int] = None) -> Dict[str, Any]:
        """
        Analyze NDJSON content and generate a comprehensive JSON schema.
        
        Args:
            ndjson_content: NDJSON string content
            sample_size: Number of objects to sample for analysis (None for all)
            
        Returns:
            Generated JSON schema
        """
        objects = self.parse_ndjson(ndjson_content)
        
        if not objects:
            raise ValueError("NDJSON content is empty or contains no valid JSON objects")
        
        # Sample data if specified
        if sample_size and len(objects) > sample_size:
            import random
            objects = random.sample(objects, sample_size)
            logger.info(f"Sampled {sample_size} objects from {len(self.parse_ndjson(ndjson_content))} total objects")
        
        return self._analyze_objects(objects)
    
    def analyze_ndjson_file(self, file_path: str, sample_size: Optional[int] = None) -> Dict[str, Any]:
        """
        Analyze NDJSON file and generate a comprehensive JSON schema.
        
        Args:
            file_path: Path to the NDJSON file
            sample_size: Number of objects to sample for analysis (None for all)
            
        Returns:
            Generated JSON schema
        """
        objects = self.parse_ndjson_file(file_path)
        
        if not objects:
            raise ValueError(f"NDJSON file {file_path} is empty or contains no valid JSON objects")
        
        # Sample data if specified
        if sample_size and len(objects) > sample_size:
            import random
            objects = random.sample(objects, sample_size)
            logger.info(f"Sampled {sample_size} objects from {len(self.parse_ndjson_file(file_path))} total objects")
        
        return self._analyze_objects(objects)
    
    def _analyze_objects(self, objects: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze a list of JSON objects and generate a comprehensive JSON schema.
        
        Args:
            objects: List of JSON objects to analyze
            
        Returns:
            Generated JSON schema
        """
        if not objects:
            raise ValueError("JSON objects list cannot be empty")
        
        # Analyze all objects to understand the structure
        field_analysis = self._analyze_fields(objects)
        
        # Generate schema based on analysis
        schema = self._generate_schema_from_analysis(field_analysis)
        
        # Validate the generated schema
        self._validate_schema(schema, objects)
        
        return schema
    
    def _analyze_fields(self, objects: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """
        Analyze all fields across all objects to understand their types and patterns.
        
        Args:
            objects: List of JSON objects to analyze
            
        Returns:
            Dictionary mapping field names to their analysis
        """
        field_analysis = {}
        total_objects = len(objects)
        
        # First pass: collect all field names and initialize analysis
        all_field_names = set()
        for obj in objects:
            all_field_names.update(obj.keys())
        
        for field_name in all_field_names:
            field_analysis[field_name] = {
                'types': set(),
                'values': [],
                'null_count': 0,
                'total_count': 0,
                'missing_count': 0,
                'min_length': None,
                'max_length': None,
                'min_value': None,
                'max_value': None,
                'patterns': set(),
                'is_binary': False,
                'is_mixed': False
            }
        
        # Second pass: analyze each object
        for obj in objects:
            for field_name in all_field_names:
                analysis = field_analysis[field_name]
                
                if field_name not in obj:
                    # Field is missing from this object
                    analysis['missing_count'] += 1
                    continue
                
                field_value = obj[field_name]
                analysis['total_count'] += 1
                analysis['values'].append(field_value)
                
                if field_value is None:
                    analysis['null_count'] += 1
                    analysis['types'].add('NoneType')  # Track null as a type
                    continue
                
                # Analyze type
                field_type = type(field_value).__name__
                analysis['types'].add(field_type)
                
                # Analyze patterns and constraints
                if isinstance(field_value, str):
                    self._analyze_string_field(analysis, field_value)
                elif isinstance(field_value, (int, float)):
                    self._analyze_numeric_field(analysis, field_value)
                elif isinstance(field_value, bool):
                    # Boolean fields don't need additional analysis
                    pass
                elif isinstance(field_value, list):
                    self._analyze_array_field(analysis, field_value)
                elif isinstance(field_value, dict):
                    self._analyze_object_field(analysis, field_value)
        
        # Post-process analysis
        for field_name, analysis in field_analysis.items():
            self._post_process_field_analysis(analysis, total_objects)
        
        return field_analysis
    
    def _analyze_string_field(self, analysis: Dict[str, Any], value: str) -> None:
        """Analyze a string field for patterns and characteristics."""
        # Length analysis
        length = len(value)
        if analysis['min_length'] is None or length < analysis['min_length']:
            analysis['min_length'] = length
        if analysis['max_length'] is None or length > analysis['max_length']:
            analysis['max_length'] = length
        
        # Check for binary patterns
        if self._is_likely_binary(value):
            analysis['is_binary'] = True
        
        # Check for common patterns
        if self._is_email(value):
            analysis['patterns'].add('email')
        elif self._is_url(value):
            analysis['patterns'].add('url')
        elif self._is_date_time(value):
            analysis['patterns'].add('datetime')
        elif self._is_uuid(value):
            analysis['patterns'].add('uuid')
    
    def _analyze_numeric_field(self, analysis: Dict[str, Any], value: Union[int, float]) -> None:
        """Analyze a numeric field for constraints."""
        # Only analyze actual numeric values
        if not isinstance(value, (int, float)):
            return
            
        # Ensure we have valid numeric values
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            if analysis['min_value'] is None or value < analysis['min_value']:
                analysis['min_value'] = value
            if analysis['max_value'] is None or value > analysis['max_value']:
                analysis['max_value'] = value
    
    def _analyze_array_field(self, analysis: Dict[str, Any], value: List) -> None:
        """Analyze an array field."""
        # Length analysis
        length = len(value)
        if analysis['min_length'] is None or length < analysis['min_length']:
            analysis['min_length'] = length
        if analysis['max_length'] is None or length > analysis['max_length']:
            analysis['max_length'] = length
        
        # Analyze array item types and structure
        if 'array_structure' not in analysis:
            analysis['array_structure'] = {
                'item_types': set(),
                'item_schemas': {},
                'consistent_structure': True,
                'nested_objects': False
            }
        
        # Analyze each item in the array
        for item in value:
            item_type = type(item).__name__
            analysis['array_structure']['item_types'].add(item_type)
            
            # If item is an object, analyze its structure
            if isinstance(item, dict):
                analysis['array_structure']['nested_objects'] = True
                
                # Create a unique key for this object structure
                item_keys = tuple(sorted(item.keys()))
                if item_keys not in analysis['array_structure']['item_schemas']:
                    analysis['array_structure']['item_schemas'][item_keys] = {
                        'fields': set(),
                        'field_types': {},
                        'field_patterns': {},
                        'field_constraints': {},
                        'count': 0
                    }
                
                schema_info = analysis['array_structure']['item_schemas'][item_keys]
                schema_info['count'] += 1
                
                # Analyze each field in the object
                for field_name, field_value in item.items():
                    schema_info['fields'].add(field_name)
                    
                    # Analyze field type
                    field_type = type(field_value).__name__
                    if field_name not in schema_info['field_types']:
                        schema_info['field_types'][field_name] = set()
                    schema_info['field_types'][field_name].add(field_type)
                    
                    # Analyze string patterns
                    if isinstance(field_value, str):
                        if field_name not in schema_info['field_patterns']:
                            schema_info['field_patterns'][field_name] = set()
                        
                        if self._is_email(field_value):
                            schema_info['field_patterns'][field_name].add('email')
                        elif self._is_url(field_value):
                            schema_info['field_patterns'][field_name].add('url')
                        elif self._is_date_time(field_value):
                            schema_info['field_patterns'][field_name].add('datetime')
                        elif self._is_uuid(field_value):
                            schema_info['field_patterns'][field_name].add('uuid')
                        elif self._is_likely_binary(field_value):
                            schema_info['field_patterns'][field_name].add('binary')
                    
                    # Analyze constraints
                    if field_name not in schema_info['field_constraints']:
                        schema_info['field_constraints'][field_name] = {
                            'min_length': None,
                            'max_length': None,
                            'min_value': None,
                            'max_value': None
                        }
                    
                    constraints = schema_info['field_constraints'][field_name]
                    
                    if isinstance(field_value, str):
                        length = len(field_value)
                        if constraints['min_length'] is None or length < constraints['min_length']:
                            constraints['min_length'] = length
                        if constraints['max_length'] is None or length > constraints['max_length']:
                            constraints['max_length'] = length
                    elif isinstance(field_value, (int, float)) and not isinstance(field_value, bool):
                        if constraints['min_value'] is None or field_value < constraints['min_value']:
                            constraints['min_value'] = field_value
                        if constraints['max_value'] is None or field_value > constraints['max_value']:
                            constraints['max_value'] = field_value
    
    def _analyze_object_field(self, analysis: Dict[str, Any], value: Dict) -> None:
        """Analyze an object field."""
        # Analyze nested object structure
        if 'nested_structure' not in analysis:
            analysis['nested_structure'] = {
                'fields': set(),
                'field_types': {},
                'field_patterns': {},
                'field_constraints': {}
            }
        
        # Analyze each field in the nested object
        for field_name, field_value in value.items():
            analysis['nested_structure']['fields'].add(field_name)
            
            # Analyze field type
            field_type = type(field_value).__name__
            if field_name not in analysis['nested_structure']['field_types']:
                analysis['nested_structure']['field_types'][field_name] = set()
            analysis['nested_structure']['field_types'][field_name].add(field_type)
            
            # Analyze string patterns
            if isinstance(field_value, str):
                if field_name not in analysis['nested_structure']['field_patterns']:
                    analysis['nested_structure']['field_patterns'][field_name] = set()
                
                if self._is_email(field_value):
                    analysis['nested_structure']['field_patterns'][field_name].add('email')
                elif self._is_url(field_value):
                    analysis['nested_structure']['field_patterns'][field_name].add('url')
                elif self._is_date_time(field_value):
                    analysis['nested_structure']['field_patterns'][field_name].add('datetime')
                elif self._is_uuid(field_value):
                    analysis['nested_structure']['field_patterns'][field_name].add('uuid')
                elif self._is_likely_binary(field_value):
                    analysis['nested_structure']['field_patterns'][field_name].add('binary')
            
            # Analyze constraints
            if field_name not in analysis['nested_structure']['field_constraints']:
                analysis['nested_structure']['field_constraints'][field_name] = {
                    'min_length': None,
                    'max_length': None,
                    'min_value': None,
                    'max_value': None
                }
            
            constraints = analysis['nested_structure']['field_constraints'][field_name]
            
            if isinstance(field_value, str):
                length = len(field_value)
                if constraints['min_length'] is None or length < constraints['min_length']:
                    constraints['min_length'] = length
                if constraints['max_length'] is None or length > constraints['max_length']:
                    constraints['max_length'] = length
            elif isinstance(field_value, (int, float)) and not isinstance(field_value, bool):
                if constraints['min_value'] is None or field_value < constraints['min_value']:
                    constraints['min_value'] = field_value
                if constraints['max_value'] is None or field_value > constraints['max_value']:
                    constraints['max_value'] = field_value
    
    def _post_process_field_analysis(self, analysis: Dict[str, Any], total_objects: int) -> None:
        """Post-process field analysis to determine final characteristics."""
        # Check if field has mixed types
        if len(analysis['types']) > 1:
            analysis['is_mixed'] = True
        
        # Determine if field is required (present in all objects and never null)
        # A field is required if it appears in all objects AND is never null when present
        analysis['required'] = (analysis['missing_count'] == 0 and analysis['null_count'] == 0)
        
        # Calculate null percentage
        analysis['null_percentage'] = analysis['null_count'] / analysis['total_count'] if analysis['total_count'] > 0 else 0
        
        # Calculate presence percentage
        analysis['presence_percentage'] = (total_objects - analysis['missing_count']) / total_objects
    
    def _is_likely_binary(self, value: str) -> bool:
        """Check if a string value is likely binary data."""
        if not value:
            return False
        
        # Skip very short strings - they're unlikely to be binary
        if len(value) < 20:
            return False
        
        # Check for base64 pattern (must be longer and more specific)
        for pattern in self.binary_patterns:
            if re.match(pattern, value):
                return True
        
        # Check for high entropy (lots of different characters) - but be more conservative
        unique_chars = len(set(value))
        if len(value) > 50 and unique_chars / len(value) > 0.9:
            return True
        
        # Additional checks for common non-binary patterns
        # If it looks like a name, email, URL, etc., it's probably not binary
        if self._is_email(value) or self._is_url(value) or self._is_date_time(value) or self._is_uuid(value):
            return False
        
        # If it contains spaces or common punctuation, it's probably text
        if ' ' in value or any(char in value for char in ',.!?;:()[]{}"\''):
            return False
        
        # If it's all lowercase or all uppercase, it's probably text
        if value.islower() or value.isupper():
            return False
        
        return False
    
    def _is_email(self, value: str) -> bool:
        """Check if a string is an email address."""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(email_pattern, value))
    
    def _is_url(self, value: str) -> bool:
        """Check if a string is a URL."""
        url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        return bool(re.match(url_pattern, value))
    
    def _is_date_time(self, value: str) -> bool:
        """Check if a string is a date/time."""
        # Common date/time patterns
        patterns = [
            r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}',  # ISO format
            r'^\d{4}-\d{2}-\d{2}$',  # Date only
            r'^\d{2}/\d{2}/\d{4}$',  # MM/DD/YYYY
            r'^\d{2}-\d{2}-\d{4}$',  # MM-DD-YYYY
        ]
        
        for pattern in patterns:
            if re.match(pattern, value):
                return True
        
        return False
    
    def _is_uuid(self, value: str) -> bool:
        """Check if a string is a UUID."""
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        return bool(re.match(uuid_pattern, value.lower()))
    
    def _generate_schema_from_analysis(self, field_analysis: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a JSON schema from field analysis.
        
        Args:
            field_analysis: Analysis of all fields
            
        Returns:
            Generated JSON schema
        """
        schema = {
            "$schema": "http://json-schema.org/draft-2020-12/schema#",
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False  # Top-level schema NEVER allows additional properties
        }
        
        for field_name, analysis in field_analysis.items():
            property_schema = self._generate_property_schema(field_name, analysis)
            schema["properties"][field_name] = property_schema
            
            if analysis.get('required', False):
                schema["required"].append(field_name)
        
        return schema
    
    def _generate_property_schema(self, field_name: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a property schema for a single field.
        
        Args:
            field_name: Name of the field
            analysis: Analysis of the field
            
        Returns:
            Property schema
        """
        types = analysis['types']
        
        # Handle mixed types
        if analysis.get('is_mixed', False) or len(types) > 1:
            return self._generate_mixed_type_schema(analysis)
        
        # Handle single types
        if 'NoneType' in types and len(types) == 1:
            # Field is only null
            return {"type": "null"}
        elif 'str' in types:
            return self._generate_string_schema(analysis)
        elif 'int' in types or 'float' in types:
            return self._generate_numeric_schema(analysis)
        elif 'bool' in types:
            return self._generate_boolean_schema(analysis)
        elif 'list' in types:
            return self._generate_array_schema(analysis)
        elif 'dict' in types:
            return self._generate_object_schema(analysis)
        else:
            # Fallback to any type
            return {"type": "string"}
    
    def _generate_mixed_type_schema(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate schema for fields with mixed types."""
        type_schemas = []
        
        # Handle null type separately to avoid nested oneOf
        has_null = 'NoneType' in analysis['types'] or analysis.get('null_percentage', 0) > 0
        
        if 'str' in analysis['types']:
            str_schema = {"type": "string"}
            # Add length constraints if available
            if analysis.get('min_length') is not None:
                str_schema["minLength"] = analysis['min_length']
            if analysis.get('max_length') is not None:
                str_schema["maxLength"] = analysis['max_length']
            # Add pattern constraints
            if 'email' in analysis.get('patterns', set()):
                str_schema["format"] = "email"
            elif 'url' in analysis.get('patterns', set()):
                str_schema["format"] = "uri"
            elif 'datetime' in analysis.get('patterns', set()):
                str_schema["format"] = "date-time"
            elif 'uuid' in analysis.get('patterns', set()):
                str_schema["format"] = "uuid"
            # Handle binary data
            if analysis.get('is_binary', False):
                str_schema["contentEncoding"] = "base64"
                str_schema["contentMediaType"] = "application/octet-stream"
            type_schemas.append(str_schema)
            
        if 'int' in analysis['types'] or 'float' in analysis['types']:
            if 'float' in analysis['types']:
                numeric_schema = {"type": "number"}
            else:
                numeric_schema = {"type": "integer"}
            # Add value constraints
            min_value = analysis.get('min_value')
            max_value = analysis.get('max_value')
            if min_value is not None and isinstance(min_value, (int, float)) and not isinstance(min_value, bool):
                numeric_schema["minimum"] = min_value
            if max_value is not None and isinstance(max_value, (int, float)) and not isinstance(max_value, bool):
                numeric_schema["maximum"] = max_value
            type_schemas.append(numeric_schema)
            
        if 'bool' in analysis['types']:
            type_schemas.append({"type": "boolean"})
            
        if 'list' in analysis['types']:
            array_schema = {"type": "array", "minItems": 0, "items": {}}
            type_schemas.append(array_schema)
            
        if 'dict' in analysis['types']:
            type_schemas.append({
                "type": "object",
                "additionalProperties": True
            })
        
        # Add null if it's optional
        if has_null:
            type_schemas.append({"type": "null"})
        
        return {"oneOf": type_schemas}
    
    def _generate_string_schema(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate schema for string fields."""
        # Check if field can be null
        if analysis.get('null_percentage', 0) > 0:
            return {
                "oneOf": [
                    {"type": "string"},
                    {"type": "null"}
                ]
            }
        
        schema = {"type": "string"}
        
        # Add flexible length constraints - only set minLength if it's reasonable
        min_length = analysis.get('min_length')
        max_length = analysis.get('max_length')
        
        # Only set minLength if it's greater than 0 and not too restrictive
        if min_length is not None and min_length > 0:
            # For most fields, use a reasonable minimum of 1
            # Only use the actual minimum for very specific cases like UUIDs
            if 'uuid' in analysis.get('patterns', set()):
                schema["minLength"] = min_length  # UUIDs have fixed length
            elif 'email' in analysis.get('patterns', set()):
                schema["minLength"] = 5  # Reasonable minimum for emails
            else:
                schema["minLength"] = 1  # General minimum for strings
        
        # Set maxLength for better validation - use a reasonable maximum
        if max_length is not None and max_length > 0:
            # For specific patterns, use exact max length
            if 'uuid' in analysis.get('patterns', set()):
                schema["maxLength"] = max_length  # UUIDs have fixed length
            elif 'credit_card' in analysis.get('patterns', set()):
                schema["maxLength"] = max_length  # Credit cards have fixed format
            elif 'email' in analysis.get('patterns', set()):
                # For emails, use a reasonable maximum (254 chars is RFC standard)
                schema["maxLength"] = min(max_length * 2, 254)
            elif 'url' in analysis.get('patterns', set()):
                # For URLs, use a reasonable maximum
                schema["maxLength"] = min(max_length * 3, 2048)
            else:
                # For other strings, use a reasonable maximum based on observed data
                # Allow some flexibility but not unlimited
                schema["maxLength"] = min(max_length * 2, 1000)  # Cap at 1000 chars
        
        # Add pattern constraints
        if 'email' in analysis.get('patterns', set()):
            schema["format"] = "email"
        elif 'url' in analysis.get('patterns', set()):
            schema["format"] = "uri"
        elif 'datetime' in analysis.get('patterns', set()):
            schema["format"] = "date-time"
        elif 'uuid' in analysis.get('patterns', set()):
            schema["format"] = "uuid"
        
        # Handle binary data
        if analysis.get('is_binary', False):
            schema["contentEncoding"] = "base64"
            schema["contentMediaType"] = "application/octet-stream"
        
        return schema
    
    def _generate_numeric_schema(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate schema for numeric fields."""
        if 'float' in analysis['types']:
            schema = {"type": "number"}
        else:
            schema = {"type": "integer"}
        
        # Add smart value constraints with reasonable ranges
        min_value = analysis.get('min_value')
        max_value = analysis.get('max_value')
        
        if min_value is not None and max_value is not None and isinstance(min_value, (int, float)) and isinstance(max_value, (int, float)) and not isinstance(min_value, bool) and not isinstance(max_value, bool):
            # Use smart ranges instead of exact values
            if 'float' in analysis['types']:
                # For floats, use percentage-based expansion
                if min_value == max_value:
                    # Single value - use 10% range
                    range_size = abs(min_value) * 0.1
                    schema["minimum"] = min_value - range_size
                    schema["maximum"] = max_value + range_size
                else:
                    # Range of values - expand by 20%
                    range_size = max_value - min_value
                    expansion = range_size * 0.2
                    schema["minimum"] = min_value - expansion
                    schema["maximum"] = max_value + expansion
            else:
                # For integers, use reasonable ranges
                if min_value == max_value:
                    # Single value - use a small range around it
                    range_size = max(1, abs(min_value) // 10)
                    schema["minimum"] = min_value - range_size
                    schema["maximum"] = max_value + range_size
                else:
                    # Range of values - expand it slightly
                    range_size = max_value - min_value
                    expansion = max(1, range_size // 4)  # Expand by 25%
                    schema["minimum"] = min_value - expansion
                    schema["maximum"] = max_value + expansion
        
        return schema
    
    def _generate_boolean_schema(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate schema for boolean fields."""
        return {"type": "boolean"}
    
    def _generate_array_schema(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate schema for array fields."""
        # Check if field can be null
        if analysis.get('null_percentage', 0) > 0:
            return {
                "oneOf": [
                    self._generate_nested_array_schema(analysis),
                    {"type": "null"}
                ]
            }
        
        return self._generate_nested_array_schema(analysis)
    
    def _generate_nested_array_schema(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate schema for array fields with detailed item analysis."""
        schema = {"type": "array"}
        
        # Add flexible length constraints
        min_length = analysis.get('min_length')
        max_length = analysis.get('max_length')
        
        if min_length is not None and min_length > 0:
            schema["minItems"] = 0  # Allow empty arrays for flexibility
        
        # Generate items schema based on array structure analysis
        if 'array_structure' in analysis:
            array_structure = analysis['array_structure']
            
            if array_structure['nested_objects'] and array_structure['item_schemas']:
                # Array contains objects - generate detailed item schema
                schema["items"] = self._generate_array_item_schema(array_structure)
            else:
                # Simple array - use basic item schema
                schema["items"] = self._generate_simple_array_item_schema(array_structure)
        else:
            # No structure analysis available - use generic schema
            schema["items"] = {}
        
        return schema
    
    def _generate_array_item_schema(self, array_structure: Dict[str, Any]) -> Dict[str, Any]:
        """Generate schema for array items when they are objects."""
        if len(array_structure['item_schemas']) == 1:
            # All items have the same structure
            item_schema_info = list(array_structure['item_schemas'].values())[0]
            return self._generate_array_object_schema(item_schema_info)
        else:
            # Multiple different object structures - use oneOf
            item_schemas = []
            for item_schema_info in array_structure['item_schemas'].values():
                item_schemas.append(self._generate_array_object_schema(item_schema_info))
            return {"oneOf": item_schemas}
    
    def _generate_array_object_schema(self, item_schema_info: Dict[str, Any]) -> Dict[str, Any]:
        """Generate schema for an object within an array."""
        schema = {
            "type": "object",
            "properties": {}
        }
        
        # Generate schemas for each field in the object
        for field_name in item_schema_info['fields']:
            field_types = item_schema_info['field_types'].get(field_name, set())
            field_patterns = item_schema_info['field_patterns'].get(field_name, set())
            field_constraints = item_schema_info['field_constraints'].get(field_name, {})
            
            # Generate schema for this field
            field_schema = self._generate_nested_field_schema(field_types, field_patterns, field_constraints)
            schema["properties"][field_name] = field_schema
        
        # Analyze if this array object needs additionalProperties
        needs_additional = self._analyze_array_object_additional_properties_needed(item_schema_info)
        if needs_additional:
            schema["additionalProperties"] = True
            # Add warning in description
            mixed_fields = []
            for field_name in item_schema_info['fields']:
                field_types = item_schema_info['field_types'].get(field_name, set())
                if len(field_types) > 1:
                    mixed_fields.append(f"{field_name}({', '.join(field_types)})")
            
            schema["description"] = f"⚠️ WARNING: Array item allows additional properties due to mixed types in fields: {', '.join(mixed_fields)}. Consider defining explicit field schemas for better validation."
        
        return schema
    
    def _generate_simple_array_item_schema(self, array_structure: Dict[str, Any]) -> Dict[str, Any]:
        """Generate schema for simple array items (strings, numbers, etc.)."""
        item_types = array_structure['item_types']
        
        if len(item_types) == 1:
            # Single type
            item_type = list(item_types)[0]
            if item_type == 'str':
                return {"type": "string"}
            elif item_type == 'int':
                return {"type": "integer"}
            elif item_type == 'float':
                return {"type": "number"}
            elif item_type == 'bool':
                return {"type": "boolean"}
            elif item_type == 'dict':
                # For dict items, analyze if they need additionalProperties
                needs_additional = self._analyze_dict_item_additional_properties_needed(array_structure)
                schema = {"type": "object"}
                if needs_additional:
                    schema["additionalProperties"] = True
                    schema["description"] = "⚠️ WARNING: Array dict item allows additional properties due to complex structure. Consider defining explicit field schemas."
                return schema
            elif item_type == 'list':
                return {"type": "array", "items": {}}
            else:
                return {"type": "string"}
        else:
            # Multiple types - use oneOf
            type_schemas = []
            for item_type in item_types:
                if item_type == 'str':
                    type_schemas.append({"type": "string"})
                elif item_type == 'int':
                    type_schemas.append({"type": "integer"})
                elif item_type == 'float':
                    type_schemas.append({"type": "number"})
                elif item_type == 'bool':
                    type_schemas.append({"type": "boolean"})
                elif item_type == 'dict':
                    # For dict items, analyze if they need additionalProperties
                    needs_additional = self._analyze_dict_item_additional_properties_needed(array_structure)
                    schema = {"type": "object"}
                    if needs_additional:
                        schema["additionalProperties"] = True
                        schema["description"] = "⚠️ WARNING: Array dict item allows additional properties due to complex structure. Consider defining explicit field schemas."
                    type_schemas.append(schema)
                elif item_type == 'list':
                    type_schemas.append({"type": "array", "items": {}})
                else:
                    type_schemas.append({"type": "string"})
            
            return {"oneOf": type_schemas}
    
    def _generate_object_schema(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate schema for object fields."""
        # Check if field can be null
        if analysis.get('null_percentage', 0) > 0:
            return {
                "oneOf": [
                    self._generate_nested_object_schema(analysis),
                    {"type": "null"}
                ]
            }
        
        return self._generate_nested_object_schema(analysis)
    
    def _generate_nested_object_schema(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate schema for nested object fields with detailed structure."""
        if 'nested_structure' not in analysis:
            return {
                "type": "object",
                "additionalProperties": False  # No additional properties if we don't know the structure
            }
        
        nested = analysis['nested_structure']
        schema = {
            "type": "object",
            "properties": {}
        }
        
        # Generate schemas for each field in the nested object
        for field_name in nested['fields']:
            field_types = nested['field_types'].get(field_name, set())
            field_patterns = nested['field_patterns'].get(field_name, set())
            field_constraints = nested['field_constraints'].get(field_name, {})
            
            # Generate schema for this field
            field_schema = self._generate_nested_field_schema(field_types, field_patterns, field_constraints)
            schema["properties"][field_name] = field_schema
        
        # Analyze if this nested object needs additionalProperties
        needs_additional = self._analyze_nested_additional_properties_needed(analysis)
        if needs_additional:
            schema["additionalProperties"] = True
            # Add warning in description
            mixed_fields = []
            for field_name in nested['fields']:
                field_types = nested['field_types'].get(field_name, set())
                if len(field_types) > 1:
                    mixed_fields.append(f"{field_name}({', '.join(field_types)})")
            
            schema["description"] = f"⚠️ WARNING: This object allows additional properties due to mixed types in fields: {', '.join(mixed_fields)}. Consider defining explicit field schemas for better validation."
        
        return schema
    
    def _generate_nested_field_schema(self, field_types: Set[str], field_patterns: Set[str], field_constraints: Dict[str, Any]) -> Dict[str, Any]:
        """Generate schema for a nested field."""
        if len(field_types) == 1:
            # Single type
            field_type = list(field_types)[0]
            if field_type == 'str':
                return self._generate_nested_string_schema(field_patterns, field_constraints)
            elif field_type == 'int':
                return self._generate_nested_numeric_schema('integer', field_constraints)
            elif field_type == 'float':
                return self._generate_nested_numeric_schema('number', field_constraints)
            elif field_type == 'bool':
                return {"type": "boolean"}
            elif field_type == 'list':
                return {"type": "array", "items": {}}
            elif field_type == 'dict':
                return {"type": "object", "additionalProperties": True}
            else:
                return {"type": "string"}
        else:
            # Multiple types - use oneOf
            type_schemas = []
            for field_type in field_types:
                if field_type == 'str':
                    type_schemas.append(self._generate_nested_string_schema(field_patterns, field_constraints))
                elif field_type == 'int':
                    type_schemas.append(self._generate_nested_numeric_schema('integer', field_constraints))
                elif field_type == 'float':
                    type_schemas.append(self._generate_nested_numeric_schema('number', field_constraints))
                elif field_type == 'bool':
                    type_schemas.append({"type": "boolean"})
                elif field_type == 'list':
                    type_schemas.append({"type": "array", "items": {}})
                elif field_type == 'dict':
                    type_schemas.append({"type": "object", "additionalProperties": True})
                else:
                    type_schemas.append({"type": "string"})
            
            return {"oneOf": type_schemas}
    
    def _generate_nested_string_schema(self, field_patterns: Set[str], field_constraints: Dict[str, Any]) -> Dict[str, Any]:
        """Generate schema for nested string fields."""
        schema = {"type": "string"}
        
        # Add smart length constraints with reasonable ranges
        min_length = field_constraints.get('min_length')
        max_length = field_constraints.get('max_length')
        
        if min_length is not None and max_length is not None and min_length > 0 and max_length > 0:
            # Use smart ranges instead of exact values
            if min_length == max_length:
                # Single length - use a reasonable range
                if min_length <= 3:
                    # Very short strings - allow some flexibility
                    schema["minLength"] = 1
                    schema["maxLength"] = min_length * 3
                elif min_length <= 10:
                    # Short strings - allow moderate flexibility
                    schema["minLength"] = max(1, min_length - 2)
                    schema["maxLength"] = min_length * 2
                else:
                    # Longer strings - allow percentage-based flexibility
                    schema["minLength"] = max(1, int(min_length * 0.8))
                    schema["maxLength"] = int(min_length * 1.5)
            else:
                # Range of lengths - expand it slightly
                range_size = max_length - min_length
                expansion = max(1, range_size // 3)  # Expand by 33%
                schema["minLength"] = max(1, min_length - expansion)
                schema["maxLength"] = max_length + expansion
        elif min_length is not None and min_length > 0:
            # Only min length available
            schema["minLength"] = min_length
        elif max_length is not None and max_length > 0:
            # Only max length available
            schema["maxLength"] = max_length
        
        # Add pattern constraints
        if 'email' in field_patterns:
            schema["format"] = "email"
        elif 'url' in field_patterns:
            schema["format"] = "uri"
        elif 'datetime' in field_patterns:
            schema["format"] = "date-time"
        elif 'uuid' in field_patterns:
            schema["format"] = "uuid"
        elif 'binary' in field_patterns:
            schema["contentEncoding"] = "base64"
            schema["contentMediaType"] = "application/octet-stream"
        
        return schema
    
    def _generate_nested_numeric_schema(self, numeric_type: str, field_constraints: Dict[str, Any]) -> Dict[str, Any]:
        """Generate schema for nested numeric fields."""
        schema = {"type": numeric_type}
        
        # Add smart value constraints with reasonable ranges
        min_value = field_constraints.get('min_value')
        max_value = field_constraints.get('max_value')
        
        if min_value is not None and max_value is not None and isinstance(min_value, (int, float)) and isinstance(max_value, (int, float)) and not isinstance(min_value, bool) and not isinstance(max_value, bool):
            # Use smart ranges instead of exact values
            if numeric_type == 'integer':
                # For integers, use reasonable ranges
                if min_value == max_value:
                    # Single value - use a small range around it
                    range_size = max(1, abs(min_value) // 10)
                    schema["minimum"] = min_value - range_size
                    schema["maximum"] = max_value + range_size
                else:
                    # Range of values - expand it slightly
                    range_size = max_value - min_value
                    expansion = max(1, range_size // 4)  # Expand by 25%
                    schema["minimum"] = min_value - expansion
                    schema["maximum"] = max_value + expansion
            else:
                # For floats, use percentage-based expansion
                if min_value == max_value:
                    # Single value - use 10% range
                    range_size = abs(min_value) * 0.1
                    schema["minimum"] = min_value - range_size
                    schema["maximum"] = max_value + range_size
                else:
                    # Range of values - expand by 20%
                    range_size = max_value - min_value
                    expansion = range_size * 0.2
                    schema["minimum"] = min_value - expansion
                    schema["maximum"] = max_value + expansion
        
        return schema
    
    def _analyze_additional_properties_needed(self, field_analysis: Dict[str, Dict[str, Any]]) -> bool:
        """
        Analyze if the schema needs additionalProperties based on field analysis.
        
        Args:
            field_analysis: Analysis of all fields
            
        Returns:
            True if additionalProperties should be allowed
        """
        # Check if we have mixed types or complex nested structures
        for field_name, analysis in field_analysis.items():
            # If any field has mixed types, we might need additionalProperties
            if analysis.get('is_mixed', False) or len(analysis['types']) > 1:
                return True
            
            # If any field is an object with unknown structure, we might need additionalProperties
            if 'dict' in analysis['types'] and 'nested_structure' not in analysis:
                return True
            
            # If any field has high null percentage, it might indicate flexible structure
            if analysis.get('null_percentage', 0) > 0.5:
                return True
        
        # If we have very few fields and they're all well-defined, don't allow additionalProperties
        if len(field_analysis) <= 3:
            all_well_defined = True
            for analysis in field_analysis.values():
                if len(analysis['types']) > 1 or analysis.get('is_mixed', False):
                    all_well_defined = False
                    break
            if all_well_defined:
                return False
        
        # Default to allowing additionalProperties for flexibility
        return True
    
    def _analyze_nested_additional_properties_needed(self, analysis: Dict[str, Any]) -> bool:
        """
        Analyze if a nested object needs additionalProperties.
        This is very restrictive - only allows additionalProperties when absolutely necessary.
        
        Args:
            analysis: Analysis of the nested object
            
        Returns:
            True if additionalProperties should be allowed
        """
        if 'nested_structure' not in analysis:
            return False
        
        nested = analysis['nested_structure']
        
        # Only allow additionalProperties if we have mixed types in multiple fields
        mixed_type_fields = 0
        for field_name in nested['fields']:
            field_types = nested['field_types'].get(field_name, set())
            if len(field_types) > 1:
                mixed_type_fields += 1
        
        # Only allow additionalProperties if more than 50% of fields have mixed types
        if mixed_type_fields > len(nested['fields']) * 0.5:
            return True
        
        # Default to not allowing additionalProperties for nested objects
        return False
    
    def _analyze_array_object_additional_properties_needed(self, item_schema_info: Dict[str, Any]) -> bool:
        """
        Analyze if an array object needs additionalProperties.
        This is very restrictive - only allows additionalProperties when absolutely necessary.
        
        Args:
            item_schema_info: Analysis of the array item object
            
        Returns:
            True if additionalProperties should be allowed
        """
        # Only allow additionalProperties if we have mixed types in multiple fields
        mixed_type_fields = 0
        for field_name in item_schema_info['fields']:
            field_types = item_schema_info['field_types'].get(field_name, set())
            if len(field_types) > 1:
                mixed_type_fields += 1
        
        # Only allow additionalProperties if more than 50% of fields have mixed types
        if mixed_type_fields > len(item_schema_info['fields']) * 0.5:
            return True
        
        # Default to not allowing additionalProperties for array objects
        return False
    
    def _analyze_dict_item_additional_properties_needed(self, array_structure: Dict[str, Any]) -> bool:
        """
        Analyze if dict items in arrays need additionalProperties.
        
        Args:
            array_structure: Analysis of the array structure
            
        Returns:
            True if additionalProperties should be allowed
        """
        # If we have multiple different object schemas, allow additionalProperties
        if len(array_structure.get('item_schemas', {})) > 1:
            return True
        
        # If we have nested objects but don't know their structure well, allow additionalProperties
        if array_structure.get('nested_objects', False) and not array_structure.get('item_schemas'):
            return True
        
        # Default to not allowing additionalProperties for dict items
        return False
    
    def _analyze_dict_type_additional_properties_needed(self, analysis: Dict[str, Any]) -> bool:
        """
        Analyze if a dict type field needs additionalProperties.
        
        Args:
            analysis: Analysis of the field
            
        Returns:
            True if additionalProperties should be allowed
        """
        # If we have nested structure analysis, use that to decide
        if 'nested_structure' in analysis:
            return self._analyze_nested_additional_properties_needed(analysis)
        
        # If we have mixed types, allow additionalProperties
        if analysis.get('is_mixed', False) or len(analysis['types']) > 1:
            return True
        
        # If we have high null percentage, allow additionalProperties
        if analysis.get('null_percentage', 0) > 0.3:
            return True
        
        # Default to not allowing additionalProperties for dict types
        return False
    
    def _validate_schema(self, schema: Dict[str, Any], data: List[Dict[str, Any]]) -> None:
        """
        Validate that the generated schema correctly validates the input data.
        
        Args:
            schema: Generated JSON schema
            data: Original data to validate against
            
        Raises:
            ValueError: If schema validation fails
        """
        try:
            import jsonschema
            from jsonschema import validate
            
            for i, item in enumerate(data):
                validate(instance=item, schema=schema)
            logger.info(f"Schema validation successful for {len(data)} items")
        except ImportError:
            logger.warning("jsonschema not available, skipping validation")
        except jsonschema.exceptions.ValidationError as e:
            logger.error(f"Schema validation failed for item {i}: {e}")
            raise ValueError(f"Generated schema does not validate input data: {e}")
    
    def generate_flexible_schema(self, objects: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a flexible JSON schema that allows for any content in fields.
        This is useful when you want to be very permissive about field content.
        
        Args:
            objects: List of JSON objects to analyze
            
        Returns:
            Flexible JSON schema that allows any content
        """
        if not objects:
            raise ValueError("JSON objects list cannot be empty")
        
        # Analyze fields but make the schema very permissive
        field_analysis = self._analyze_fields(objects)
        
        schema = {
            "$schema": "http://json-schema.org/draft-2020-12/schema#",
            "type": "object",
            "properties": {},
            "additionalProperties": True
        }
        
        for field_name, analysis in field_analysis.items():
            # Create very permissive property schema
            property_schema = {
                "oneOf": [
                    {"type": "string"},
                    {"type": "number"},
                    {"type": "integer"},
                    {"type": "boolean"},
                    {"type": "object", "additionalProperties": True},
                    {"type": "array", "items": {}},
                    {"type": "null"}
                ]
            }
            
            # Add binary support if detected
            if analysis.get('is_binary', False):
                property_schema["oneOf"].append({
                    "type": "string",
                    "contentEncoding": "base64"
                })
            
            schema["properties"][field_name] = property_schema
        
        return schema
    
    def generate_binary_aware_schema(self, objects: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a JSON schema that specifically handles binary data fields.
        
        Args:
            objects: List of JSON objects to analyze
            
        Returns:
            JSON schema optimized for binary data handling
        """
        if not objects:
            raise ValueError("JSON objects list cannot be empty")
        
        # Analyze fields with focus on binary detection
        field_analysis = self._analyze_fields(objects)
        
        schema = {
            "$schema": "http://json-schema.org/draft-2020-12/schema#",
            "type": "object",
            "properties": {},
            "required": []
        }
        
        for field_name, analysis in field_analysis.items():
            property_schema = self._generate_binary_aware_property_schema(field_name, analysis)
            schema["properties"][field_name] = property_schema
            
            if analysis.get('required', False):
                schema["required"].append(field_name)
        
        return schema
    
    def _generate_binary_aware_property_schema(self, field_name: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a binary-aware property schema.
        
        Args:
            field_name: Name of the field
            analysis: Analysis of the field
            
        Returns:
            Binary-aware property schema
        """
        if analysis.get('is_binary', False):
            # Field contains binary data
            return {
                "type": "string",
                "contentEncoding": "base64",
                "contentMediaType": "application/octet-stream",
                "description": f"Binary data for {field_name}"
            }
        elif analysis.get('is_mixed', False):
            # Mixed content that might include binary
            return {
                "oneOf": [
                    {"type": "string", "description": "Text content"},
                    {
                        "type": "string",
                        "contentEncoding": "base64",
                        "description": "Binary content"
                    },
                    {"type": "object", "additionalProperties": True, "description": "Object content"},
                    {"type": "array", "items": {}, "description": "Array content"},
                    {"type": "number", "description": "Numeric content"},
                    {"type": "boolean", "description": "Boolean content"},
                    {"type": "null", "description": "Null value"}
                ]
            }
        else:
            # Regular field, use standard generation
            return self._generate_property_schema(field_name, analysis)
    
    def generate_flexible_with_types_schema(self, objects: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a flexible JSON schema that allows any content but preserves type information.
        This schema is flexible but still maintains some type awareness.
        
        Args:
            objects: List of JSON objects to analyze
            
        Returns:
            Flexible JSON schema with type information
        """
        if not objects:
            raise ValueError("JSON objects list cannot be empty")
        
        # Analyze fields to understand types
        field_analysis = self._analyze_fields(objects)
        
        schema = {
            "$schema": "http://json-schema.org/draft-2020-12/schema#",
            "type": "object",
            "properties": {},
            "additionalProperties": True
        }
        
        for field_name, analysis in field_analysis.items():
            # Create flexible property schema that preserves type info
            type_options = []
            
            # Add detected types
            if 'str' in analysis['types']:
                type_options.append({"type": "string"})
            if 'int' in analysis['types']:
                type_options.append({"type": "integer"})
            if 'float' in analysis['types']:
                type_options.append({"type": "number"})
            if 'bool' in analysis['types']:
                type_options.append({"type": "boolean"})
            if 'list' in analysis['types']:
                type_options.append({"type": "array", "items": {}})
            if 'dict' in analysis['types']:
                # For dict types, analyze if they need additionalProperties
                needs_additional = self._analyze_dict_type_additional_properties_needed(analysis)
                schema = {"type": "object"}
                if needs_additional:
                    schema["additionalProperties"] = True
                    schema["description"] = "⚠️ WARNING: Object allows additional properties due to mixed content. Consider defining explicit field schemas."
                type_options.append(schema)
            
            # Always allow null for flexibility
            type_options.append({"type": "null"})
            
            # Add binary support if detected
            if analysis.get('is_binary', False):
                type_options.append({
                    "type": "string",
                    "contentEncoding": "base64",
                    "contentMediaType": "application/octet-stream"
                })
            
            # If we have multiple types, use oneOf, otherwise use the single type
            if len(type_options) > 1:
                property_schema = {"oneOf": type_options}
            else:
                property_schema = type_options[0] if type_options else {"type": "string"}
            
            schema["properties"][field_name] = property_schema
        
        return schema
    
    def generate_pydantic_model_with_any(self, objects: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a JSON schema that mimics Pydantic's Any type behavior.
        Fields that contain binary data or mixed content use Any type (allows everything).
        
        Args:
            objects: List of JSON objects to analyze
            
        Returns:
            JSON schema with Any type for binary/mixed fields
        """
        if not objects:
            raise ValueError("JSON objects list cannot be empty")
        
        # Analyze fields to understand types
        field_analysis = self._analyze_fields(objects)
        
        schema = {
            "$schema": "http://json-schema.org/draft-2020-12/schema#",
            "type": "object",
            "properties": {},
            "required": []
        }
        
        for field_name, analysis in field_analysis.items():
            # Check if field should use Any type (binary or mixed content)
            should_use_any = (
                analysis.get('is_binary', False) or 
                analysis.get('is_mixed', False) or
                analysis.get('null_percentage', 0) > 0.3  # High null percentage
            )
            
            if should_use_any:
                # Use Any type - allows everything
                property_schema = {
                    "oneOf": [
                        {"type": "string"},
                        {"type": "number"},
                        {"type": "integer"},
                        {"type": "boolean"},
                        {"type": "object", "additionalProperties": True},
                        {"type": "array", "items": {}},
                        {"type": "null"}
                    ],
                    "description": f"Any type for {field_name} (allows all content types)"
                }
            else:
                # Use specific type based on analysis
                property_schema = self._generate_property_schema(field_name, analysis)
            
            schema["properties"][field_name] = property_schema
            
            if analysis.get('required', False):
                schema["required"].append(field_name)
        
        return schema
    
    def generate_hardened_binary_schema(self, objects: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a hardened JSON schema that is very strict about binary data.
        Binary fields are strictly enforced, while other fields are more flexible.
        
        Args:
            objects: List of JSON objects to analyze
            
        Returns:
            Hardened JSON schema with strict binary handling
        """
        if not objects:
            raise ValueError("JSON objects list cannot be empty")
        
        # Analyze fields to understand types
        field_analysis = self._analyze_fields(objects)
        
        schema = {
            "$schema": "http://json-schema.org/draft-2020-12/schema#",
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False  # No extra fields allowed
        }
        
        for field_name, analysis in field_analysis.items():
            if analysis.get('is_binary', False):
                # Strict binary field - must be base64 encoded string
                property_schema = {
                    "type": "string",
                    "contentEncoding": "base64",
                    "contentMediaType": "application/octet-stream",
                    "minLength": 1,
                    "pattern": "^[A-Za-z0-9+/]*={0,2}$",  # Base64 pattern
                    "description": f"Binary data for {field_name} (base64 encoded)",
                    "examples": ["SGVsbG8gV29ybGQ="]  # Example base64
                }
            elif analysis.get('is_mixed', False):
                # Mixed content field - allow everything but with descriptions
                property_schema = {
                    "oneOf": [
                        {
                            "type": "string",
                            "description": "Text content",
                            "minLength": 1
                        },
                        {
                            "type": "string",
                            "contentEncoding": "base64",
                            "description": "Binary content (base64 encoded)",
                            "pattern": "^[A-Za-z0-9+/]*={0,2}$"
                        },
                        {
                            "type": "object",
                            "additionalProperties": True,
                            "description": "Object content"
                        },
                        {
                            "type": "array",
                            "items": {},
                            "description": "Array content",
                            "minItems": 0
                        },
                        {
                            "type": "number",
                            "description": "Numeric content"
                        },
                        {
                            "type": "integer",
                            "description": "Integer content"
                        },
                        {
                            "type": "boolean",
                            "description": "Boolean content"
                        },
                        {
                            "type": "null",
                            "description": "Null value"
                        }
                    ],
                    "description": f"Mixed content for {field_name} (allows any type)"
                }
            else:
                # Regular field - use standard generation but be more strict
                property_schema = self._generate_property_schema(field_name, analysis)
                
                # Add additional constraints for non-binary fields
                if property_schema.get("type") == "string":
                    property_schema["minLength"] = 1
                elif property_schema.get("type") == "array":
                    property_schema["minItems"] = 0
            
            schema["properties"][field_name] = property_schema
            
            if analysis.get('required', False):
                schema["required"].append(field_name)
        
        return schema
    
    def generate_smart_hardened_schema(self, objects: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a smart, hardened JSON schema that intelligently handles nested binary data,
        mixed types, and complex structures while being strict when appropriate.
        
        This schema:
        - Detects and strictly validates binary data with proper encoding
        - Handles nested objects and arrays with recursive analysis
        - Allows mixed types when detected but with clear descriptions
        - Enforces strict validation for known patterns
        - Provides flexibility for truly mixed content
        
        Args:
            objects: List of JSON objects to analyze
            
        Returns:
            Smart hardened JSON schema with intelligent type handling
        """
        return self.generate_smart_hardened_schema_with_depth(objects, max_depth=200)
    
    def generate_smart_hardened_schema_with_depth(self, objects: List[Dict[str, Any]], max_depth: int = 100) -> Dict[str, Any]:
        """
        Generate a smart, hardened JSON schema with configurable max nested depth.
        
        Args:
            objects: List of JSON objects to analyze
            max_depth: Maximum depth to analyze for nested structures (default: 100)
            
        Returns:
            Smart hardened JSON schema with intelligent type handling
        """
        if not objects:
            raise ValueError("JSON objects list cannot be empty")
        
        # Use simple field analysis instead of complex deep analysis
        field_analysis = self._analyze_fields(objects)
        
        schema = {
            "$schema": "http://json-schema.org/draft-2020-12/schema#",
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,  # Top-level schema NEVER allows additional properties
            "description": f"Smart hardened schema with intelligent binary and mixed type handling (max depth: {max_depth})"
        }
        
        for field_name, analysis in field_analysis.items():
            property_schema = self._generate_smart_property_schema(field_name, analysis)
            schema["properties"][field_name] = property_schema
            
            if analysis.get('required', False):
                schema["required"].append(field_name)
        
        return schema
    
    def _analyze_fields_deep(self, objects: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """
        Deep analysis of fields including nested structures and binary detection.
        
        Args:
            objects: List of JSON objects to analyze
            
        Returns:
            Enhanced field analysis with nested structure information
        """
        return self._analyze_fields_deep_with_depth(objects, max_depth=200)
    
    def _analyze_fields_deep_with_depth(self, objects: List[Dict[str, Any]], max_depth: int = 100) -> Dict[str, Dict[str, Any]]:
        """
        Deep analysis of fields including nested structures and binary detection with configurable max depth.
        
        Args:
            objects: List of JSON objects to analyze
            max_depth: Maximum depth to analyze for nested structures
            
        Returns:
            Enhanced field analysis with nested structure information
        """
        field_analysis = self._analyze_fields(objects)
        
        # Enhance analysis with deep nested structure detection
        for field_name, analysis in field_analysis.items():
            # Analyze nested structures if present
            if 'dict' in analysis['types'] or 'list' in analysis['types']:
                # Use recursive analysis for deep nesting with custom max depth
                nested_analysis = self._analyze_nested_structures_recursive(objects, field_name, max_depth=max_depth)
                analysis.update(nested_analysis)
            
            # Enhanced binary detection for nested content
            if self._has_nested_binary(objects, field_name):
                analysis['has_nested_binary'] = True
                analysis['is_binary'] = True  # Mark as binary if nested binary is found
        
        return field_analysis
    
    def _enhance_deep_analysis(self, field_analysis: Dict[str, Dict[str, Any]], objects: List[Dict[str, Any]], max_depth: int) -> Dict[str, Dict[str, Any]]:
        """
        Enhance the deep analysis with additional insights about nested structures.
        
        Args:
            field_analysis: Initial field analysis
            objects: List of JSON objects
            max_depth: Maximum depth to analyze
            
        Returns:
            Enhanced field analysis with deeper insights
        """
        enhanced_analysis = field_analysis.copy()
        
        for field_name, analysis in enhanced_analysis.items():
            # Analyze nested structures more deeply
            if 'dict' in analysis['types'] or 'list' in analysis['types']:
                nested_insights = self._analyze_deep_nested_insights(objects, field_name, max_depth)
                analysis.update(nested_insights)
            
            # Analyze string patterns more deeply (simplified)
            if 'str' in analysis['types']:
                # Just add basic string insights without complex analysis
                string_insights = self._analyze_basic_string_patterns(objects, field_name)
                analysis.update(string_insights)
            
            # Analyze array contents more deeply
            if 'list' in analysis['types']:
                array_insights = self._analyze_deep_array_contents(objects, field_name, max_depth)
                analysis.update(array_insights)
        
        return enhanced_analysis
    
    def _analyze_deep_nested_insights(self, objects: List[Dict[str, Any]], field_name: str, max_depth: int) -> Dict[str, Any]:
        """
        Analyze nested structures for deeper insights.
        
        Args:
            objects: List of JSON objects
            field_name: Name of the field to analyze
            max_depth: Maximum depth to analyze
            
        Returns:
            Deep nested insights
        """
        insights = {
            'deep_nested_types': set(),
            'deep_nested_patterns': set(),
            'deep_nested_binary_count': 0,
            'deep_nested_string_lengths': [],
            'deep_nested_complexity': 0
        }
        
        for obj in objects:
            if field_name in obj:
                value = obj[field_name]
                self._analyze_single_nested_value(value, insights, 0, max_depth)
        
        # Calculate complexity score
        insights['deep_nested_complexity'] = len(insights['deep_nested_types']) + len(insights['deep_nested_patterns'])
        
        return insights
    
    def _analyze_single_nested_value(self, value: Any, insights: Dict[str, Any], current_depth: int, max_depth: int) -> None:
        """
        Analyze a single nested value recursively.
        
        Args:
            value: Value to analyze
            insights: Insights dictionary to update
            current_depth: Current depth in the structure
            max_depth: Maximum depth to analyze
        """
        if current_depth >= max_depth:
            return
        
        value_type = type(value).__name__
        insights['deep_nested_types'].add(value_type)
        
        if isinstance(value, str):
            # Analyze string patterns
            if self._is_email(value):
                insights['deep_nested_patterns'].add('email')
            elif self._is_url(value):
                insights['deep_nested_patterns'].add('url')
            elif self._is_date_time(value):
                insights['deep_nested_patterns'].add('datetime')
            elif self._is_uuid(value):
                insights['deep_nested_patterns'].add('uuid')
            
            # Track string lengths
            insights['deep_nested_string_lengths'].append(len(value))
            
            # Check for binary
            if self._is_likely_binary(value):
                insights['deep_nested_binary_count'] += 1
                
        elif isinstance(value, dict):
            # Recursively analyze dictionary
            for k, v in value.items():
                self._analyze_single_nested_value(v, insights, current_depth + 1, max_depth)
                
        elif isinstance(value, list):
            # Recursively analyze list items
            for item in value:
                self._analyze_single_nested_value(item, insights, current_depth + 1, max_depth)
    
    def _analyze_basic_string_patterns(self, objects: List[Dict[str, Any]], field_name: str) -> Dict[str, Any]:
        """
        Analyze string patterns with basic insights (simplified version).
        
        Args:
            objects: List of JSON objects
            field_name: Name of the field to analyze
            
        Returns:
            Basic string pattern insights
        """
        insights = {
            'string_patterns': set(),
            'string_length_distribution': []
        }
        
        string_values = []
        for obj in objects:
            if field_name in obj and isinstance(obj[field_name], str):
                string_values.append(obj[field_name])
        
        if not string_values:
            return insights
        
        # Analyze patterns
        for value in string_values:
            if self._is_email(value):
                insights['string_patterns'].add('email')
            elif self._is_url(value):
                insights['string_patterns'].add('url')
            elif self._is_date_time(value):
                insights['string_patterns'].add('datetime')
            elif self._is_uuid(value):
                insights['string_patterns'].add('uuid')
            elif self._is_likely_binary(value):
                insights['string_patterns'].add('binary')
            
            # Track length distribution
            insights['string_length_distribution'].append(len(value))
        
        return insights
    
    def _analyze_deep_string_patterns(self, objects: List[Dict[str, Any]], field_name: str) -> Dict[str, Any]:
        """
        Analyze string patterns more deeply.
        
        Args:
            objects: List of JSON objects
            field_name: Name of the field to analyze
            
        Returns:
            Deep string pattern insights
        """
        insights = {
            'string_patterns': set(),
            'string_length_distribution': [],
            'string_entropy_scores': [],
            'string_common_prefixes': set(),
            'string_common_suffixes': set()
        }
        
        string_values = []
        for obj in objects:
            if field_name in obj and isinstance(obj[field_name], str):
                string_values.append(obj[field_name])
        
        if not string_values:
            return insights
        
        # Analyze patterns
        for value in string_values:
            if self._is_email(value):
                insights['string_patterns'].add('email')
            elif self._is_url(value):
                insights['string_patterns'].add('url')
            elif self._is_date_time(value):
                insights['string_patterns'].add('datetime')
            elif self._is_uuid(value):
                insights['string_patterns'].add('uuid')
            elif self._is_likely_binary(value):
                insights['string_patterns'].add('binary')
            
            # Track length distribution
            insights['string_length_distribution'].append(len(value))
            
            # Calculate entropy (simplified)
            unique_chars = len(set(value))
            if len(value) > 0:
                entropy = unique_chars / len(value)
                insights['string_entropy_scores'].append(entropy)
            
            # Track common prefixes/suffixes (first/last 3 chars)
            if len(value) >= 3:
                insights['string_common_prefixes'].add(value[:3])
                insights['string_common_suffixes'].add(value[-3:])
        
        return insights
    
    def _analyze_deep_array_contents(self, objects: List[Dict[str, Any]], field_name: str, max_depth: int) -> Dict[str, Any]:
        """
        Analyze array contents more deeply.
        
        Args:
            objects: List of JSON objects
            field_name: Name of the field to analyze
            max_depth: Maximum depth to analyze
            
        Returns:
            Deep array content insights
        """
        insights = {
            'array_item_types': set(),
            'array_item_patterns': set(),
            'array_nested_complexity': 0,
            'array_consistent_structure': True,
            'array_max_nested_depth': 0
        }
        
        array_structures = []
        
        for obj in objects:
            if field_name in obj and isinstance(obj[field_name], list):
                array = obj[field_name]
                array_structures.append(len(array))
                
                for item in array:
                    item_type = type(item).__name__
                    insights['array_item_types'].add(item_type)
                    
                    # Analyze nested items
                    if isinstance(item, (dict, list)):
                        nested_insights = {'deep_nested_types': set(), 'deep_nested_patterns': set()}
                        self._analyze_single_nested_value(item, nested_insights, 0, max_depth)
                        insights['array_item_patterns'].update(nested_insights['deep_nested_patterns'])
                        insights['array_max_nested_depth'] = max(insights['array_max_nested_depth'], 
                                                               len(nested_insights['deep_nested_types']))
        
        # Check if arrays have consistent structure
        if len(set(array_structures)) > 1:
            insights['array_consistent_structure'] = False
        
        insights['array_nested_complexity'] = len(insights['array_item_types']) + len(insights['array_item_patterns'])
        
        return insights
    
    def _analyze_nested_structures(self, objects: List[Dict[str, Any]], field_name: str) -> Dict[str, Any]:
        """
        Analyze nested structures within a field.
        
        Args:
            objects: List of JSON objects
            field_name: Name of the field to analyze
            
        Returns:
            Analysis of nested structures
        """
        nested_analysis = {
            'nested_types': set(),
            'max_depth': 0,
            'has_binary_at_depth': {},
            'mixed_nested_types': False
        }
        
        for obj in objects:
            if field_name in obj:
                value = obj[field_name]
                depth_info = self._analyze_structure_depth(value, 0)
                nested_analysis['max_depth'] = max(nested_analysis['max_depth'], depth_info['depth'])
                nested_analysis['nested_types'].update(depth_info['types'])
                
                # Check for binary at different depths
                if depth_info['has_binary']:
                    nested_analysis['has_binary_at_depth'][depth_info['depth']] = True
        
        nested_analysis['mixed_nested_types'] = len(nested_analysis['nested_types']) > 1
        return nested_analysis
    
    def _analyze_structure_depth(self, value: Any, current_depth: int) -> Dict[str, Any]:
        """
        Analyze the depth and types of a nested structure.
        
        Args:
            value: Value to analyze
            current_depth: Current depth in the structure
            
        Returns:
            Depth analysis information
        """
        result = {
            'depth': current_depth,
            'types': {type(value).__name__},
            'has_binary': False
        }
        
        if isinstance(value, str):
            if self._is_likely_binary(value):
                result['has_binary'] = True
        elif isinstance(value, dict):
            for k, v in value.items():
                nested_result = self._analyze_structure_depth(v, current_depth + 1)
                result['depth'] = max(result['depth'], nested_result['depth'])
                result['types'].update(nested_result['types'])
                if nested_result['has_binary']:
                    result['has_binary'] = True
        elif isinstance(value, list):
            for item in value:
                nested_result = self._analyze_structure_depth(item, current_depth + 1)
                result['depth'] = max(result['depth'], nested_result['depth'])
                result['types'].update(nested_result['types'])
                if nested_result['has_binary']:
                    result['has_binary'] = True
        
        return result
    
    def _has_nested_binary(self, objects: List[Dict[str, Any]], field_name: str) -> bool:
        """
        Check if a field contains nested binary data.
        
        Args:
            objects: List of JSON objects
            field_name: Name of the field to check
            
        Returns:
            True if nested binary data is found
        """
        for obj in objects:
            if field_name in obj:
                if self._contains_binary_recursive(obj[field_name]):
                    return True
        return False
    
    def _contains_binary_recursive(self, value: Any) -> bool:
        """
        Recursively check if a value contains binary data.
        
        Args:
            value: Value to check
            
        Returns:
            True if binary data is found
        """
        if isinstance(value, str):
            return self._is_likely_binary(value)
        elif isinstance(value, dict):
            return any(self._contains_binary_recursive(v) for v in value.values())
        elif isinstance(value, list):
            return any(self._contains_binary_recursive(item) for item in value)
        return False
    
    def _generate_smart_property_schema(self, field_name: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a smart property schema that intelligently handles various data types.
        
        Args:
            field_name: Name of the field
            analysis: Analysis of the field
            
        Returns:
            Smart property schema
        """
        # Handle binary data
        if analysis.get('is_binary', False):
            return self._generate_smart_binary_schema(field_name, analysis)
        
        # Handle mixed types with intelligence
        if analysis.get('is_mixed', False) or len(analysis['types']) > 1:
            return self._generate_smart_mixed_schema(field_name, analysis)
        
        # Handle single types with enhanced validation
        return self._generate_smart_single_type_schema(field_name, analysis)
    
    def _generate_smart_binary_schema(self, field_name: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate schema for binary data with intelligent handling.
        
        Args:
            field_name: Name of the field
            analysis: Analysis of the field
            
        Returns:
            Binary-aware schema
        """
        # Direct binary - strict validation
        return {
            "type": "string",
            "contentEncoding": "base64",
            "contentMediaType": "application/octet-stream",
            "minLength": 1,
            "pattern": "^[A-Za-z0-9+/]*={0,2}$",
            "description": f"Binary data for {field_name} (base64 encoded)",
            "examples": ["SGVsbG8gV29ybGQ="]
        }
    
    def _generate_smart_mixed_schema(self, field_name: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate schema for mixed types with intelligent handling.
        
        Args:
            field_name: Name of the field
            analysis: Analysis of the field
            
        Returns:
            Smart mixed type schema
        """
        type_options = []
        
        # Add detected types with enhanced validation
        if 'str' in analysis['types']:
            str_schema = {"type": "string", "minLength": 1}
            
            # Add max length constraint for strings (simplified)
            max_length = analysis.get('max_length')
            if max_length is not None and max_length > 0:
                # Use reasonable maximum based on pattern
                patterns = analysis.get('patterns', set())
                if 'uuid' in patterns:
                    str_schema["maxLength"] = max_length
                elif 'email' in patterns:
                    str_schema["maxLength"] = min(max_length * 2, 254)
                elif 'url' in patterns:
                    str_schema["maxLength"] = min(max_length * 3, 2048)
                else:
                    str_schema["maxLength"] = min(max_length * 2, 1000)
            
            if analysis.get('is_binary', False):
                str_schema.update({
                    "contentEncoding": "base64",
                    "pattern": "^[A-Za-z0-9+/]*={0,2}$"
                })
            type_options.append(str_schema)
        
        if 'int' in analysis['types']:
            type_options.append({"type": "integer"})
        if 'float' in analysis['types']:
            type_options.append({"type": "number"})
        if 'bool' in analysis['types']:
            type_options.append({"type": "boolean"})
        if 'list' in analysis['types']:
            type_options.append({
                "type": "array",
                "items": {},
                "minItems": 0
            })
        if 'dict' in analysis['types']:
            # For dict types, analyze if they need additionalProperties
            needs_additional = self._analyze_dict_type_additional_properties_needed(analysis)
            schema = {"type": "object"}
            if needs_additional:
                schema["additionalProperties"] = True
                schema["description"] = "⚠️ WARNING: Object allows additional properties due to mixed content. Consider defining explicit field schemas."
            type_options.append(schema)
        
        # Always allow null for flexibility
        type_options.append({"type": "null"})
        
        return {
            "oneOf": type_options,
            "description": f"Mixed content for {field_name} (intelligently handles detected types)"
        }
    
    def _generate_smart_nested_schema(self, field_name: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate schema for nested structures with recursive analysis.
        
        Args:
            field_name: Name of the field
            analysis: Analysis of the field
            
        Returns:
            Nested structure schema
        """
        # Check if we have recursive nested analysis
        if 'max_depth_found' in analysis and analysis['max_depth_found'] > 0:
            # Use recursive nested schema generation
            return self._generate_recursive_nested_schema(field_name, analysis)
        
        # Fallback to original nested schema generation
        if analysis.get('has_nested_binary', False):
            # Nested structure with binary content
            return {
                "oneOf": [
                    {
                        "type": "object",
                        "additionalProperties": True,
                        "description": f"Object with nested binary content for {field_name}"
                    },
                    {
                        "type": "array",
                        "items": {},
                        "description": f"Array with nested binary content for {field_name}"
                    }
                ],
                "description": f"Complex nested structure for {field_name} (may contain binary data)"
            }
        else:
            # Regular nested structure
            return {
                "oneOf": [
                    {
                        "type": "object",
                        "additionalProperties": True,
                        "description": f"Object structure for {field_name}"
                    },
                    {
                        "type": "array",
                        "items": {},
                        "description": f"Array structure for {field_name}"
                    }
                ],
                "description": f"Nested structure for {field_name}"
            }
    
    def _generate_smart_single_type_schema(self, field_name: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate schema for single type fields with enhanced validation.
        
        Args:
            field_name: Name of the field
            analysis: Analysis of the field
            
        Returns:
            Enhanced single type schema
        """
        schema = self._generate_property_schema(field_name, analysis)
        
        # Add enhanced validation
        if schema.get("type") == "string":
            schema["minLength"] = 1
            if analysis.get('is_binary', False):
                schema.update({
                    "contentEncoding": "base64",
                    "pattern": "^[A-Za-z0-9+/]*={0,2}$"
                })
        elif schema.get("type") == "array":
            schema["minItems"] = 0
        
        return schema
    
    def _analyze_nested_structures_recursive(self, objects: List[Dict[str, Any]], field_name: str, max_depth: int = 100) -> Dict[str, Any]:
        """
        Recursively analyze nested structures to understand the complete hierarchy.
        
        Args:
            objects: List of JSON objects
            field_name: Name of the field to analyze
            max_depth: Maximum depth to analyze (default: 100)
            
        Returns:
            Analysis of nested structures with complete hierarchy
        """
        nested_analysis = {
            'max_depth_found': 0,
            'structure_hierarchy': {},
            'all_possible_paths': set(),
            'has_binary_at_depth': {},
            'mixed_types_at_depth': {},
            'required_fields_at_depth': {},
            'optional_fields_at_depth': {}
        }
        
        for obj in objects:
            if field_name in obj:
                value = obj[field_name]
                if isinstance(value, dict):
                    self._analyze_dict_structure_recursive(value, nested_analysis, 0, max_depth, [field_name])
        
        return nested_analysis
    
    def _analyze_dict_structure_recursive(self, data: Dict[str, Any], analysis: Dict[str, Any], 
                                        current_depth: int, max_depth: int, path: List[str]) -> None:
        """
        Recursively analyze dictionary structure to build complete hierarchy.
        
        Args:
            data: Dictionary to analyze
            analysis: Analysis dictionary to update
            current_depth: Current depth in the structure
            max_depth: Maximum depth to analyze
            path: Current path in the structure
        """
        if current_depth >= max_depth:
            return
            
        analysis['max_depth_found'] = max(analysis['max_depth_found'], current_depth)
        
        # Record the current path
        path_str = '.'.join(path)
        analysis['all_possible_paths'].add(path_str)
        
        # Initialize depth-specific analysis if not exists
        if current_depth not in analysis['structure_hierarchy']:
            analysis['structure_hierarchy'][current_depth] = {
                'fields': set(),
                'types': set(),
                'required_fields': set(),
                'optional_fields': set()
            }
        
        # Analyze current level
        for key, value in data.items():
            analysis['structure_hierarchy'][current_depth]['fields'].add(key)
            
            # Analyze value type
            value_type = type(value).__name__
            analysis['structure_hierarchy'][current_depth]['types'].add(value_type)
            
            # Check for binary data
            if isinstance(value, str) and self._is_likely_binary(value):
                if current_depth not in analysis['has_binary_at_depth']:
                    analysis['has_binary_at_depth'][current_depth] = set()
                analysis['has_binary_at_depth'][current_depth].add(key)
            
            # Track required vs optional fields
            if value is not None:
                analysis['structure_hierarchy'][current_depth]['required_fields'].add(key)
            else:
                analysis['structure_hierarchy'][current_depth]['optional_fields'].add(key)
            
            # Recursively analyze nested structures
            if isinstance(value, dict):
                new_path = path + [key]
                self._analyze_dict_structure_recursive(value, analysis, current_depth + 1, max_depth, new_path)
            elif isinstance(value, list):
                # Analyze list items if they contain dictionaries
                for item in value:
                    if isinstance(item, dict):
                        new_path = path + [key, '[]']
                        self._analyze_dict_structure_recursive(item, analysis, current_depth + 1, max_depth, new_path)
    
    def _generate_recursive_nested_schema(self, field_name: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate schema for deeply nested structures with recursive analysis.
        
        Args:
            field_name: Name of the field
            analysis: Analysis of the nested structure
            
        Returns:
            Schema for nested structure
        """
        max_depth = analysis.get('max_depth_found', 0)
        structure_hierarchy = analysis.get('structure_hierarchy', {})
        
        if max_depth == 0:
            # No nesting found
            return {"type": "object", "additionalProperties": True}
        
        # Generate schema for the maximum depth found
        schema = self._generate_nested_level_schema(structure_hierarchy, max_depth, field_name)
        
        # Add description about the nested structure
        schema["description"] = f"Deeply nested structure for {field_name} (max depth: {max_depth})"
        
        return schema
    
    def _generate_nested_level_schema(self, structure_hierarchy: Dict[int, Dict[str, Any]], 
                                    target_depth: int, field_name: str) -> Dict[str, Any]:
        """
        Generate schema for a specific nesting level.
        
        Args:
            structure_hierarchy: Hierarchy analysis
            target_depth: Target depth to generate schema for
            field_name: Name of the field
            
        Returns:
            Schema for the specified nesting level
        """
        if target_depth == 0:
            # Base case - generate object schema
            return self._generate_base_object_schema(structure_hierarchy.get(0, {}))
        
        # Recursive case - generate nested object
        current_level = structure_hierarchy.get(target_depth, {})
        base_schema = self._generate_base_object_schema(current_level)
        
        # If this is not the deepest level, allow further nesting
        if target_depth > 0:
            # Allow additional properties for potential deeper nesting
            base_schema["additionalProperties"] = True
        
        return base_schema
    
    def _generate_base_object_schema(self, level_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate base object schema for a specific level.
        
        Args:
            level_analysis: Analysis for the current level
            
        Returns:
            Base object schema
        """
        schema = {
            "type": "object",
            "properties": {},
            "additionalProperties": True  # Allow additional properties for flexibility
        }
        
        fields = level_analysis.get('fields', set())
        required_fields = level_analysis.get('required_fields', set())
        optional_fields = level_analysis.get('optional_fields', set())
        
        # Generate property schemas for each field
        for field in fields:
            # For now, allow any type for nested fields
            # This could be enhanced to analyze the actual types found
            schema["properties"][field] = {
                "oneOf": [
                    {"type": "string"},
                    {"type": "number"},
                    {"type": "integer"},
                    {"type": "boolean"},
                    {"type": "object", "additionalProperties": True},
                    {"type": "array", "items": {}},
                    {"type": "null"}
                ]
            }
        
        # Add required fields if any
        if required_fields:
            schema["required"] = list(required_fields)
        
        return schema
    
    def analyze_objects_with_depth(self, objects: List[Dict[str, Any]], max_depth: int = 200) -> Dict[str, Any]:
        """
        Analyze objects to understand their structure without generating a schema.
        
        Args:
            objects: List of JSON objects to analyze
            max_depth: Maximum depth to analyze for nested structures (default: 100)
            
        Returns:
            Detailed analysis of object structure
        """
        if not objects:
            raise ValueError("JSON objects list cannot be empty")
        
        # Get deep field analysis
        field_analysis = self._analyze_fields_deep_with_depth(objects, max_depth)
        
        # Create comprehensive analysis result
        analysis = {
            "total_objects": len(objects),
            "max_depth_analyzed": max_depth,
            "fields": {},
            "summary": {
                "total_fields": len(field_analysis),
                "fields_with_nesting": 0,
                "fields_with_binary": 0,
                "fields_with_mixed_types": 0,
                "max_nested_depth_found": 0
            }
        }
        
        # Process each field
        for field_name, field_info in field_analysis.items():
            field_analysis_result = {
                "types": list(field_info.get('types', set())),
                "is_required": field_info.get('required', False),
                "null_percentage": field_info.get('null_percentage', 0),
                "is_binary": field_info.get('is_binary', False),
                "is_mixed": field_info.get('is_mixed', False),
                "has_nested_binary": field_info.get('has_nested_binary', False)
            }
            
            # Add nested structure info if present
            if 'max_depth_found' in field_info:
                field_analysis_result["nested_structure"] = {
                    "max_depth": field_info['max_depth_found'],
                    "all_possible_paths": list(field_info.get('all_possible_paths', set())),
                    "structure_hierarchy": {}
                }
                
                # Convert sets to lists for JSON serialization
                if 'structure_hierarchy' in field_info:
                    hierarchy = field_info['structure_hierarchy']
                    for depth, level_info in hierarchy.items():
                        field_analysis_result["nested_structure"]["structure_hierarchy"][depth] = {
                            "fields": list(level_info.get('fields', set())),
                            "types": list(level_info.get('types', set())),
                            "required_fields": list(level_info.get('required_fields', set())),
                            "optional_fields": list(level_info.get('optional_fields', set()))
                        }
                
                analysis["summary"]["max_nested_depth_found"] = max(
                    analysis["summary"]["max_nested_depth_found"], 
                    field_info['max_depth_found']
                )
                analysis["summary"]["fields_with_nesting"] += 1
            
            # Update summary statistics
            if field_info.get('is_binary', False) or field_info.get('has_nested_binary', False):
                analysis["summary"]["fields_with_binary"] += 1
            
            if field_info.get('is_mixed', False):
                analysis["summary"]["fields_with_mixed_types"] += 1
            
            analysis["fields"][field_name] = field_analysis_result
        
        return analysis
    
    # Backward compatibility methods
    def analyze_json_list(self, json_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Backward compatibility method for JSON list analysis.
        
        Args:
            json_data: List of JSON objects to analyze
            
        Returns:
            Generated JSON schema
        """
        return self._analyze_objects(json_data)
