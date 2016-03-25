#coding = 'utf-8'
"""data explore for raw datasheet"""
__author__ = "changandao&jiangweiwu"
__date__   = "2016.3.8"

import numpy as np
import pandas as pd
#from sklearn import *
#from sklearn.preprocessing import Imputer
import matplotlib.pyplot as plt
from pandas import datetime


class IVProcess:
    corresWOE = pd.DataFrame()
    replacedclm = pd.DataFrame()
    dropdf = pd.DataFrame()
    tmpWOE = pd.DataFrame()
    tmptotal = pd.DataFrame()
    Iv_object = pd.DataFrame()
    WOE = pd.DataFrame()
    #dateser = pd.Series()
    ori_train_file = ''
    ori_type_file = ''
    ori_test_file = ''
    k = 0
    case = 0
    timeoption = 0
    NaNRate = 0
    IV = 0
    reflag = 0
    def __init__(self, ori_train_file_name, ori_test_file_name, ori_type_file_name, k, case, timeoption,NaNRate):
        self.ori_train_file = pd.read_csv(ori_train_file_name,encoding="gb18030")
        self.ori_type_file = pd.read_csv(ori_type_file_name,encoding="gb18030")
        self.ori_test_file = pd.read_csv(ori_test_file_name,encoding="gb18030")
        self.k = k
        self.case = case
        self.timeoption = timeoption
        self.NaNRate = NaNRate
        self.__replacenull()
        print 'all -1 has been replaced'
        self.__resetType()
        print 'resetType finished'
   

    def __replacenull(self):
        self.ori_train_file = self.ori_train_file.replace(-1, np.nan)
        self.ori_test_file = self.ori_test_file.replace(-1, np.nan)


    def __resetType(self):       
        typetmp = self.ori_type_file.dropna(axis=1)
        se = typetmp.set_index('Idx')
        ser = pd.Series(se['Index'],index = typetmp['Idx'])
        for i in ser.index:
            if ser[i]=='Categorical':
                ser[i] = 'object'
            elif ser[i]=='Numerical':
                ser[i] = 'float64'
            else:
                pass
            try:
                 self.ori_train_file[i] =  self.ori_train_file[i].astype(ser[i])
            except:
                 pass
            try:
                 self.ori_test_file[i] =  self.ori_test_file[i].astype(ser[i])
            except:
                pass


    def __WOEcal(self, goodpct, badpct):
        pct_ratio = goodpct/badpct
        pct_ratio =  pct_ratio.fillna(0.)
        npratio = np.array(pct_ratio)
        self.WOE = np.log(npratio)
        self.WOE = pd.Series(self.WOE)


    def __IVcal(self, good,bad):
        goodall = good.sum()
        badall = bad.sum()
        pct_good = good/goodall
        pct_bad = bad/badall
        self.__WOEcal(pct_good,pct_bad)
        pct_diff = pct_good-pct_bad
        pct_diff =  pct_diff.fillna(0.)
        npdiff = np.array(pct_diff)
        iv = npdiff*self.WOE
        ivser = pd.Series(iv)
        self.IV = ivser.sum()


    def __Objectprocess(self, goodser, badser, totalser):##case =1 replace unicode ,case = 2 replace all
        goodOValue = goodser.value_counts()
        badOValue = badser.value_counts()
        totalOvalue = totalser.value_counts()
        badtmp = totalOvalue.copy()
        goodtmp = totalOvalue.copy()
        badtmp[(totalOvalue - badOValue).notnull()] = badOValue+1
        badtmp[(totalOvalue - badOValue).isnull()] = 1
        goodtmp[(totalOvalue - goodOValue).notnull()] = goodOValue+1
        goodtmp[(totalOvalue - goodOValue).isnull()] = 1
        goodtmp = goodtmp.sort_index()
        badtmp = badtmp.sort_index()
        good_pct = goodtmp/goodtmp.sum()
        bad_pct = badtmp/badtmp.sum()
        totalOvalue = totalOvalue.sort_index()
        self.corresWOE =totalOvalue.copy()
        self.tmpWOE = self.__WOEcal(good_pct,bad_pct)
        self.corresWOE[:] = self.tmpWOE###coresponding woe
        self.tmptotal = totalser.copy()###original series
        self.__repalcewoe()
        self.IV = self.__IVcal(goodtmp,badtmp)
        return self.tmptotal


    def __repalcewoe(self):##replace unicode with woe
        def _case1():
            totalidx = self.corresWOE.index
            for i in self.tmptotal.index:
                if type(self.tmptotal[i]) == unicode:
                    idx = totalidx.get_loc(self.tmptotal[i])
                    self.tmptotal[i] = self.corresWOE[idx]
                    self.reflag = 1
        def _case2():
            totalidx = self.corresWOE.index
            for i in self.tmptotal.index:
                #if type(tmptotal[i]) == unicode:
                idx = totalidx.get_loc(self.tmptotal[i])
                self.tmptotal[i] = self.corresWOE[idx]
        if self.case == 1:
            _case1()
        elif self.case == 2:
            _case2()
        #return oriseries,shouldreplace###return the replaced series and flag of relace all or only unicode

    def __NUMprocess(self, goodser, badser, totalser,bin):
        totalcuts = pd.cut(totalser, bin, right = True, include_lowest = True)
        goodcuts = pd.cut(goodser, bin, right = True, include_lowest = True)
        badcuts = pd.cut(badser, bin, right = True, include_lowest = True)

        ####### do statistics
        totalsum = totalcuts.value_counts()
        goodsum = goodcuts.value_counts()
        badsum = badcuts.value_counts()

        totalsum = totalsum.sort_index() # sort the index
        goodsum = goodsum.sort_index()# sort the index
        badsum = badsum.sort_index()# sort the index
        badsum[(totalsum==0) != (badsum == 0)] = 1
        goodsum[(totalsum==0) != (goodsum == 0)] = 1
        self.__IVcal(goodsum, badsum)


    def __dateprocess(self, dateseries):
        dateser = pd.to_datetime(dateseries)
        dateser = dateser-dateser.min()
        return dateser

    def __replaceunicode(self,repalceser):
        flag = 0
        for i in repalceser.index:
            if type(repalceser.ix[i]) == unicode:
                flag=1
            #else:flag = 0
        if flag == 1:
            repalceser = repalceser.fillna(u'no') #option with D E
        else:pass
        return repalceser


    def handel_test(self):
        testdrop = pd.DataFrame()
        testframe = self.ori_train_file.set_index('Idx')
        for clm in testframe.columns:
            if clm == 'ListingInfo':
                if self.timeoption == 0:
                    testframe[clm] = self.__dateprocess(testframe[clm])
                else:continue
            elif clm in self.dropdf.columns:
                testdrop[clm] = testframe[clm]
                del testframe[clm]
            elif clm in self.replacedclm.columns:
                testframe[clm] = self.__replaceunicode(testframe[clm])
                testframe[clm],shouldreplace = self.__repalcewoe(testframe[clm])
            else:pass
        return testframe,testdrop



    def IVFunc(self):#case defined in Objectprocess ,1 only replace unicoid ,2 replace all
        lst = []
        count = 0
        final_IV = 0
        newFrame = self.ori_train_file.set_index('Idx')
        testFrame = self.ori_test_file.set_index('Idx')
        goodN = newFrame.groupby('target').get_group(1)
        badN = newFrame.groupby('target').get_group(0)
        for clm in newFrame.columns:
            if clm == 'target':
                continue
            elif clm == 'ListingInfo':
                if self.timeoption == 0:
                    newFrame[clm] = self.__dateprocess(newFrame[clm])
                    testFrame[clm] = self.__dateprocess(testFrame[clm])
                else:continue
            else:
                rate = float(len(newFrame[clm].dropna()))/30000
                if rate < self.NaNRate:
                    print clm,' drop ',str(rate)
                    self.dropdf[clm] = newFrame[clm]
                    del newFrame[clm]
                    continue
                else:
                    if newFrame[clm].dtypes =='object':
                        newFrame[clm] = self.__replaceunicode(newFrame[clm])
                        newFrame[clm] = self.__Objectprocess(goodN[clm],badN[clm],newFrame[clm])
                        #print newFrame[clm].dtypes
                        #print newFrame[clm]
                        if self.reflag == 1:
                            newFrame[clm] = newFrame[clm].astype('float64')
                            self.replacedclm[clm] = newFrame[clm]
                        else:pass
                        if self.IV >1:
                            print 'final_IV larger than 1',clm
                            continue

                    ######## numerical#######
                    else:
                        continue
