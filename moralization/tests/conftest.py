import pytest
from moralization import input_data
import pathlib


def _data_path_fixture(dir_path):
    @pytest.fixture
    def _fixture():
        return dir_path

    return _fixture


def _doc_dict_fixture(dir_path):
    @pytest.fixture
    def _fixture():
        return input_data.InputOutput.read_data(dir_path)

    return _fixture


dir_path = pathlib.Path(__file__).parents[1].resolve() / "data"
data_dir = _data_path_fixture(dir_path)
doc_dict = _doc_dict_fixture(dir_path)

ts_file = _data_path_fixture(dir_path / "TypeSystem.xml")
data_file = _data_path_fixture(
    dir_path / "test_data-trimmed_version_of-Interviews-pos-SH-neu-optimiert-AW.xmi"
)
config_file = _data_path_fixture(dir_path / "config.cfg")
