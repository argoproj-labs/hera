"""Tests for the CLI generation utility functions."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from hera._cli.generate.util import (
    convert_code,
    expand_paths,
    filter_paths,
    write_output,
)


class TestCliGenerateUtil:
    """Tests for the CLI generation utility functions."""

    def test_expand_paths_file(self, tmp_path):
        """Test expanding a file path."""
        file_path = tmp_path / "test.py"
        file_path.write_text("# Test file")

        paths = list(expand_paths(file_path, {".py"}, recursive=False))
        assert len(paths) == 1
        assert paths[0] == file_path

    def test_expand_paths_directory_non_recursive(self, tmp_path):
        """Test expanding a directory path without recursion."""
        # Create test files
        (tmp_path / "file1.py").write_text("# Test file 1")
        (tmp_path / "file2.py").write_text("# Test file 2")
        (tmp_path / "file3.txt").write_text("Test file 3")

        # Create a subdirectory with a file
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        (subdir / "file4.py").write_text("# Test file 4")

        # Test expansion
        paths = list(expand_paths(tmp_path, {".py"}, recursive=False))
        assert len(paths) == 2
        assert tmp_path / "file1.py" in paths
        assert tmp_path / "file2.py" in paths
        assert tmp_path / "file3.txt" not in paths  # Wrong extension
        assert subdir / "file4.py" not in paths  # In subdirectory

    def test_expand_paths_directory_recursive(self, tmp_path):
        """Test expanding a directory path with recursion."""
        # Create test files
        (tmp_path / "file1.py").write_text("# Test file 1")
        (tmp_path / "file2.py").write_text("# Test file 2")
        (tmp_path / "file3.txt").write_text("Test file 3")

        # Create a subdirectory with a file
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        (subdir / "file4.py").write_text("# Test file 4")

        # Test expansion
        paths = list(expand_paths(tmp_path, {".py"}, recursive=True))
        assert len(paths) == 3
        assert tmp_path / "file1.py" in paths
        assert tmp_path / "file2.py" in paths
        assert tmp_path / "file3.txt" not in paths  # Wrong extension
        assert subdir / "file4.py" in paths  # In subdirectory, but recursive

    def test_filter_paths_no_filters(self):
        """Test filtering paths with no filters."""
        paths = [Path("file1.py"), Path("file2.py"), Path("file3.py")]
        filtered = list(filter_paths(paths, [], []))
        assert filtered == paths

    def test_filter_paths_include(self):
        """Test filtering paths with include filter."""
        paths = [Path("file1.py"), Path("file2.py"), Path("file3.py")]
        filtered = list(filter_paths(paths, ["*1*", "*3*"], []))
        assert len(filtered) == 2
        assert Path("file1.py") in filtered
        assert Path("file3.py") in filtered
        assert Path("file2.py") not in filtered

    def test_filter_paths_exclude(self):
        """Test filtering paths with exclude filter."""
        paths = [Path("file1.py"), Path("file2.py"), Path("file3.py")]
        filtered = list(filter_paths(paths, [], ["*2*"]))
        assert len(filtered) == 2
        assert Path("file1.py") in filtered
        assert Path("file3.py") in filtered
        assert Path("file2.py") not in filtered

    def test_filter_paths_include_and_exclude(self):
        """Test filtering paths with both include and exclude filters."""
        paths = [Path("file1.py"), Path("file2.py"), Path("file3.py"), Path("file4.py")]
        filtered = list(filter_paths(paths, ["*[1-3]*"], ["*2*"]))
        assert len(filtered) == 2
        assert Path("file1.py") in filtered
        assert Path("file3.py") in filtered
        assert Path("file2.py") not in filtered  # Excluded
        assert Path("file4.py") not in filtered  # Not included

    def test_write_output_to_stdout(self):
        """Test writing output to stdout."""
        input_paths_to_output = {
            "file1.py": "content1",
            "file2.py": "content2",
        }

        with patch("sys.stdout.write") as mock_write:
            write_output(
                output_path=None,
                input_paths_to_output=input_paths_to_output,
                extensions={".py"},
                default_extension=".py",
                join_delimiter="\n",
            )
            mock_write.assert_called_once()
            output = mock_write.call_args[0][0]
            assert "content1" in output
            assert "content2" in output

    def test_write_output_to_file(self, tmp_path):
        """Test writing output to a file."""
        output_file = tmp_path / "output.py"
        input_paths_to_output = {
            "file1.py": "content1",
            "file2.py": "content2",
        }

        write_output(
            output_path=output_file,
            input_paths_to_output=input_paths_to_output,
            extensions={".py"},
            default_extension=".py",
            join_delimiter="\n",
        )

        assert output_file.exists()
        content = output_file.read_text()
        assert "content1" in content
        assert "content2" in content

    def test_write_output_to_directory(self, tmp_path):
        """Test writing output to a directory."""
        output_dir = tmp_path / "output"
        input_paths_to_output = {
            "file1": "content1",
            "file2": "content2",
            "subdir/file3": "content3",
        }

        write_output(
            output_path=output_dir,
            input_paths_to_output=input_paths_to_output,
            extensions={".py"},
            default_extension=".py",
            join_delimiter="\n",
        )

        assert output_dir.exists()
        assert (output_dir / "file1.py").exists()
        assert (output_dir / "file2.py").exists()
        assert (output_dir / "subdir").exists()
        assert (output_dir / "subdir" / "file3.py").exists()

        assert (output_dir / "file1.py").read_text() == "content1"
        assert (output_dir / "file2.py").read_text() == "content2"
        assert (output_dir / "subdir" / "file3.py").read_text() == "content3"

    def test_convert_code(self):
        """Test converting code using loader and dumper functions."""
        paths = [Path("file1.py"), Path("file2.py")]

        # Mock options
        options = MagicMock()
        options.from_ = Path(".")
        options.include = []
        options.exclude = []
        options.recursive = False
        options.flatten = False

        # Mock loader and dumper functions
        def loader_func(path):
            if path == Path("file1.py"):
                return ["workflow1", "workflow2"]
            else:
                return ["workflow3"]

        def dumper_func(workflow):
            return f"dumped_{workflow}"

        result = convert_code(
            paths=paths,
            options=options,
            loader_func=loader_func,
            dumper_func=dumper_func,
            join_delimiter="\n",
        )

        assert "file1.py" in result
        assert "file2.py" in result
        assert result["file1.py"] == "dumped_workflow1\ndumped_workflow2"
        assert result["file2.py"] == "dumped_workflow3"

    def test_convert_code_recursive_flatten(self):
        """Test converting code with recursive and flatten options."""
        paths = [Path("dir1/file1.py"), Path("dir2/file2.py")]

        # Mock options
        options = MagicMock()
        options.from_ = Path(".")
        options.include = []
        options.exclude = []
        options.recursive = True
        options.flatten = True

        # Mock loader and dumper functions
        def loader_func(path):
            if path == Path("dir1/file1.py"):
                return ["workflow1"]
            else:
                return ["workflow2"]

        def dumper_func(workflow):
            return f"dumped_{workflow}"

        result = convert_code(
            paths=paths,
            options=options,
            loader_func=loader_func,
            dumper_func=dumper_func,
            join_delimiter="\n",
        )

        assert "file1.py" in result
        assert "file2.py" in result
        assert result["file1.py"] == "dumped_workflow1"
        assert result["file2.py"] == "dumped_workflow2"

    def test_convert_code_recursive_no_flatten(self):
        """Test converting code with recursive but no flatten option."""
        paths = [Path("dir1/file1.py"), Path("dir2/file2.py")]

        # Mock options
        options = MagicMock()
        options.from_ = Path(".")
        options.include = []
        options.exclude = []
        options.recursive = True
        options.flatten = False

        # Mock loader and dumper functions
        def loader_func(path):
            if path == Path("dir1/file1.py"):
                return ["workflow1"]
            else:
                return ["workflow2"]

        def dumper_func(workflow):
            return f"dumped_{workflow}"

        result = convert_code(
            paths=paths,
            options=options,
            loader_func=loader_func,
            dumper_func=dumper_func,
            join_delimiter="\n",
        )

        assert "dir1/file1.py" in result
        assert "dir2/file2.py" in result
        assert result["dir1/file1.py"] == "dumped_workflow1"
        assert result["dir2/file2.py"] == "dumped_workflow2"

    def test_convert_code_empty_result(self):
        """Test converting code with no results from loader."""
        paths = [Path("file1.py"), Path("file2.py")]

        # Mock options
        options = MagicMock()
        options.from_ = Path(".")
        options.include = []
        options.exclude = []
        options.recursive = False
        options.flatten = False

        # Mock loader and dumper functions
        def loader_func(path):
            return []

        def dumper_func(workflow):
            return f"dumped_{workflow}"

        result = convert_code(
            paths=paths,
            options=options,
            loader_func=loader_func,
            dumper_func=dumper_func,
            join_delimiter="\n",
        )

        assert result == {}