##        print newFrame.dtypes
##        imp = preprocessing.Imputer(missing_values='NaN', strategy='mean', axis=0)
##        imp.fit(newFrame)
##        test = imp.transform(newFrame)
##        print newFrame.shape,test.shape
##        newFrame[clm] = test
##                        
                        ####### Discretization
##                        Maxmum = float(newFrame[clm].max())
##                        Minmum = float(newFrame[clm].min())
##                        dist = float((Maxmum - Minmum)/self.k)
##                        if (Maxmum - Minmum) < self.k:
##                            final_IV,newFrame[clm],reflag = self.__Objectprocess(goodN[clm],badN[clm],newFrame[clm])
##                        else:
##                            if dist == 0:
##                                self.dropdf[clm] = newFrame[clm]
##                                print clm,' drop  with 0 dist '
##                                del newFrame[clm]
##                                continue
##                            bins =[]
##                            for i in range(0,self.k+1):
##                                start = Minmum + i*dist
##                                bins.append(start)
##                            final_IV = self.__NUMprocess(goodN[clm],badN[clm],newFrame[clm],bins)
##                            if final_IV >1:
##                                continue
##                            elif final_IV >0.1:
##                                pass

##                    lst.append(final_IV)
        return lst,newFrame,self.dropdf

if __name__=='__main__':
    FilePath = '../data/'
    Dataset = 'Training Set/'
    Testset = 'Test Set/'
    MasterTrainFile = FilePath + Dataset + 'PPD_Training_Master_GBK_3_1_Training_Set.csv'
    MasterTestile = FilePath + Testset + 'PPD_Master_GBK_2_Test_Set.csv'
    MasterFileType = FilePath + 'TypeState.csv'

    ivpro = IVProcess(MasterTrainFile,MasterTestile,MasterFileType,20,1,0,0.7)
    IV, DF, droped = ivpro.IVFunc()
    
    #imp = Imputer(missing_values='NaN', strategy='mean', axis=0)
    # 
    #TESTDATA = Dateprocess(Master, TEST, TypeStatement,20,1,0,0.75)
    DF_test,droped_Test = Dateprocess.handel_test(TESTDATA)
    #print DF
    DF.to_csv('../Output/S1/statistics/seleted_Master_Train.csv', encoding="gb18030")
    droped.to_csv('../Output/S1/statistics/droped_Master_Train.csv', encoding="gb18030")
    DF_test.to_csv('../Output/S1/statistics/seleted_Master_Train.csv', encoding="gb18030")
    droped_Test.to_csv('../Output/S1/statistics/droped_Master_Test.csv', encoding="gb18030")
    #droped_test.to_csv('../Output/S1/statistics/droped_Master.csv', encoding="gb18030")
