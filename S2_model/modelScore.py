#coding = 'utf-8'
"""training model from data set and model decision"""
__author__ = "jiangweiwu"
__date__   = "2016.3.16"

import random
import numpy as np
import pandas as pd
import scipy as sci
from datetime import datetime
from sklearn import *
import matplotlib.pyplot as plt
from time import time

#from sklearn.ensemble import RandomForestRegressor
#from sklearn.pipeline import Pipeline
class modelScore:
    trainFileName = ''
    testFileName = ''
    scoreFileName = ''
    codingType = 'utf-8'
    testXData = []
    trainYLabel = []
    trainXData = []
    def __init__(self,trainFileName,testFileName,scoreFileName,codingType):
        self.trainFileName = trainFileName
        self.testFileName = testFileName
        self.scoreFileName = scoreFileName
        self.codingType = codingType

		
    def readData(self):
	# FilePath = '../data/'
    # TrainDataset = 'Training Set/'
    # TestDataset = 'Test Set/'
    # train_set = pd.read_csv(FilePath + TrainDataset  + 'PPD_Training_Master_GBK_3_fi1_Training_Set.csv',encoding='gb18030')
    # test_set = pd.read_csv(FilePath + TestDataset  + 'PPD_Master_GBK_2_Test_Set.csv',encoding='gb18030')
    
    # train_set.dropna(axis=1,how='all')  # if all values are NA, drop that label
    # train_set_col = train_set.columns
    # index = 0
    # for temp in train_set.dtypes.values:
        # if temp == 'object':
            # train_set = train_set.drop(train_set_col[index],axis=1)
            # test_set = test_set.drop(train_set_col[index],axis=1)
        # index += 1
    # 
    # 
        trainSet = pd.read_csv(self.trainFileName,encoding=self.codingType)
        self.testXData = pd.read_csv(self.testFileName,encoding=self.codingType)
        self.trainYLabel = trainSet['target']
        self.trainXData = trainSet.drop('target',axis=1)
        
        self.trainXData = self.trainXData.drop('ListingInfo',axis=1)
        self.testXData = self.testXData.drop('ListingInfo',axis=1)
        imp = preprocessing.Imputer(missing_values='NaN', strategy='mean', axis=0)
        imp.fit(self.trainXData)
        self.trainXData = imp.transform(self.trainXData)
        #self.testXData = imp.transform(self.testXData)
     
    def modelTraining(self):
        skf = cross_validation.StratifiedKFold(self.trainYLabel.values,50)
        for train_index, test_index in skf:
            trainXData_CV_Train = self.trainXData[train_index]
            trainXData_CV_Test = self.trainXData[test_index]
            trainYLabel_CV_Train = self.trainYLabel[train_index]
            trainYLabel_CV_Test = self.trainYLabel[test_index]

            cost_time = time()
            grd = ensemble.GradientBoostingClassifier(n_estimators=200,max_depth=3,learning_rate=0.05) #test case learning_rate=0.01
            grd.fit(trainXData_CV_Train, trainYLabel_CV_Train)
            cost_time = time() - cost_time
            temp_trainXData_CV_Train = grd.apply(trainXData_CV_Train)[:, :, 0]
            temp_trainXData_CV_Test = grd.apply(trainXData_CV_Test)[:, :, 0]
            #print cost_time
	
            cost_time = time()
            grd_enc = preprocessing.OneHotEncoder()
            grd_enc.fit(temp_trainXData_CV_Train)
            new_trainXData_CV_Train = grd_enc.transform(temp_trainXData_CV_Train)
            new_trainXData_CV_Test = grd_enc.transform(temp_trainXData_CV_Test)
            cost_time = time() - cost_time
            #print cost_time

            res_l1_LR_list = [0,0,0]
            for i,C in enumerate((0.006,0.005,0.004)):
                lm_LR = linear_model.LogisticRegression(C=C,penalty='l1',tol=0.005,solver='liblinear',max_iter=200)
                lm_LR.fit(new_trainXData_CV_Train, trainYLabel_CV_Train)
                y_pred_lm_LR = lm_LR.predict_proba(new_trainXData_CV_Test)[:, 1]
                res_y_pred_lm_LR = metrics.roc_auc_score(trainYLabel_CV_Test, y_pred_lm_LR)
                print i,res_y_pred_lm_LR
                res_l1_LR_list[i] = res_l1_LR_list[i] + y_pred_lm_LR
            #print np.average(res_l1_LR_list)
        

        
        #grd = ensemble.GradientBoostingClassifier(n_estimators=300,max_depth=4) 
        #grd.fit(New_X_Data, Y_Label)
        #temp_X_Train = grd.apply(New_X_Data)[:, :, 0]
        #temp_X_Test = grd.apply(New_Test_Data)[:, :, 0]
        #grd_enc = preprocessing.OneHotEncoder()
        #grd_enc.fit(temp_X_Train)
        #New_temp_X_Train = grd_enc.transform(temp_X_Train)
        #New_temp_X_Test = grd_enc.transform(temp_X_Test)
        #grd_lm = linear_model.LogisticRegression(C=0.06,penalty='l1',tol=0.005,solver='liblinear',max_iter=400)
        #grd_lm.fit(New_temp_X_Train, Y_Label)
        #New_Test_Data_res = grd_lm.predict_proba(New_temp_X_Test)
        #Total_res = np.column_stack((New_Test_Data[:,0].astype(int),New_Test_Data_res[:,1]))
        #np.savetxt('2.csv',Total_res,fmt='%.6f')
	

	
	
if __name__=="__main__":
    test_modelScore = modelScore('../Output/S1/statistics/seleted_Master.csv',"../data/Test Set/PPD_Master_GBK_2_Test_Set.csv",'../submit/test.csv','gb18030')
    test_modelScore.readData()
    test_modelScore.modelTraining()
	
