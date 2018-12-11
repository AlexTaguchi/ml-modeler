#!/usr/bin/env python3

# Modules
from mlm.data import one_hot
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB, MultinomialNB


class Logistic:
    """
    Logistic regression classifier
    """

    def __init__(self):
        pass

    def train(self, train):

        # Instantiate the classifiers
        mlr = LogisticRegression(solver='sag', max_iter=10000, multi_class='multinomial')
        ovr = LogisticRegression(solver='sag', max_iter=10000, multi_class='ovr')

        # Train classifier
        mlr.fit(train.iloc[:, :-1], train.iloc[:, -1])
        ovr.fit(train.iloc[:, :-1], train.iloc[:, -1])

        return mlr, ovr

    def predict(self, feature, mlr, ovr):

        # Predict labels
        return mlr.predict(feature), ovr.predict(feature)


    def __call__(self, train, test):

        # Convert train and test to one-hot
        train = one_hot(train)
        test = one_hot(test)

        # Train Gaussian and Multinomial classifiers
        mlr, ovr = self.train(train)

        # Predict train and test labels
        train_pred_mlr, train_pred_ovr = self.predict(train.iloc[:, :-1], mlr, ovr)
        test_pred_mlr, test_pred_ovr = self.predict(test.iloc[:, :-1], mlr, ovr)

        # Print results
        print('==========LOGISTIC REGRESSION==========')
        train_hit_mlr = (train.iloc[:, -1] == train_pred_mlr).sum()
        train_hit_ovr = (train.iloc[:, -1] == train_pred_ovr).sum()
        test_hit_mlr = (test.iloc[:, -1] == test_pred_mlr).sum()
        test_hit_ovr = (test.iloc[:, -1] == test_pred_ovr).sum()
        print('Train accuracy:  %.2f%% (Multinomial), %.2f%% (One-vs-Rest)'
              % (100 * train_hit_mlr / len(train), 100 * train_hit_ovr / len(train)))
        print('Test accuracy:   %.2f%% (Multinomial), %.2f%% (One-vs-Rest)'
              % (100 * test_hit_mlr / len(test), 100 * test_hit_ovr / len(test)))
        print('')


class Bayes:
    """
    Naive Bayes classifier
    """

    def __init__(self):
        self.categorical = 'object'
        self.numerical = 'number'

    def cat_num_split(self, feature):

        # Split features into categorical and numberical types
        feature_cat = feature.select_dtypes(include=self.categorical)
        feature_num = feature.select_dtypes(include=self.numerical)

        return feature_cat, feature_num

    def train(self, train_cat, train_num, train_labels):

        # Instantiate the classifiers
        mnb = MultinomialNB()
        gnb = GaussianNB()

        # Train classifier
        if train_cat.shape[1]:
            mnb.fit(train_cat, train_labels)
        if train_num.shape[1]:
            gnb.fit(train_num, train_labels)

        return mnb, gnb

    def predict(self, feature_cat, feature_num, mnb, gnb):

        # Predict labels
        cat_pred = mnb.predict_proba(feature_cat) if feature_cat.shape[1] else 0
        cat_pred *= feature_cat.shape[1]
        num_pred = gnb.predict_proba(feature_num) if feature_num.shape[1] else 0
        num_pred *= feature_num.shape[1]

        return (cat_pred + num_pred).argmax(axis=1)

    def __call__(self, train, test):

        # Split train and test into categorical and numerical features
        train_cat, train_num = self.cat_num_split(train.iloc[:, :-1])
        test_cat, test_num = self.cat_num_split(test.iloc[:, :-1])

        # Assign labels
        train_labels = train.iloc[:, -1]
        test_labels = test.iloc[:, -1]

        # Train Gaussian and Multinomial classifiers
        mnb, gnb = self.train(train_cat, train_num, train_labels)

        # Predict train and test labels
        train_pred = self.predict(train_cat, train_num, mnb, gnb)
        test_pred = self.predict(test_cat, test_num, mnb, gnb)

        # Print results
        print('==============NAIVE BAYES==============')
        train_hit = (train_labels == train_pred).sum()
        test_hit = (test_labels == test_pred).sum()
        print('Train accuracy:  %.2f%%'
              % (100 * train_hit / len(train)))
        print('Test accuracy:   %.2f%%'
              % (100 * test_hit / len(test)))
        print('')