##                                continue
##                            bins =[]
##                            for i in range(0,self.k+1):
##                                start = Minmum + i*dist
##                                bins.append(start)
##                            final_IV = self.__NUMprocess(goodN[clm],badN[clm],newFrame[clm],bins)
##                            if final_IV >1:
##                                continue
##                            elif final_IV >0.1:
##                                pass

##                    lst.append(final_IV)
        return lst,newFrame,self.dropdf

if __name__=='__main__':
    FilePath = '../data/'
    Dataset = 'Training Set/'
    Testset = 'Test Set/'
    MasterTrainFile = FilePath + Dataset + 'PPD_Training_Master_GBK_3_1_Training_Set.csv'
    MasterTestile = FilePath + Testset + 'PPD_Master_GBK_2_Test_Set.csv'
    MasterFileType = FilePath + 'TypeState.csv'

    ivpro = IVProcess(MasterTrainFile,MasterTestile,MasterFileType,20,1,0,0.75)
    IV, DF, droped = ivpro.IVFunc()
    
    #imp = Imputer(missing_values='NaN', strategy='mean', axis=0)
    # 
    #TESTDATA = Dateprocess(Master, TEST, TypeStatement,20,1,0,0.75)
    DF_test,droped_Test = Dateprocess.handel_test(TESTDATA)
    #print DF
    DF.to_csv('../Output/S1/statistics/seleted_Master_Train.csv', encoding="gb18030")
    droped.to_csv('../Output/S1/statistics/droped_Master_Train.csv', encoding="gb18030")
    DF_test.to_csv('../Output/S1/statistics/seleted_Master_Train.csv', encoding="gb18030")
    droped_Test.to_csv('../Output/S1/statistics/droped_Master_Test.csv', encoding="gb18030")
    #droped_test.to_csv('../Output/S1/statistics/droped_Master.csv', encoding="gb18030")
