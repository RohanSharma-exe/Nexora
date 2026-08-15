import os

from nexora.config import load_environment


def test_load_environment_reads_project_dotenv(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("NVIDIA_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    (tmp_path / ".env").write_text(
        "NVIDIA_API_KEY=test-nvidia-key\nGEMINI_API_KEY=test-gemini-key\n",
        encoding="utf-8",
    )

    load_environment()

    assert os.environ["NVIDIA_API_KEY"] == "test-nvidia-key"
    assert os.environ["GEMINI_API_KEY"] == "test-gemini-key"
