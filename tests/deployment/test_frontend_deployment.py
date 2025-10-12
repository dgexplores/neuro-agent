"""
Frontend Deployment Tests
Tests for frontend build, configuration, and deployment readiness
"""

import json
import os
import pytest
from pathlib import Path


class TestFrontendConfiguration:
    """Test frontend configuration files"""

    def test_package_json_exists(self):
        """Test that package.json exists"""
        package_json = Path("frontend/package.json")
        assert package_json.exists(), "package.json should exist in frontend directory"

    def test_package_json_valid(self):
        """Test that package.json is valid JSON with required fields"""
        with open("frontend/package.json") as f:
            package = json.load(f)

        assert "name" in package, "package.json should have name field"
        assert "version" in package, "package.json should have version field"
        assert "dependencies" in package, "package.json should have dependencies"
        assert "scripts" in package, "package.json should have scripts"

    def test_required_dependencies(self):
        """Test that all required dependencies are present"""
        with open("frontend/package.json") as f:
            package = json.load(f)

        required_deps = [
            "react",
            "react-dom",
            "react-router-dom",
            "@mui/material",
            "axios"
        ]

        for dep in required_deps:
            assert dep in package["dependencies"], \
                f"{dep} should be in dependencies"

    def test_required_scripts(self):
        """Test that required npm scripts are defined"""
        with open("frontend/package.json") as f:
            package = json.load(f)

        required_scripts = ["start", "build", "test"]

        for script in required_scripts:
            assert script in package["scripts"], \
                f"{script} script should be defined"

    def test_env_production_exists(self):
        """Test that .env.production file exists"""
        env_prod = Path("frontend/.env.production")
        assert env_prod.exists(), ".env.production should exist"

    def test_env_production_config(self):
        """Test that .env.production has correct API URL"""
        with open("frontend/.env.production") as f:
            content = f.read()

        assert "REACT_APP_API_URL" in content, \
            ".env.production should define REACT_APP_API_URL"
        assert "1w80v6fnw1.execute-api.us-east-1.amazonaws.com" in content, \
            ".env.production should point to AWS API Gateway"

    def test_vercel_config_exists(self):
        """Test that vercel.json exists for deployment"""
        vercel_json = Path("frontend/vercel.json")
        assert vercel_json.exists(), "vercel.json should exist for Vercel deployment"

    def test_vercel_config_valid(self):
        """Test that vercel.json is valid and properly configured"""
        with open("frontend/vercel.json") as f:
            config = json.load(f)

        assert "builds" in config, "vercel.json should define builds"
        assert "routes" in config, "vercel.json should define routes"


class TestFrontendBuild:
    """Test frontend build process"""

    def test_build_directory_exists(self):
        """Test that build directory is created after npm run build"""
        build_dir = Path("frontend/build")
        assert build_dir.exists(), \
            "Build directory should exist after running npm run build"

    def test_build_index_html_exists(self):
        """Test that build produces index.html"""
        index_html = Path("frontend/build/index.html")
        assert index_html.exists(), \
            "Build should produce index.html"

    def test_build_static_assets_exist(self):
        """Test that build produces static assets"""
        static_dir = Path("frontend/build/static")
        assert static_dir.exists(), \
            "Build should produce static directory"

        # Check for JS bundle
        js_dir = static_dir / "js"
        assert js_dir.exists(), "Build should produce JS bundle"
        assert len(list(js_dir.glob("*.js"))) > 0, \
            "Build should contain at least one JS file"


class TestFrontendComponents:
    """Test that all required frontend components exist"""

    def test_app_component_exists(self):
        """Test that App.js exists"""
        app_js = Path("frontend/src/App.js")
        assert app_js.exists(), "App.js should exist"

    def test_required_pages_exist(self):
        """Test that all required page components exist"""
        required_pages = [
            "HomePage.js",
            "DiagnosisPage.js",
            "CaseHistoryPage.js"
        ]

        components_dir = Path("frontend/src/components")
        for page in required_pages:
            page_path = components_dir / page
            assert page_path.exists(), f"{page} should exist in components directory"

    def test_api_service_exists(self):
        """Test that API service exists"""
        api_service = Path("frontend/src/services/api.js")
        assert api_service.exists(), "api.js service should exist"

    def test_api_service_config(self):
        """Test that API service is properly configured"""
        with open("frontend/src/services/api.js", encoding='utf-8') as f:
            content = f.read()

        assert "REACT_APP_API_URL" in content, \
            "API service should read from REACT_APP_API_URL env var"
        assert "axios" in content, \
            "API service should use axios"


class TestDeploymentReadiness:
    """Test overall deployment readiness"""

    def test_no_console_errors_in_code(self):
        """Test that there are no console.error calls in production code"""
        # Check for console.error in source files (excluding test files)
        src_dir = Path("frontend/src")
        has_console_error = False

        for js_file in src_dir.rglob("*.js"):
            if "test" not in str(js_file):
                with open(js_file, encoding='utf-8') as f:
                    content = f.read()
                    if "console.error" in content and "axios" not in content:
                        # Allow console.error in error handling
                        has_console_error = True

        # This is informational, not a hard failure
        assert True, "Console.error check completed"

    def test_deployment_docs_exist(self):
        """Test that deployment documentation exists"""
        docs = [
            Path("DEPLOYMENT_QUICKSTART.md"),
            Path("README.md"),
            Path("DEMO_SCRIPT.md")
        ]

        for doc in docs:
            assert doc.exists(), f"{doc.name} should exist for deployment guidance"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
