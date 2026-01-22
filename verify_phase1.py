"""
Phase 1 Verification Script

Checks that all required files and components are in place.
Run this to verify Phase 1 completion.
"""

import os
import sys
from pathlib import Path
from typing import List, Tuple

# ANSI color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


def print_header(text: str):
    """Print section header"""
    print(f"\n{BLUE}{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}{RESET}\n")


def check_file(filepath: str, required: bool = True) -> bool:
    """Check if a file exists"""
    exists = os.path.exists(filepath)
    status = f"{GREEN}✓{RESET}" if exists else f"{RED}✗{RESET}"
    req_text = "(required)" if required else "(optional)"
    print(f"  {status} {filepath} {req_text}")
    return exists


def check_directory(dirpath: str) -> bool:
    """Check if a directory exists"""
    exists = os.path.isdir(dirpath)
    status = f"{GREEN}✓{RESET}" if exists else f"{RED}✗{RESET}"
    print(f"  {status} {dirpath}/")
    return exists


def check_import(module_name: str) -> bool:
    """Check if a Python module can be imported"""
    try:
        __import__(module_name)
        print(f"  {GREEN}✓{RESET} {module_name}")
        return True
    except ImportError:
        print(f"  {RED}✗{RESET} {module_name} (import failed)")
        return False


def verify_phase1() -> Tuple[int, int]:
    """Verify all Phase 1 requirements"""
    
    checks_passed = 0
    total_checks = 0
    
    # Change to project root
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    print_header("PHASE 1 VERIFICATION")
    print(f"Project Root: {project_root}\n")
    
    # 1. Check folder structure
    print_header("1. FOLDER STRUCTURE")
    
    directories = [
        "backend",
        "backend/app",
        "backend/app/api",
        "backend/app/core",
        "backend/app/schemas",
        "backend/app/utils",
        "backend/config",
        "docs",
        "frontend",
        "HRM-main",
    ]
    
    for directory in directories:
        total_checks += 1
        if check_directory(directory):
            checks_passed += 1
    
    # 2. Check core backend files
    print_header("2. CORE BACKEND FILES")
    
    core_files = [
        "backend/app/__init__.py",
        "backend/app/main.py",
        "backend/app/config.py",
        "backend/app/api/__init__.py",
        "backend/app/api/routes.py",
        "backend/app/api/middleware.py",
        "backend/app/core/__init__.py",
        "backend/app/core/preprocessor.py",
        "backend/app/core/llm_interpreter.py",
        "backend/app/core/hrm_engine.py",
        "backend/app/core/action_executor.py",
        "backend/app/core/schema_validator.py",
        "backend/app/schemas/__init__.py",
        "backend/app/schemas/request_schema.py",
        "backend/app/utils/__init__.py",
        "backend/app/utils/helpers.py",
    ]
    
    for file in core_files:
        total_checks += 1
        if check_file(file):
            checks_passed += 1
    
    # 3. Check configuration files
    print_header("3. CONFIGURATION FILES")
    
    config_files = [
        "backend/requirements.txt",
        "backend/.env.example",
        "backend/README.md",
        ".gitignore",
    ]
    
    for file in config_files:
        total_checks += 1
        if check_file(file):
            checks_passed += 1
    
    # 4. Check test files
    print_header("4. TEST FILES")
    
    test_files = [
        "backend/test_system.py",
        "backend/test_phase1.py",
    ]
    
    for file in test_files:
        total_checks += 1
        if check_file(file):
            checks_passed += 1
    
    # 5. Check documentation
    print_header("5. DOCUMENTATION")
    
    doc_files = [
        "README.md",
        "ARCHITECTURE.md",
        "PHASE-1-COMPLETE.md",
        "docs/PROJECT.md",
        "docs/PHASE-1.md",
        "docs/PHASE-2.md",
        "docs/PHASE-3.md",
        "docs/PHASE-4.md",
    ]
    
    for file in doc_files:
        total_checks += 1
        if check_file(file):
            checks_passed += 1
    
    # 6. Check Python imports
    print_header("6. PYTHON MODULES (Import Test)")
    
    # Change to backend directory for imports
    backend_path = project_root / "backend"
    sys.path.insert(0, str(backend_path))
    
    modules = [
        "app.schemas.request_schema",
        "app.core.preprocessor",
        "app.core.llm_interpreter",
        "app.core.hrm_engine",
        "app.core.action_executor",
        "app.core.schema_validator",
        "app.api.routes",
        "app.main",
    ]
    
    for module in modules:
        total_checks += 1
        if check_import(module):
            checks_passed += 1
    
    # 7. Check dependencies
    print_header("7. REQUIRED DEPENDENCIES")
    
    dependencies = [
        "fastapi",
        "uvicorn",
        "pydantic",
        "pytest",
    ]
    
    for dep in dependencies:
        total_checks += 1
        if check_import(dep):
            checks_passed += 1
    
    # 8. Check optional dependencies
    print_header("8. OPTIONAL DEPENDENCIES")
    
    optional_deps = [
        ("google.generativeai", "Gemini API (for LLM mode)"),
        ("torch", "PyTorch (for HRM model)"),
    ]
    
    for dep, description in optional_deps:
        try:
            __import__(dep)
            print(f"  {GREEN}✓{RESET} {dep} - {description}")
        except ImportError:
            print(f"  {YELLOW}○{RESET} {dep} - {description} (not installed, optional)")
    
    return checks_passed, total_checks


def main():
    """Main verification function"""
    
    try:
        checks_passed, total_checks = verify_phase1()
        
        # Print summary
        print_header("VERIFICATION SUMMARY")
        
        percentage = (checks_passed / total_checks * 100) if total_checks > 0 else 0
        
        print(f"  Checks Passed: {checks_passed}/{total_checks}")
        print(f"  Completion: {percentage:.1f}%\n")
        
        if checks_passed == total_checks:
            print(f"{GREEN}✅ PHASE 1 COMPLETE - ALL CHECKS PASSED!{RESET}")
            print(f"\n{BLUE}Next Steps:{RESET}")
            print(f"  1. Run: cd backend && python test_system.py")
            print(f"  2. Run: python -m app.main")
            print(f"  3. Visit: http://localhost:8000/docs")
            return 0
        else:
            print(f"{YELLOW}⚠️  PHASE 1 INCOMPLETE{RESET}")
            print(f"\n{RED}Missing Components: {total_checks - checks_passed}{RESET}")
            print(f"\nPlease ensure all required files are in place.")
            return 1
            
    except Exception as e:
        print(f"\n{RED}❌ VERIFICATION FAILED{RESET}")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
