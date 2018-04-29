"""
* Copyright (c) 2015-2017 The Hyve B.V.
* This code is licensed under the GNU General Public License,
* version 3.
"""
import pandas as pd

concept_id = 'concept.conceptCode'
trial_visit_id = 'trial visit.id'
patient_id = 'patient.id'
start_time_id = 'start time'
study_id = 'study.name'

dimensions = {
    'concept': concept_id,
    'study': study_id,
    'trial_visit': trial_visit_id,
    'start_time': start_time_id,
    'subject': patient_id
}

value_columns = ['numericValue', 'stringValue']


class HypercubeException(Exception):
    pass


class Hypercube:

    def __init__(self):
        self.dims = []
        self._cols = list(dimensions.values()) + value_columns
        self.data = pd.DataFrame()
        self.total_subjects = None
        self._subject_bool_mask = None
        self.__subjects_mask = None
        self.study_concept_pairs = set()

    @property
    def subject_mask(self):
        return self.__subjects_mask

    @subject_mask.setter
    def subject_mask(self, values):
        self.__subjects_mask = values
        if values is not None:
            self._subject_bool_mask = self.data[patient_id].isin(values)

    def add_variable(self, df):
        # check duplicate study-concept pairs
        ns = {(v[0], v[1]) for v
              in df.loc[:, [concept_id, study_id]].drop_duplicates().values}
        if self.study_concept_pairs.intersection(ns):
            return
        self.study_concept_pairs.update(ns)

        sub_set = df.loc[:, self._cols]
        self.data = self.data.append(sub_set, ignore_index=True)
        self.total_subjects = len(self.data[patient_id].unique())

    def query(self, no_filter=False, **kwargs):
        expressions = []
        for kw, column in dimensions.items():
            if kw not in kwargs:
                continue
            parameter = kwargs.get(kw)
            if isinstance(parameter, (pd.Series, list)):
                expr = self.data[column].isin(parameter)
            else:
                expr = self.data[column] == parameter
            expressions.append(expr)

        bools = True
        for expr in expressions:
            bools &= expr

        if not no_filter and self.subject_mask is not None:
            bools &= self._subject_bool_mask

        return self.data.loc[bools, [patient_id, *value_columns]]

