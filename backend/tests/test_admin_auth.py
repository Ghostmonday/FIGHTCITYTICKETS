import os
import pytest
from unittest.mock import patch, mock_open, MagicMock
from fastapi import HTTPException, Request, status

# Import from src.auth
from src.auth import verify_admin_secret, log_admin_action

@pytest.fixture
def mock_request():
    request = MagicMock(spec=Request)
    request.client.host = "1.2.3.4"
    request.url.path = "/test"
    request.method = "GET"
    return request

class TestAdminAuth:

    @patch("src.auth.os.getenv")
    @patch("src.auth.secrets.compare_digest")
    def test_verify_admin_secret_success(self, mock_compare, mock_getenv, mock_request):
        mock_getenv.side_effect = lambda k, d=None: "correct-secret" if k == "ADMIN_SECRET" else d
        mock_compare.return_value = True

        result = verify_admin_secret(mock_request, "correct-secret")
        assert result == "correct-secret"
        mock_compare.assert_called()

    @patch("src.auth.os.getenv")
    @patch("src.auth.secrets.compare_digest")
    def test_verify_admin_secret_failure(self, mock_compare, mock_getenv, mock_request):
        mock_getenv.side_effect = lambda k, d=None: "correct-secret" if k == "ADMIN_SECRET" else d
        mock_compare.return_value = False

        with pytest.raises(HTTPException) as excinfo:
            verify_admin_secret(mock_request, "wrong-secret")

        assert excinfo.value.status_code == 401
        assert excinfo.value.detail == "Invalid admin secret"

    @patch("src.auth.os.getenv")
    @patch("src.auth.secrets.compare_digest")
    def test_verify_admin_secret_ip_allowed(self, mock_compare, mock_getenv, mock_request):
        def getenv_side_effect(key, default=None):
            if key == "ADMIN_SECRET":
                return "correct-secret"
            if key == "ADMIN_ALLOWED_IPS":
                return "1.2.3.4,5.6.7.8"
            return default

        mock_getenv.side_effect = getenv_side_effect
        mock_compare.return_value = True
        mock_request.client.host = "1.2.3.4"

        result = verify_admin_secret(mock_request, "correct-secret")
        assert result == "correct-secret"

    @patch("src.auth.os.getenv")
    @patch("src.auth.secrets.compare_digest")
    def test_verify_admin_secret_ip_forbidden(self, mock_compare, mock_getenv, mock_request):
        def getenv_side_effect(key, default=None):
            if key == "ADMIN_SECRET":
                return "correct-secret"
            if key == "ADMIN_ALLOWED_IPS":
                return "5.6.7.8,9.10.11.12"
            return default

        mock_getenv.side_effect = getenv_side_effect
        mock_compare.return_value = True
        mock_request.client.host = "1.2.3.4"

        with pytest.raises(HTTPException) as excinfo:
            verify_admin_secret(mock_request, "correct-secret")

        assert excinfo.value.status_code == 403
        assert excinfo.value.detail == "IP not authorized for admin access"

    @patch("builtins.open", new_callable=mock_open)
    def test_log_admin_action(self, mock_file, mock_request):
        log_admin_action("test_action", "secret", mock_request, {"foo": "bar"})

        mock_file.assert_called_with("admin_audit.log", "a")
        handle = mock_file()
        handle.write.assert_called()
