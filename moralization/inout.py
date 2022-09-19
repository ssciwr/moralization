from cassis import load_typesystem, load_cas_from_xmi
import glob
import os
import importlib_resources
from moralization import analyse

pkg = importlib_resources.files("moralization")


class InputOutput:
    """Namespace class to handle input and output."""

    # this dict can be extended to contain more file formats
    input_type = {"xmi": load_cas_from_xmi}

    @staticmethod
    def get_file_type(filename):
        return filename.strip().split(".")[-1]

    @staticmethod
    def read_typesystem(filename="") -> object:
        # read in the file system types
        if filename == "":
            filename = pkg / "data" / "TypeSystem.xml"
        with open(filename, "rb") as f:
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
    def get_input_dir(dir_path: str) -> dict:
        """Get a list of input files from a given directory. Currently only xmi files.
        Read the TypeSystem file from the provided data directory.
        """
        ### load multiple files into a list of dictionaries
        ts_file = glob.glob(os.path.join(dir_path, "TypeSystem.xml"))
        if len(ts_file) == 1:
            ts = InputOutput.read_typesystem(ts_file[0])
        elif len(ts_file) == 0:
            print(
                f"No Typesystem found in {os.path.abspath(dir_path)}, trying default location"
            )
            if not glob.glob(str(pkg / "data" / "TypeSystem.xml")):
                raise FileNotFoundError("No typesystem found in ", pkg / "data")
            ts = InputOutput.read_typesystem(pkg / "data" / "TypeSystem.xml")
        else:
            raise Warning("Multiple typesystems found. Please provide only one.")

        data_files = glob.glob(os.path.join(dir_path, "*.xmi"))
        data_dict = {}
        for data_file in data_files:
            # get the file type dynamically
            file_type = InputOutput.get_file_type(data_file)
            # the wikipediadiskussionen file breaks as it has an invalid xmi charakter.
            # if data_file != "../data/Wikipediadiskussionen-neg-BD-neu-optimiert-CK.xmi":
            with open(data_file, "rb") as f:
                cas = InputOutput.input_type[file_type](f, typesystem=ts)
            data_dict[os.path.basename(data_file).split(".xmi")[0]] = {
                "data": analyse.sort_spans(cas, ts),
                "file_type": os.path.basename(data_file).split(".")[1],
            }
        return data_dict


if __name__ == "__main__":
    # data = InputOutput.get_input_file(
    # "moralization/data/Gerichtsurteile-pos-AW-neu-optimiert-BB.xmi"
    # )
    data_dict = InputOutput.get_input_dir("data/")
    df_instances = analyse.AnalyseOccurence(data_dict, mode="instances").df
    print(df_instances)
    # I checked these numbers using test_data-trimmed_version_of-Gerichtsurteile-neg-AW-neu-optimiert-BB
    # and it looks correct
    #
    #
    # this df can now easily be filtered.
    print(df_instances.loc["KAT2Subjektive_Ausdrcke"])
    # checked these numbers and they look correct
    #
    df_spans = analyse.AnalyseOccurence(data_dict, mode="spans").df
    print(df_spans)
    # checked these numbers and they look correct
    #
    # analyse.get_overlap_percent(
    # "Forderer:in", "Neutral", data_dict, "Gerichtsurteile-neg-AW-neu-optimiert-BB"
    #     )
