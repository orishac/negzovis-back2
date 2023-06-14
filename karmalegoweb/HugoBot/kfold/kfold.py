from sklearn.model_selection import StratifiedKFold


class KFold:
    """ This class allows to divide the dataset into train and test folds,
        so that train and test sets have class distribution """
    def __init__(self, nb_folds, entity_class_relations):
        """
        :param nb_folds: int, number of folds
        :param entity_class_relations: Dataframe
        """
        self.nb_folds = nb_folds
        self.entity_class_relations = entity_class_relations

    def divide_dataset(self, dataset):
        """
        :param dataset: Dataframe, a dataset
        :return:
            List, a list where each element contains a
            tuple with a train set and a test set as dataframes
        """
        k_fold = StratifiedKFold(n_splits=self.nb_folds, random_state=1, shuffle=True)
        folds = list(k_fold.split(self.entity_class_relations, self.entity_class_relations.ClassID))

        res = []
        for fold in folds:
            train_entity_ids = self.entity_class_relations.iloc[fold[0]].EntityID
            test_entity_ids = self.entity_class_relations.iloc[fold[1]].EntityID

            train = dataset[dataset['EntityID'].isin(train_entity_ids)]
            test = dataset[dataset['EntityID'].isin(test_entity_ids)]

            res.append([train, test])

        return res
