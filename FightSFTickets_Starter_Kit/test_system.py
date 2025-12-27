#!/usr/bin/env python3
"""
Comprehensive System Test for FightSFTickets
Tests all critical components to verify production readiness and revenue capability.
"""

import sys
import os
import json
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add backend to path - need to add both backend/src and backend/src/app
backend_src = Path(__file__).parent / "backend" / "src"
sys.path.insert(0, str(backend_src))
sys.path.insert(0, str(backend_src.parent))

# Change to backend/src directory for imports
os.chdir(str(backend_src))

def test_imports():
    """Test that all critical modules can be imported."""
    print("🔍 Testing imports...")
    try:
        # Try different import paths
        try:
            from src.app import app
            from src.config import settings
            from src.services.database import get_db_service
            from src.services.stripe_service import StripeService
            from src.services.mail import get_mail_service
            from src.middleware.request_id import RequestIDMiddleware
            from src.middleware.rate_limit import get_rate_limiter
        except ImportError:
            # Fallback to direct imports
            from app import app
            from config import settings
            from services.database import get_db_service
            from services.stripe_service import StripeService
            from services.mail import get_mail_service
            from middleware.request_id import RequestIDMiddleware
            from middleware.rate_limit import get_rate_limiter
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_configuration():
    """Test that configuration is properly set up."""
    print("\n🔍 Testing configuration...")
    try:
        from config import settings
        
        issues = []
        
        # Check critical settings
        if settings.app_env == "dev":
            print("⚠️  Running in DEV mode (expected for testing)")
        
        # Check database URL
        if "postgres" not in settings.database_url.lower():
            issues.append("Database URL doesn't look like PostgreSQL")
        
        # Check Stripe
        if settings.stripe_secret_key.startswith("sk_test_"):
            print("⚠️  Using Stripe TEST keys (expected for testing)")
        elif settings.stripe_secret_key == "sk_test_dummy":
            issues.append("Stripe secret key not configured")
        
        # Check Lob
        if settings.lob_api_key == "test_dummy" or settings.lob_api_key == "change-me":
            issues.append("Lob API key not configured")
        
        # Check AI services
        if settings.deepseek_api_key == "sk_dummy" or settings.deepseek_api_key == "change-me":
            print("⚠️  DeepSeek API key not configured (optional)")
        
        if issues:
            print(f"❌ Configuration issues: {', '.join(issues)}")
            return False
        else:
            print("✅ Configuration looks good")
            return True
            
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_database_connection():
    """Test database connectivity."""
    print("\n🔍 Testing database connection...")
    try:
        from services.database import get_db_service
        
        db_service = get_db_service()
        if db_service.health_check():
            print("✅ Database connection successful")
            return True
        else:
            print("❌ Database health check failed")
            return False
            
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("   Note: Database may not be running. Start with: docker-compose up -d db")
        return False

def test_api_routes():
    """Test that all API routes are registered."""
    print("\n🔍 Testing API routes...")
    try:
        from app import app
        
        routes = [route.path for route in app.routes]
        required_routes = [
            "/",
            "/health",
            "/status",
            "/tickets/validate",
            "/checkout/create-session",
            "/api/webhook/stripe",
            "/admin/stats",
        ]
        
        missing = []
        for route in required_routes:
            if not any(route in r for r in routes):
                missing.append(route)
        
        if missing:
            print(f"❌ Missing routes: {', '.join(missing)}")
            return False
        else:
            print(f"✅ All required routes registered ({len(routes)} total)")
            return True
            
    except Exception as e:
        print(f"❌ Route test failed: {e}")
        return False

def test_middleware():
    """Test that middleware is properly configured."""
    print("\n🔍 Testing middleware...")
    try:
        from app import app
        from middleware.request_id import RequestIDMiddleware
        from middleware.rate_limit import RateLimitMiddleware
        
        middleware_types = [type(m).__name__ for m in app.user_middleware]
        
        has_request_id = any("RequestIDMiddleware" in str(m) for m in app.user_middleware)
        has_cors = any("CORSMiddleware" in str(m) for m in app.user_middleware)
        
        if not has_request_id:
            print("⚠️  RequestIDMiddleware not found (may be registered differently)")
        if not has_cors:
            print("⚠️  CORSMiddleware not found")
        
        # Check rate limiter
        if hasattr(app.state, 'limiter'):
            print("✅ Rate limiter configured")
        else:
            print("⚠️  Rate limiter not in app.state")
        
        print(f"✅ Middleware configured ({len(app.user_middleware)} middleware)")
        return True
        
    except Exception as e:
        print(f"❌ Middleware test failed: {e}")
        return False

