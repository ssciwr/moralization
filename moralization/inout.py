from cassis import load_typesystem, load_cas_from_xmi
import pathlib
import importlib_resources
import logging
from moralization import analyse
from lxml.etree import XMLSyntaxError

pkg = importlib_resources.files("moralization")


class InputOutput:
    """Namespace class to handle input and output."""

    # this dict can be extended to contain more file formats
    input_type = {"xmi": load_cas_from_xmi}

    @staticmethod
    def get_file_type(filename):
        return pathlib.Path(filename).suffix[1:]

    @staticmethod
    def read_typesystem() -> object:
        # read in the file system types
        myfile = pkg / "data" / "TypeSystem.xml"
        with open(myfile, "rb") as f:
            ts = load_typesystem(f)
        return ts

    @staticmethod
    def get_input_file(filename: str) -> object:
        """Read in the input file. Currently only xmi file format."""
        ts = InputOutput.read_typesystem()
        file_type = InputOutput.get_file_type(filename)
        # read the actual data file
        with open(filename, "rb") as f:
            data = InputOutput.input_type[file_type](f, typesystem=ts)
        return data

    @staticmethod
    def get_input_dir(dir: str) -> dict:
        "Get a list of input files from a given directory. Currently only xmi files."
        ### load multiple files into a list of dictionaries
        ts = InputOutput.read_typesystem()
        dir_path = pathlib.Path(dir)
        if not dir_path.is_dir():
            raise RuntimeError(f"Path {dir_path} does not exist")
        data_files = dir_path.glob("*.xmi")
        if not data_files:
            raise RuntimeError(f"No input files found in {dir_path}")
        data_dict = {}
        for data_file in data_files:
            # get the file type dynamically
            file_type = InputOutput.get_file_type(data_file)
            try:
                with open(data_file, "rb") as f:
                    cas = InputOutput.input_type[file_type](f, typesystem=ts)
                data_dict[data_file.stem] = {
                    "data": analyse.sort_spans(cas, ts),
                    "file_type": file_type,
                    "sofa": cas.sofa_string,  # note: use .sofa_string not .get_sofa() as the latter removes \n and similar markers
                }
            except XMLSyntaxError as e:
                logging.warning(
                    f"WARNING: skipping file '{data_file}' due to XMLSyntaxError: {e}"
                )

        return data_dict


if __name__ == "__main__":
    data_dict = InputOutput.get_input_dir("data/")
    df_instances = analyse.AnalyseOccurence(data_dict, mode="instances").df
    df_instances.to_csv("instances_out.csv")
    # this df can now easily be filtered.
    # print(df_instances.loc["KAT2-Subjektive Ausdrücke"])
    df_spans = analyse.AnalyseOccurence(data_dict, mode="spans").df
    df_spans.to_csv("spans_out.csv")
    #
    # analyse.get_overlap_percent(
    # "Forderer:in", "Neutral", data_dict, "Gerichtsurteile-neg-AW-neu-optimiert-BB"
    #     )
