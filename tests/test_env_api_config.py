"""Tests for environment variable API configuration functionality."""

from __future__ import annotations

import os

import pytest
from pydantic import SecretStr

from kimi_cli.config import LLMModel, LLMProvider
from kimi_cli.llm import augment_provider_with_env_vars, get_available_models_from_env


def test_augment_provider_with_kimi_env_vars():
    """Test augmenting provider with KIMI environment variables."""
    provider = LLMProvider(type="kimi", base_url="", api_key=SecretStr(""))
    model = LLMModel(provider="", model="", max_context_size=100_000)

    os.environ["KIMI_BASE_URL"] = "https://api.test.com"
    os.environ["KIMI_API_KEY"] = "test_key_123"
    os.environ["KIMI_MODEL_NAME"] = "test-model"
    os.environ["KIMI_MODEL_MAX_CONTEXT_SIZE"] = "200000"
    os.environ["KIMI_MODEL_CAPABILITIES"] = "thinking,image_in"

    try:
        applied = augment_provider_with_env_vars(provider, model)

        assert provider.base_url == "https://api.test.com"
        assert provider.api_key.get_secret_value() == "test_key_123"
        assert model.model == "test-model"
        assert model.max_context_size == 200000
        assert model.capabilities == {"thinking", "image_in"}
        assert "KIMI_BASE_URL" in applied
        assert "KIMI_API_KEY" in applied
        assert "KIMI_MODEL_NAME" in applied
    finally:
        os.environ.pop("KIMI_BASE_URL", None)
        os.environ.pop("KIMI_API_KEY", None)
        os.environ.pop("KIMI_MODEL_NAME", None)
        os.environ.pop("KIMI_MODEL_MAX_CONTEXT_SIZE", None)
        os.environ.pop("KIMI_MODEL_CAPABILITIES", None)


def test_augment_provider_with_openai_env_vars():
    """Test augmenting provider with OpenAI environment variables."""
    provider = LLMProvider(type="openai_legacy", base_url="", api_key=SecretStr(""))
    model = LLMModel(provider="", model="", max_context_size=100_000)

    os.environ["OPENAI_BASE_URL"] = "https://api.openai.com"
    os.environ["OPENAI_API_KEY"] = "sk-test-key"
    os.environ["OPENAI_MODEL_NAME"] = "gpt-4"

    try:
        applied = augment_provider_with_env_vars(provider, model)

        assert provider.base_url == "https://api.openai.com"
        assert provider.api_key.get_secret_value() == "sk-test-key"
        assert model.model == "gpt-4"
        assert "OPENAI_BASE_URL" in applied
        assert "OPENAI_API_KEY" in applied
        assert "OPENAI_MODEL_NAME" in applied
    finally:
        os.environ.pop("OPENAI_BASE_URL", None)
        os.environ.pop("OPENAI_API_KEY", None)
        os.environ.pop("OPENAI_MODEL_NAME", None)


def test_get_available_models_from_env():
    """Test getting available models from environment variables."""
    os.environ["KIMI_MODEL_LIST"] = "model1,model2,model3"

    try:
        models = get_available_models_from_env()
        assert models == ["model1", "model2", "model3"]
    finally:
        os.environ.pop("KIMI_MODEL_LIST", None)


def test_get_available_models_from_env_alternative_name():
    """Test getting available models from KIMI_AVAILABLE_MODELS environment variable."""
    os.environ["KIMI_AVAILABLE_MODELS"] = "model-a,model-b"

    try:
        models = get_available_models_from_env()
        assert models == ["model-a", "model-b"]
    finally:
        os.environ.pop("KIMI_AVAILABLE_MODELS", None)


def test_get_available_models_from_env_not_set():
    """Test getting available models when environment variable is not set."""
    os.environ.pop("KIMI_MODEL_LIST", None)
    os.environ.pop("KIMI_AVAILABLE_MODELS", None)

    models = get_available_models_from_env()
    assert models is None


def test_get_available_models_from_env_with_spaces():
    """Test getting available models with spaces in the list."""
    os.environ["KIMI_MODEL_LIST"] = "model1, model2 , model3"

    try:
        models = get_available_models_from_env()
        assert models == ["model1", "model2", "model3"]
    finally:
        os.environ.pop("KIMI_MODEL_LIST", None)

