import io
import os

from django.core.management.base import CommandError

import pytest

from django_unicorn.management.commands.startunicorn import Command


def test_handle_no_base_dir():
    with pytest.raises(CommandError):
        Command().handle()


def test_handle_no_args(settings):
    settings.BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    with pytest.raises(CommandError):
        Command().handle()


def test_handle_new_app(settings, tmp_path, monkeypatch, capsys):
    settings.BASE_DIR = tmp_path

    # Reply "y" then "n"
    monkeypatch.setattr("sys.stdin", io.StringIO("y\nn\n"))

    app_name = "test123"
    component_names = ["hello-world"]
    Command().handle(app_name=app_name, component_names=component_names)

    assert (tmp_path / f"{app_name}/components/__init__.py").exists()
    assert (tmp_path / f"{app_name}/components/hello_world.py").exists()
    assert (tmp_path / f"{app_name}/templates/unicorn/hello-world.html").exists()

    captured = capsys.readouterr()
    assert "Starring the GitHub repo " in captured.out
    assert f'Make sure to add `"{app_name}",` to your' in captured.out


def test_handle_existing_app(settings, tmp_path, monkeypatch, capsys):
    settings.BASE_DIR = tmp_path

    app_name = "test123"
    (tmp_path / app_name).mkdir()

    # Reply "y" then "n"
    monkeypatch.setattr("sys.stdin", io.StringIO("y\nn\n"))

    component_names = ["hello-world"]
    Command().handle(app_name=app_name, component_names=component_names)

    assert (tmp_path / f"{app_name}/components/__init__.py").exists()
    assert (tmp_path / f"{app_name}/components/hello_world.py").exists()
    assert (tmp_path / f"{app_name}/templates/unicorn/hello-world.html").exists()

    captured = capsys.readouterr()
    assert "Starring the GitHub repo " in captured.out
    assert "That's a bummer" in captured.out
    assert "Make sure to add " not in captured.out


def test_handle_existing_component(settings, tmp_path, monkeypatch, capsys):
    settings.BASE_DIR = tmp_path

    app_name = "test123"
    (tmp_path / app_name).mkdir()
    (tmp_path / app_name / "components").mkdir()

    # Reply "y"
    monkeypatch.setattr("sys.stdin", io.StringIO("y\n"))

    component_names = ["hello-world"]
    Command().handle(app_name=app_name, component_names=component_names)

    assert (tmp_path / f"{app_name}/components/__init__.py").exists()
    assert (tmp_path / f"{app_name}/components/hello_world.py").exists()
    assert (tmp_path / f"{app_name}/templates/unicorn/hello-world.html").exists()

    captured = capsys.readouterr()
    assert "Starring the GitHub repo " not in captured.out
    assert "Make sure to add " not in captured.out


def test_handle_existing_templates(settings, tmp_path, monkeypatch, capsys):
    settings.BASE_DIR = tmp_path

    app_name = "test123"
    (tmp_path / app_name).mkdir()
    (tmp_path / app_name / "components").mkdir()
    (tmp_path / app_name / "templates").mkdir()

    # Reply "y"
    monkeypatch.setattr("sys.stdin", io.StringIO("y\n"))

    component_names = ["hello-world"]
    Command().handle(app_name=app_name, component_names=component_names)

    assert (tmp_path / f"{app_name}/components/__init__.py").exists()
    assert (tmp_path / f"{app_name}/components/hello_world.py").exists()
    assert (tmp_path / f"{app_name}/templates/unicorn/hello-world.html").exists()

    captured = capsys.readouterr()
    assert "Starring the GitHub repo " not in captured.out
    assert "Make sure to add " not in captured.out


def test_handle_existing_unicorn_templates(settings, tmp_path, monkeypatch, capsys):
    settings.BASE_DIR = tmp_path

    app_name = "test123"
    (tmp_path / app_name).mkdir()
    (tmp_path / app_name / "components").mkdir()
    (tmp_path / app_name / "templates").mkdir()
    (tmp_path / app_name / "templates" / "unicorn").mkdir()

    # Reply "y"
    monkeypatch.setattr("sys.stdin", io.StringIO("y\n"))

    component_names = ["hello-world"]
    Command().handle(app_name=app_name, component_names=component_names)

    assert (tmp_path / f"{app_name}/components/__init__.py").exists()
    assert (tmp_path / f"{app_name}/components/hello_world.py").exists()
    assert (tmp_path / f"{app_name}/templates/unicorn/hello-world.html").exists()

    captured = capsys.readouterr()
    assert "Starring the GitHub repo " not in captured.out
    assert "Make sure to add " not in captured.out


def test_handle_reply_no(settings, tmp_path, monkeypatch, capsys):
    settings.BASE_DIR = tmp_path

    # Reply "n"
    monkeypatch.setattr("sys.stdin", io.StringIO("n\n"))

    app_name = "test123"
    component_names = ["hello-world"]
    Command().handle(app_name=app_name, component_names=component_names)

    assert not (tmp_path / f"{app_name}/components/__init__.py").exists()
    assert not (tmp_path / f"{app_name}/components/hello_world.py").exists()
    assert not (tmp_path / f"{app_name}/templates/unicorn/hello-world.html").exists()

    captured = capsys.readouterr()
    assert "Make sure to add " not in captured.out

    # Reply "no"
    monkeypatch.setattr("sys.stdin", io.StringIO("no\n"))

    Command().handle(app_name=app_name, component_names=component_names)

    assert not (tmp_path / f"{app_name}/components/__init__.py").exists()
    assert not (tmp_path / f"{app_name}/components/hello_world.py").exists()
    assert not (tmp_path / f"{app_name}/templates/unicorn/hello-world.html").exists()

    captured = capsys.readouterr()
    assert "Make sure to add " not in captured.out


def test_handle_reply_yes_star(settings, tmp_path, monkeypatch, capsys):
    settings.BASE_DIR = tmp_path

    # Reply "y" then "y"
    monkeypatch.setattr("sys.stdin", io.StringIO("y\ny\n"))

    # Patch opening a webbrowser
    def webbrowser_open(url, **kwargs):
        assert url == "https://github.com/adamghill/django-unicorn"

    monkeypatch.setattr("webbrowser.open", webbrowser_open)

    app_name = "test123"
    component_names = ["hello-world"]

    Command().handle(app_name=app_name, component_names=component_names)

    assert (tmp_path / f"{app_name}/components/__init__.py").exists()
    assert (tmp_path / f"{app_name}/components/hello_world.py").exists()
    assert (tmp_path / f"{app_name}/templates/unicorn/hello-world.html").exists()

    captured = capsys.readouterr()
    assert "Starring the GitHub repo " in captured.out
    assert "That's a bummer" not in captured.out
    assert "Thank you for helping spread the" in captured.out
    assert f'Make sure to add `"{app_name}",` to your' in captured.out
