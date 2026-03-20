#!/usr/bin/env python3
"""
First-run setup wizard for Second Brain.

Guides new users through:
1. Ollama installation check
2. Model download
3. Vault path configuration
4. Slack credentials validation
"""

import json
import logging
import subprocess
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import Callable, Optional, List

import httpx

# Configure module logger
logger = logging.getLogger(__name__)

# Default configuration
DEFAULT_MODEL = "llama3.2:latest"
DEFAULT_VAULT_PATH = Path.home() / "Library" / "Mobile Documents" / "iCloud~md~obsidian" / "Documents"


class SetupStep(Enum):
    """Wizard step enumeration."""
    WELCOME = auto()
    OLLAMA_CHECK = auto()
    MODEL_DOWNLOAD = auto()
    VAULT_CONFIG = auto()
    SLACK_CREDENTIALS = auto()
    COMPLETE = auto()


@dataclass
class StepResult:
    """Result of a wizard step."""
    success: bool
    message: str
    data: Optional[dict] = None


class SetupWizard:
    """
    First-run setup wizard for Second Brain.
    
    Guides users through configuration without CLI knowledge.
    """
    
    # Step order for iteration
    STEP_ORDER = [
        SetupStep.WELCOME,
        SetupStep.OLLAMA_CHECK,
        SetupStep.MODEL_DOWNLOAD,
        SetupStep.VAULT_CONFIG,
        SetupStep.SLACK_CREDENTIALS,
        SetupStep.COMPLETE,
    ]
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize setup wizard.
        
        Args:
            config_path: Path to state file (default: .state/setup_state.json)
        """
        if config_path is None:
            config_path = Path(__file__).parent / ".state" / "setup_state.json"
        
        self.config_path = Path(config_path)
        self._current_step = SetupStep.WELCOME
        self._completed_steps: List[SetupStep] = []
        self._config: dict = {}
        
        self._load_state()
    
    @property
    def current_step(self) -> SetupStep:
        """Get current wizard step."""
        return self._current_step
    
    def _load_state(self):
        """Load wizard state from file."""
        try:
            if self.config_path.exists():
                data = json.loads(self.config_path.read_text())
                
                # Restore current step
                step_name = data.get("current_step", "WELCOME")
                self._current_step = SetupStep[step_name]
                
                # Restore completed steps
                completed = data.get("completed_steps", [])
                self._completed_steps = [SetupStep[s] for s in completed]
                
                # Restore config
                self._config = data.get("config", {})
                
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.warning(f"Failed to load wizard state: {e}")
            self._current_step = SetupStep.WELCOME
    
    def save_state(self):
        """Save wizard state to file."""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                "current_step": self._current_step.name,
                "completed_steps": [s.name for s in self._completed_steps],
                "config": self._config,
            }
            
            self.config_path.write_text(json.dumps(data, indent=2))
            
        except IOError as e:
            logger.error(f"Failed to save wizard state: {e}")
    
    def advance_step(self):
        """Move to next step in wizard."""
        current_index = self.STEP_ORDER.index(self._current_step)
        
        # Mark current step as complete
        if self._current_step not in self._completed_steps:
            self._completed_steps.append(self._current_step)
        
        # Move to next step
        if current_index < len(self.STEP_ORDER) - 1:
            self._current_step = self.STEP_ORDER[current_index + 1]
        
        self.save_state()
    
    def can_advance(self) -> bool:
        """Check if current step can be advanced."""
        step = self._current_step
        
        if step == SetupStep.WELCOME:
            return True
        
        if step == SetupStep.OLLAMA_CHECK:
            return self.is_ollama_installed()
        
        if step == SetupStep.MODEL_DOWNLOAD:
            return self.is_model_available(DEFAULT_MODEL)
        
        if step == SetupStep.VAULT_CONFIG:
            vault_path = self._config.get("vault_path")
            return vault_path and self.validate_vault_path(Path(vault_path))
        
        if step == SetupStep.SLACK_CREDENTIALS:
            token = self._config.get("slack_token")
            if token:
                result = self.validate_slack_credentials(token)
                return result.get("valid", False)
            return False
        
        if step == SetupStep.COMPLETE:
            return True
        
        return False
    
    def is_ollama_installed(self) -> bool:
        """Check if Ollama is installed."""
        try:
            result = subprocess.run(
                ["ollama", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def _get_ollama_models(self) -> List[str]:
        """Get list of available Ollama models."""
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode != 0:
                return []
            
            # Parse model list (skip header line)
            models = []
            for line in result.stdout.strip().split("\n")[1:]:
                if line.strip():
                    model_name = line.split()[0]
                    models.append(model_name)
            return models
            
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return []
    
    def is_model_available(self, model_name: str) -> bool:
        """Check if model is available in Ollama."""
        models = self._get_ollama_models()
        
        # Check exact match or prefix match
        for model in models:
            if model == model_name or model.startswith(model_name.split(":")[0]):
                return True
        return False
    
    def download_model(
        self,
        model_name: str,
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> bool:
        """
        Download model using ollama pull.
        
        Args:
            model_name: Model to download
            progress_callback: Called with progress messages
            
        Returns:
            True if download succeeded
        """
        try:
            process = subprocess.Popen(
                ["ollama", "pull", model_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            
            while True:
                line = process.stdout.readline()
                if not line:
                    break
                
                if progress_callback:
                    progress_callback(line.decode().strip())
            
            process.wait()
            return process.returncode == 0
            
        except (FileNotFoundError, subprocess.SubprocessError) as e:
            logger.error(f"Failed to download model: {e}")
            return False
    
    def validate_vault_path(self, path: Path) -> bool:
        """
        Validate that path is an Obsidian vault.
        
        Args:
            path: Path to validate
            
        Returns:
            True if path contains .obsidian directory
        """
        path = Path(path)
        obsidian_dir = path / ".obsidian"
        return obsidian_dir.is_dir()
    
    def validate_slack_credentials(self, token: str) -> dict:
        """
        Validate Slack token by calling auth.test.
        
        Args:
            token: Slack Bot token (xoxb-...)
            
        Returns:
            Dict with 'valid' (bool) and 'team_name' if valid
        """
        try:
            response = httpx.get(
                "https://slack.com/api/auth.test",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10
            )
            data = response.json()
            
            if data.get("ok"):
                return {
                    "valid": True,
                    "team_name": data.get("team", data.get("team_id")),
                    "user": data.get("user"),
                }
            else:
                return {
                    "valid": False,
                    "error": data.get("error", "Unknown error"),
                }
                
        except (httpx.HTTPError, json.JSONDecodeError) as e:
            return {
                "valid": False,
                "error": str(e),
            }
    
    def run_step(self, step: SetupStep) -> StepResult:
        """
        Run a specific wizard step.
        
        Args:
            step: Step to run
            
        Returns:
            StepResult with success status and message
        """
        if step == SetupStep.WELCOME:
            return StepResult(
                success=True,
                message="Welcome to Second Brain setup!"
            )
        
        if step == SetupStep.OLLAMA_CHECK:
            if self.is_ollama_installed():
                return StepResult(
                    success=True,
                    message="Ollama is installed"
                )
            return StepResult(
                success=False,
                message="Please install Ollama from https://ollama.ai"
            )
        
        if step == SetupStep.MODEL_DOWNLOAD:
            if self.is_model_available(DEFAULT_MODEL):
                return StepResult(
                    success=True,
                    message=f"Model {DEFAULT_MODEL} is available"
                )
            return StepResult(
                success=False,
                message=f"Model {DEFAULT_MODEL} needs to be downloaded"
            )
        
        if step == SetupStep.VAULT_CONFIG:
            vault_path = self._config.get("vault_path")
            if vault_path and self.validate_vault_path(Path(vault_path)):
                return StepResult(
                    success=True,
                    message=f"Vault configured: {vault_path}"
                )
            return StepResult(
                success=False,
                message="Please configure vault path"
            )
        
        if step == SetupStep.SLACK_CREDENTIALS:
            token = self._config.get("slack_token")
            if token:
                result = self.validate_slack_credentials(token)
                if result.get("valid"):
                    return StepResult(
                        success=True,
                        message=f"Connected to Slack: {result.get('team_name')}",
                        data=result
                    )
            return StepResult(
                success=False,
                message="Please configure Slack credentials"
            )
        
        if step == SetupStep.COMPLETE:
            return StepResult(
                success=True,
                message="Setup complete! Starting Second Brain..."
            )
        
        return StepResult(success=False, message="Unknown step")
    
    def run(self) -> bool:
        """
        Run the complete wizard.
        
        Returns:
            True if wizard completed successfully
        """
        while self._current_step != SetupStep.COMPLETE:
            result = self.run_step(self._current_step)
            
            if not result.success:
                logger.info(f"Step {self._current_step.name} needs attention: {result.message}")
                return False
            
            self.advance_step()
        
        return True


def run_setup_wizard() -> bool:
    """
    Run the setup wizard.
    
    Returns:
        True if setup completed successfully
    """
    wizard = SetupWizard()
    return wizard.run()