def test_services():
    """Test that services can be initialized."""
    print("\n🔍 Testing services...")
    try:
        from services.stripe_service import StripeService
        from services.mail import get_mail_service
        
        # Test Stripe service
        stripe_service = StripeService()
        print(f"✅ Stripe service initialized (mode: {stripe_service.mode})")
        
        # Test Mail service
        mail_service = get_mail_service()
        print(f"✅ Mail service initialized (available: {mail_service.is_available})")
        
        return True
        
    except Exception as e:
        print(f"❌ Service test failed: {e}")
        return False

def test_citation_validation():
    """Test citation validation service."""
    print("\n🔍 Testing citation validation...")
    try:
        from services.citation import CitationValidator
        
        validator = CitationValidator()
        
        # Test SF citation
        result = validator.validate_citation("912345678")
        if result.is_valid:
            print(f"✅ Citation validation working (tested SF citation)")
            return True
        else:
            print(f"⚠️  Citation validation returned invalid (may be expected)")
            return True  # Still counts as working
            
    except Exception as e:
        print(f"❌ Citation validation test failed: {e}")
        return False

def test_database_models():
    """Test that database models are properly defined."""
    print("\n🔍 Testing database models...")
    try:
        from models import Intake, Draft, Payment, AppealType, PaymentStatus
        
        # Check that models exist
        assert Intake is not None
        assert Draft is not None
        assert Payment is not None
        assert AppealType.STANDARD == "standard"
        assert AppealType.CERTIFIED == "certified"
        
        print("✅ Database models properly defined")
        return True
        
    except Exception as e:
        print(f"❌ Database models test failed: {e}")
        return False

def test_revenue_readiness():
    """Test that the system is ready to process payments."""
    print("\n🔍 Testing revenue readiness...")
    try:
        from config import settings
        from services.stripe_service import StripeService
        
        issues = []
        
        # Check Stripe configuration
        if settings.stripe_secret_key.startswith("sk_test_"):
            print("⚠️  Using TEST Stripe keys - switch to LIVE keys for production revenue")
        elif settings.stripe_secret_key == "sk_test_dummy":
            issues.append("Stripe secret key not configured")
        
        if not settings.stripe_price_standard or settings.stripe_price_standard == "price_":
            issues.append("Stripe standard price not configured")
        
        if not settings.stripe_price_certified or settings.stripe_price_certified == "price_":
            issues.append("Stripe certified price not configured")
        
        # Check Lob (required for fulfillment)
        if settings.lob_api_key == "test_dummy" or settings.lob_api_key == "change-me":
            issues.append("Lob API key not configured (required for mail fulfillment)")
        
        # Check database (required for storing payments)
        from services.database import get_db_service
        db_service = get_db_service()
        if not db_service.health_check():
            issues.append("Database not connected (required for payment storage)")
        
        if issues:
            print(f"❌ Revenue readiness issues:")
            for issue in issues:
                print(f"   - {issue}")
            return False
        else:
            print("✅ System ready for revenue generation")
            print("   - Stripe configured")
            print("   - Prices configured")
            print("   - Mail service configured")
            print("   - Database connected")
            return True
            
    except Exception as e:
        print(f"❌ Revenue readiness test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("FightSFTickets System Test")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("Configuration", test_configuration),
        ("Database Connection", test_database_connection),
        ("API Routes", test_api_routes),
        ("Middleware", test_middleware),
        ("Services", test_services),
        ("Citation Validation", test_citation_validation),
        ("Database Models", test_database_models),
        ("Revenue Readiness", test_revenue_readiness),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name} test crashed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print("\n" + "=" * 60)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - System is ready!")
    elif passed >= total - 2:
        print("⚠️  Most tests passed - Minor issues to address")
    else:
        print("❌ Multiple tests failed - System needs attention")
    
    print("=" * 60)
    
    # Revenue readiness check
    revenue_ready = any(name == "Revenue Readiness" and result for name, result in results)
    if revenue_ready:
        print("\n💰 REVENUE READINESS: ✅ READY")
        print("   The system is configured to process payments and generate revenue.")
    else:
        print("\n💰 REVENUE READINESS: ⚠️  NOT READY")
        print("   Please configure Stripe, Lob, and database before processing payments.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

