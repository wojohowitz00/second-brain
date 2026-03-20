#!/usr/bin/env python3
"""
Tests for setup_wizard module.

TDD approach: Tests written FIRST, implementation follows.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import json


class TestSetupStep:
    """Test SetupStep enum."""

    def test_step_enum_has_all_steps(self):
        """SetupStep enum has all required steps."""
        from setup_wizard import SetupStep
        
        assert hasattr(SetupStep, "WELCOME")
        assert hasattr(SetupStep, "OLLAMA_CHECK")
        assert hasattr(SetupStep, "MODEL_DOWNLOAD")
        assert hasattr(SetupStep, "VAULT_CONFIG")
        assert hasattr(SetupStep, "SLACK_CREDENTIALS")
        assert hasattr(SetupStep, "COMPLETE")


class TestSetupWizard:
    """Test SetupWizard class."""

    @pytest.fixture
    def wizard(self, tmp_path):
        """Create wizard with temp config."""
        from setup_wizard import SetupWizard
        
        config_path = tmp_path / ".state" / "setup_state.json"
        return SetupWizard(config_path=config_path)

    def test_is_ollama_installed_true_when_installed(self, wizard):
        """is_ollama_installed() returns True when ollama command works."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="ollama version 0.1.0")
            
            result = wizard.is_ollama_installed()
            
            assert result is True

    def test_is_ollama_installed_false_when_missing(self, wizard):
        """is_ollama_installed() returns False when ollama command fails."""
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = FileNotFoundError("ollama not found")
            
            result = wizard.is_ollama_installed()
            
            assert result is False

    def test_is_model_available_checks_model_list(self, wizard):
        """is_model_available() checks if model is in Ollama list."""
        with patch.object(wizard, "_get_ollama_models") as mock_models:
            mock_models.return_value = ["llama3.2:latest", "mistral:latest"]
            
            result = wizard.is_model_available("llama3.2:latest")
            
            assert result is True

    def test_is_model_available_false_when_missing(self, wizard):
        """is_model_available() returns False when model not in list."""
        with patch.object(wizard, "_get_ollama_models") as mock_models:
            mock_models.return_value = ["mistral:latest"]
            
            result = wizard.is_model_available("llama3.2:latest")
            
            assert result is False

    def test_download_model_starts_pull(self, wizard):
        """download_model() starts ollama pull."""
        with patch("subprocess.Popen") as mock_popen:
            mock_process = MagicMock()
            mock_process.returncode = 0
            mock_process.wait.return_value = 0
            mock_process.stdout.readline.side_effect = [b"pulling...\n", b""]
            mock_popen.return_value = mock_process
            
            callback = Mock()
            result = wizard.download_model("llama3.2:latest", callback)
            
            mock_popen.assert_called_once()

    def test_validate_vault_path_true_for_valid_vault(self, tmp_path):
        """validate_vault_path() returns True for path with .obsidian."""
        from setup_wizard import SetupWizard
        
        # Create valid vault structure
        vault_path = tmp_path / "vault"
        vault_path.mkdir()
        (vault_path / ".obsidian").mkdir()
        
        wizard = SetupWizard(config_path=tmp_path / "config.json")
        result = wizard.validate_vault_path(vault_path)
        
        assert result is True

    def test_validate_vault_path_false_for_missing_obsidian(self, tmp_path):
        """validate_vault_path() returns False for path without .obsidian."""
        from setup_wizard import SetupWizard
        
        vault_path = tmp_path / "not_a_vault"
        vault_path.mkdir()
        
        wizard = SetupWizard(config_path=tmp_path / "config.json")
        result = wizard.validate_vault_path(vault_path)
        
        assert result is False

    def test_validate_slack_credentials_success(self, wizard):
        """validate_slack_credentials() returns True for valid token."""
        with patch("httpx.get") as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {"ok": True, "team": "Test Team"}
            mock_get.return_value = mock_response
            
            result = wizard.validate_slack_credentials("xoxb-test-token")
            
            assert result["valid"] is True
            assert result["team_name"] == "Test Team"

    def test_validate_slack_credentials_invalid(self, wizard):
        """validate_slack_credentials() returns False for invalid token."""
        with patch("httpx.get") as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {"ok": False, "error": "invalid_auth"}
            mock_get.return_value = mock_response
            
            result = wizard.validate_slack_credentials("invalid-token")
            
            assert result["valid"] is False

    def test_get_current_step_returns_correct_step(self, wizard):
        """get_current_step() returns current wizard step."""
        from setup_wizard import SetupStep
        
        # Default is WELCOME
        assert wizard.current_step == SetupStep.WELCOME

    def test_advance_step_moves_to_next(self, wizard):
        """advance_step() moves to next step."""
        from setup_wizard import SetupStep
        
        wizard.advance_step()
        
        assert wizard.current_step == SetupStep.OLLAMA_CHECK

    def test_can_advance_checks_prerequisites(self, wizard):
        """can_advance() checks if current step is complete."""
        from setup_wizard import SetupStep
        
        # Welcome step always can advance
        assert wizard.can_advance() is True
        
        # Move to OLLAMA_CHECK
        wizard.advance_step()
        
        # Can't advance unless Ollama is installed
        with patch.object(wizard, "is_ollama_installed", return_value=False):
            assert wizard.can_advance() is False

    def test_state_persistence(self, tmp_path):
        """Wizard saves and loads state correctly."""
        from setup_wizard import SetupWizard, SetupStep
        
        config_path = tmp_path / "state.json"
        
        # Create wizard and advance
        wizard1 = SetupWizard(config_path=config_path)
        wizard1.advance_step()
        wizard1.save_state()
        
        # Create new wizard, should load state
        wizard2 = SetupWizard(config_path=config_path)
        
        assert wizard2.current_step == SetupStep.OLLAMA_CHECK

    def test_skip_if_complete_skips_done_steps(self, tmp_path):
        """skip_if_complete() skips already completed steps."""
        from setup_wizard import SetupWizard, SetupStep
        
        config_path = tmp_path / "state.json"
        
        # Save state with some steps complete
        state = {
            "current_step": "VAULT_CONFIG",
            "completed_steps": ["WELCOME", "OLLAMA_CHECK", "MODEL_DOWNLOAD"]
        }
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.write_text(json.dumps(state))
        
        wizard = SetupWizard(config_path=config_path)
        
        assert wizard.current_step == SetupStep.VAULT_CONFIG


class TestConvenienceFunction:
    """Test module-level convenience function."""

    def test_run_setup_wizard_exists(self):
        """run_setup_wizard convenience function is exported."""
        from setup_wizard import run_setup_wizard
        
        assert callable(run_setup_wizard)
