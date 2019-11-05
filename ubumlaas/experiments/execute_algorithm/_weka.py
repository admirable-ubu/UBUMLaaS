import sklearn
import sklearn.base
import sklearn.cluster
import sklearn.linear_model
import sklearn.metrics
import sklearn.ensemble
import sklearn.neighbors
import sklearn.model_selection
import sklearn.preprocessing
import sklearn.multiclass

import pandas as pd
import numpy as np
import json

import weka.core.jvm as jvm
from weka.classifiers import Classifier
from weka.core.converters import Loader
import weka.core.serialization as serialization

import tempfile

from ubumlaas.experiments.execute_algorithm import Abstract_execute


class Execute_weka(Abstract_execute):

    def __init__(self, experiment):
        """Initizialice attributes from experiment dict and starts Java Virtual Machine

        Arguments:
            experiment {dict} -- experiment dictionary
        """
        Abstract_execute.__init__(self, experiment)

        self.y_uniques = None
        if not jvm.started:
            jvm.start(packages=True)

    def create_weka_dataset(self, X, y = None):
        """Create weka dataset using temporaly file

        Arguments:
            X {array like} -- non target class instances
            y {array like} -- target class instances

        Returns:
            java object wrapped -- weka dataset
        """
        try:
            # Create new temporal file
            temp = tempfile.NamedTemporaryFile()
            # Concat X and y. Write csv to temporaly file.

            if y is None:
                y = pd.DataFrame(["?"]*X.shape[0], columns=self.experiment_configuration["target"])
            X.reset_index(drop=True, inplace=True)
            y.reset_index(drop=True, inplace=True)
            dataframe = pd.concat([X, y], axis=1, ignore_index=True)
            dataframe.to_csv(temp.name, index=None)
            options = None
            if self.y_uniques is not None:
                options = ["-L", "{}:{}".format(dataframe.shape[1],
                           ",".join(map(str, self.y_uniques)))]
            if not self.is_classification():
                options = ["-R", "last"]
            loader = Loader(classname="weka.core.converters.CSVLoader",
                            options=options)
            data = loader.load_file(temp.name)
            # Last column of data is target
            data.class_is_last()
        finally:
            temp.close()
        return data

    @staticmethod
    def create_weka_parameters(alg_name, alg_config, baseconf=None):
        """Create weka command line parameter based in the algorithm name and algorithm configuration

        Arguments:
            alg_name {str} -- algortihm name, for example: weka.classifiers.trees.J48
            alg_config {dict} -- algorithm configuration

        Keyword Arguments:
            baseconf {dict} -- base configuration of the algortihm configuration (default: {None})

        Returns:
            [list] -- list of the command line parameter
        """
        if baseconf is None:
            from ubumlaas.models import get_algorithm_by_name
            exp = get_algorithm_by_name(alg_name)
            baseconf = json.loads(exp.config)

        lincom = []

        for i in alg_config:
            parameter = alg_config[i]
            if type(parameter) == dict:
                sub_list = Execute_weka.\
                    create_weka_parameters(parameter["alg_name"],
                                           parameter["parameters"])
                lincom += [baseconf[i]["command"], parameter["alg_name"], "--"]
                lincom += sub_list
            else:
                if parameter is not False:
                    lincom.append(baseconf[i]["command"])
                if not isinstance(parameter, bool):
                    lincom.append(str(parameter))

        return lincom

    def create_model(self):
        """Create the model with experiment

        Returns:
            [java object] -- model with the experiment configuration
        """
        lincom = Execute_weka.\
            create_weka_parameters(self.algorithm_name,
                                   self.algorithm_configuration,
                                   self.configuration)
        return Classifier(classname=self.algorithm_name, options=lincom)

    def serialize(self, model, path):
        """Serialize the java model in specific path

        Arguments:
            model {java object} -- the model to serialize
            path {str} -- path to save the model serialized
        """
        serialization.write(path, model)

    def deserialize(self, path):
        """Deserialize the model in the specific path

        Arguments:
            path {str} -- path with the model file saved

        Returns:
            [java object] -- model deserialized
        """
        return Classifier(jobject=serialization.read(path))

    def train(self, model, X, y):
        """Train the model with attributes columns (X) and targets columns (Y)

        Arguments:
            model {object} -- model to train
            X {DataFrame} -- attributes columns
            y {Series} -- target column
        """
        data = self.create_weka_dataset(X, y)
        model.build_classifier(data)

    def predict(self, model, X):
        """Predict with X columns values using the model

        Arguments:
            model {object} -- model to use for predictions
            X {DataFrame} -- dataframe with X columns values

        Returns:
            list, list -- predictions values, distribution class if is classified or None otherwise
        """
        data_test = self.create_weka_dataset(X)
        y_score = None
        if self.is_classification():
            y_pred = [data_test.class_attribute.value(
                            int(model.classify_instance(instance))
                        )for instance in data_test
                      ]

            y_score = model.distributions_for_instances(data_test)
            try:  # Trying to convert to int
                y_pred = [float(pred) for pred in y_pred]
            except ValueError:
                pass
        else:
            y_pred = [model.classify_instance(instance)
                      for instance in data_test
                      ]
            
        return y_pred, y_score

    def close(self):
        """Closes Java Virtual Machine
        """
        jvm.stop()

    def find_y_uniques(self, y):
        """If the algorithm is classification, finds uniques nominal values

        Arguments:
            y {Series} -- target column
        """
        if self.is_classification():
            uniques = np.unique(y.values)
            uniques.sort()
            self.y_uniques = uniques
