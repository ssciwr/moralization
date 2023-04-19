from moralization import data_manager
import pandas as pd
import datasets
from transformers import AutoTokenizer  # , AutoModelForTokenClassification


class TransformersSetup:
    def __init__(self) -> None:
        pass

    def get_doc_dict(self, data_dir):
        # initialize spacy
        test_setup = spacy_model.SpacySetup(data_dir)
        self.doc_dict = test_setup.doc_dict

    def get_data_lists(self, example_name=None):
        # for now just select one source
        if example_name is None:
            example_name = sorted(list(self.doc_dict.keys()))[0]
        self.sentence_list = [
            [token.text for token in sent]
            for sent in self.doc_dict[example_name]["train"].sents
        ]
        self.token_list = [
            [token for token in sent]
            for sent in self.doc_dict[example_name]["train"].sents
        ]
        # initialize nested label list to 0
        self.label_list = [
            [0 for _ in sent] for sent in self.doc_dict[example_name]["train"].sents
        ]

    def generate_labels(self, example_name=None):
        # for now just select one source
        if example_name is None:
            example_name = sorted(list(self.doc_dict.keys()))[0]
        # generate the labels based on the current list of tokens
        # now set all Moralisierung, Moralisierung Kontext,
        # Moralisierung explizit, Moralisierung interpretativ, Moralisierung Weltwissen to 1
        selected_labels = [
            "Moralisierung",
            "Moralisierung Kontext",
            "Moralisierung Weltwissen",
            "Moralisierung explizit",
            "Moralisierung interpretativ",
        ]
        # create a list as long as tokens
        # we need to do this for all the data, not just train
        self.labels = [0 for _ in self.doc_dict[example_name]["train"]]
        for span in self.doc_dict[example_name]["train"].spans["task1"]:
            if span.label_ in selected_labels:
                self.labels[span.start + 1 : span.end + 1] = [1] * (
                    span.end - span.start
                )
                # mark the beginning of a span with 2
                self.labels[span.start] = 2

    def structure_labels(self):
        # labels now needs to be structured the same way as label_list
        # set the label at beginning of sentence to 2 if it is 1
        # also punctuation is included in the moralization label - we
        # definitely need to set those labels to -100
        j = 0
        for m in range(len(self.label_list)):
            for i in range(len(self.label_list[m])):
                self.label_list[m][i] = self.labels[j]
                if i == 0 and self.labels[j] == 1:
                    self.label_list[m][i] = 2
                if self.token_list[m][i].is_punct:
                    self.label_list[m][i] = -100
                j = j + 1

    def lists_to_df(self):
        # at this point we can write the text into a df to load into datasets
        # later it can be published as such on huggingface datasets
        # column heads are sentence, labels
        df = pd.DataFrame(
            zip(self.sentence_list, self.label_list), columns=["Sentences", "Labels"]
        )
        raw_data_set = datasets.Dataset.from_pandas(df)
        # split in train test
        self.train_test_set = raw_data_set.train_test_split(test_size=0.1)

    def init_model(self, model_name="bert-base-cased"):
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        except ValueError:
            raise ValueError(
                "Could not initiate tokenizer - please check your model name"
            )
        if not self.tokenizer.is_fast:
            raise ValueError(
                "Please use a different model that provices a fast tokenizer"
            )


if __name__ == "__main__":
    obj = TransformersSetup()
    obj.get_doc_dict("data/All_Data/XMI_11")
    obj.get_data_lists()
