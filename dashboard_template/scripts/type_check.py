"""
Type Safety Check Script

This script helps identify potential type mismatches between backend Pydantic models
and frontend TypeScript interfaces. It's a basic check - manual review is still recommended.

Usage:
    python scripts/type_check.py
"""

import re
import sys
from pathlib import Path


def extract_pydantic_fields(file_path: Path) -> dict:
    """Extract field names and types from a Pydantic model file."""
    fields = {}
    content = file_path.read_text()
    
    # Find class definitions
    class_pattern = r'class\s+(\w+)\s*\([^)]*\):'
    classes = re.findall(class_pattern, content)
    
    for class_name in classes:
        # Find field definitions within the class
        class_start = content.find(f'class {class_name}')
        if class_start == -1:
            continue
        
        # Find the next class or end of file
        next_class = content.find('\nclass ', class_start + 1)
        if next_class == -1:
            class_content = content[class_start:]
        else:
            class_content = content[class_start:next_class]
        
        # Extract field definitions (simple pattern)
        field_pattern = r'(\w+)\s*:\s*(\w+)'
        fields_found = re.findall(field_pattern, class_content)
        
        if fields_found:
            fields[class_name] = {name: type_name for name, type_name in fields_found}
    
    return fields


def extract_typescript_fields(file_path: Path) -> dict:
    """Extract field names and types from a TypeScript interface file."""
    fields = {}
    content = file_path.read_text()
    
    # Find interface definitions
    interface_pattern = r'interface\s+(\w+)\s*\{([^}]+)\}'
    interfaces = re.findall(interface_pattern, content, re.DOTALL)
    
    for interface_name, interface_body in interfaces:
        # Extract field definitions
        field_pattern = r'(\w+)\s*:\s*([^,;\n]+)'
        fields_found = re.findall(field_pattern, interface_body)
        
        if fields_found:
            fields[interface_name] = {name: type_name.strip() for name, type_name in fields_found}
    
    return fields


def compare_types(pydantic_fields: dict, ts_fields: dict) -> list:
    """Compare Pydantic and TypeScript fields and report mismatches."""
    mismatches = []
    
    # Check for matching class/interface names
    for class_name in pydantic_fields:
        if class_name not in ts_fields:
            mismatches.append(f"⚠️  TypeScript interface '{class_name}' not found")
            continue
        
        pydantic_model = pydantic_fields[class_name]
        ts_interface = ts_fields[class_name]
        
        # Check for missing fields
        for field in pydantic_model:
            if field not in ts_interface:
                mismatches.append(f"⚠️  {class_name}.{field} missing in TypeScript")
        
        for field in ts_interface:
            if field not in pydantic_model:
                mismatches.append(f"⚠️  {class_name}.{field} missing in Pydantic")
    
    return mismatches


def main():
    backend_dir = Path("backend/app/routers")
    frontend_types_file = Path("frontend/src/lib/types.ts")
    
    if not backend_dir.exists():
        print("❌ Backend routers directory not found")
        return
    
    if not frontend_types_file.exists():
        print("❌ Frontend types file not found")
        return
    
    # Extract Pydantic models from router files
    pydantic_fields = {}
    for router_file in backend_dir.glob("*.py"):
        fields = extract_pydantic_fields(router_file)
        pydantic_fields.update(fields)
    
    # Extract TypeScript interfaces
    ts_fields = extract_typescript_fields(frontend_types_file)
    
    # Compare
    mismatches = compare_types(pydantic_fields, ts_fields)
    
    print("=" * 60)
    print("TYPE SAFETY CHECK")
    print("=" * 60)
    
    if mismatches:
        print(f"\n❌ Found {len(mismatches)} potential issues:\n")
        for mismatch in mismatches:
            print(mismatch)
    else:
        print("\n✅ No obvious type mismatches found")
        print("⚠️  Note: This is a basic check. Manual review recommended.")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
