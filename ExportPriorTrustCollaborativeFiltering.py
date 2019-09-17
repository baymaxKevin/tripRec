# -*- coding: utf-8 -*- 
# @Time : 2019/9/13 14:15 
# @Author : Mr.Zhe
# @File : ExportPriorTrustCollaborativeFiltering.py

import sys
import random
import math
from operator import itemgetter

"""
基于专家优先信任的协同过滤推荐算法
"""
class ExportPriorTrustCollaborativeFiltering(object):

    def __init__(self):
        self.trainset = {}  # 训练集
        self.testset = {}  # 测试集

        self.nSimAttraction = 20  # 最大相似景点数
        self.nRecAttraction = 10  # 推荐景点数

        self.attractionSimMatrix = {}  # 景点相似矩阵
        self.attractionPopular = {}  # 景点流行度
        self.attractionCount = 0  # 景点数量
        self.maxPhotoCount = 0  # 最大的照片数量

        self.userAvgRating = {}  # 用户的平均评分
        self.attractionAvgRating = {}  # 景点平均评分
        self.userRating = {}  # 用户评分
        self.exportDict = {}  # 用户id及信任度
        self.exports = {}  # 专家用户
        self.userPre = {}  # 基于专家信任的用户-景点偏好

        print('Similar attraction number = %d' % self.nSimAttraction, file=sys.stderr)
        print('Recommended attraction number = %d' % self.nRecAttraction, file=sys.stderr)

    @staticmethod
    def loadfile(filename):
        ''' 读取文件 '''
        fp = open(filename, 'r')

        for i, line in enumerate(fp):
            yield line.strip('\r\n')
        fp.close()
        print ('load %s succ' % filename, file=sys.stderr)

    def generateDataset(self, filename, pivot=0.7):
        ''' 加载数据集，分割为测试集和训练集'''
        trainset_len = 0
        testset_len = 0
        i = 0
        # 用户-最大评分
        userMaxRating = {}
        for line in self.loadfile(filename):
            userId, attractionId, photoCount = line.split(',')[0:3]
            if (i == 0):  # 去除csv头
                i = 1
                continue
            userMaxRating[userId] = max(userMaxRating.get(userId, 0),int(photoCount))
            self.maxPhotoCount = max(self.maxPhotoCount, int(photoCount))
            # 用户-景点照片数量矩阵
            self.userRating.setdefault(userId, {})
            self.userRating[userId][attractionId] = int(photoCount)

        for userId,attractions in self.userRating.items():
            for attractionId in attractions:
                self.userRating[userId][attractionId] = self.userRating[userId][attractionId]/userMaxRating[userId]
                # 按pivot比例分割数据集
                if random.random() < pivot:
                    self.trainset.setdefault(userId, {})
                    self.trainset[userId][attractionId] = int(photoCount)/userMaxRating[userId]
                    trainset_len += 1
                else:
                    self.testset.setdefault(userId, {})
                    self.testset[userId][attractionId] = int(photoCount)/userMaxRating[userId]
                    testset_len += 1

        print('split training set and test set succ', file=sys.stderr)
        print('train set = %s' % trainset_len, file=sys.stderr)
        print('test set = %s' % testset_len, file=sys.stderr)
        print(self.trainset)

    """计算专家信任度
       识别专家用户
       rate为专家在用户中占比
    """
    def calExportPriorTrustIdWithScore(self, rate):
        ''' 计算用户专家信任度 '''
        users = set()
        # 用户-评分之和dict
        userSumRatings = {}
        # 用户-评分次数dict
        userCount = {}
        # 景点-评分之和dict
        attractionSumRatings = {}
        # 景点-评分次数dict
        attractionCount = {}
        # 景点-评分最大值dict
        attractionMaxRatings = {}
        for userId, attractions in self.userRating.items():
            users.add(userId)
            for attraction in attractions:
                # 计算用户平均评分
                userSumRatings[userId] = userSumRatings.get(userId,0) + self.userRating[userId][attraction]
                userCount[userId] = userCount.get(userId,0) + 1
                self.userAvgRating[userId] = userSumRatings[userId]/userCount[userId]
                # 计算景点均值和最大评分
                attractionSumRatings[attraction] = attractionSumRatings.get(attraction, 0) + self.userRating[userId][attraction]
                attractionCount[attraction] = attractionCount.get(attraction, 0) + 1
                attractionMaxRatings[attraction] = max(attractionMaxRatings.get(attraction, 0), self.userRating[userId][attraction])

        # 用户对景点专家信任度score = sum(cr) = sum(1-|r-Ravg|/Rmax)
        for userId, attractions in self.userRating.items():
            for attraction in attractions:
                uRating = self.userRating[userId][attraction]
                if attractionCount[attraction] > 1:
                    avgRating = (attractionSumRatings[attraction] - uRating) / (attractionCount[attraction] - 1)
                else:
                    avgRating = 0
                self.attractionAvgRating[attraction] = avgRating
                maxRating = attractionMaxRatings[attraction]
                exportTrust = 1 - abs(uRating - avgRating) / maxRating
                self.exportDict[userId] = (self.exportDict.get(userId,0) + exportTrust)/self.maxPhotoCount

        print(self.exportDict)
        self.exports = sorted(self.exportDict,key=itemgetter(1), reverse=True)[:(int)(len(users) * rate)]
    
    def calUser2AttractionPreBasedExportTrust(self):
        ''' 利用专家信任高的用户评分对其他用户进行推荐 '''
        # 用户-景点评分
        for userId, attractions in self.userRating.items():
            for attraction in attractions:
                pre = self.userRating[userId][attraction]
                numerator = 0
                denominator = 0
                for export in self.exports:
                    if (attraction in self.userRating[export]):
                        # 专家对景点的评分
                        exportRating = self.userRating[export][attraction]
                        # 专家信任度
                        exportScore = self.exportDict.get(export, 0)
                        # 专家的平均评分
                        exportAvgRating = self.userAvgRating[export]
                        # if random.random() < 0.01:
                        #     print('exportScore=%.4f\texportRating=%.4f\texportAvgRating=%.4f\texport=%s' % (exportScore, exportRating, exportAvgRating, export), file=sys.stderr)
                        numerator = numerator + exportScore * (exportRating - exportAvgRating)
                        denominator = denominator + exportScore
                if denominator != 0:
                    pre = pre + numerator / denominator
                    # print('pre:',pre,'preAdd:',numerator / denominator)
            self.userPre.setdefault(userId,{})
            self.userPre[userId][attraction] = pre
        print(self.userPre)

    def calculateAttractionSim(self):
        ''' 计算景点的相似度矩阵 '''
        for userId, attractions in self.trainset.items():
            for attraction in attractions:
                # 计算景点流行度
                if attraction not in self.attractionPopular:
                    self.attractionPopular[attraction] = 0
                self.attractionPopular[attraction] += 1
        # print(self.attractionPopular)
        print('获取景点数目和流行度完成', file=sys.stderr)

        # 获取景点总数
        self.attractionCount = len(self.attractionPopular)

        # 计算景点相似度
        itemsim_mat = self.attractionSimMatrix
        for userId, attractions in self.trainset.items():
            for a1 in attractions:
                for a2 in attractions:
                    if a1 == a2:
                        continue
                    itemsim_mat.setdefault(a1, {})
                    itemsim_mat[a1].setdefault(a2, 0)
                    itemsim_mat[a1][a2] += 1

        # 计算景点相似度矩阵
        simfactor_count = 0
        PRINT_STEP = 2000000

        for a1, relatedAttraction in itemsim_mat.items():
            for a2, count in relatedAttraction.items():
                itemsim_mat[a1][a2] = count / math.sqrt(
                    self.attractionPopular[a1] * self.attractionPopular[a2])
                simfactor_count += 1
                if simfactor_count % PRINT_STEP == 0:
                    print('calculating attraction similarity factor(%d)' \
                          % simfactor_count, file=sys.stderr)

        print('计算景点相似度矩阵完成', file=sys.stderr)
        # print('Total similarity factor number = %d' % simfactor_count, file=sys.stderr)

    def recommend(self, user, flag):
        ''' Find K similar attractions and recommend N attractions. '''
        K = self.nSimAttraction
        N = self.nRecAttraction
        rank = {}
        if flag:
             watched_attractions = self.trainset[user]
        else:
            watched_attractions = self.testset[user]
        try:
            for attraction, rating in watched_attractions.items():
                pre = self.userPre[user][attraction]
                for related_attraction, similarity_factor in sorted(self.attractionSimMatrix[attraction].items(),
                                                                    key=itemgetter(1), reverse=True)[:K]:
                    if related_attraction in watched_attractions:
                        continue
                    rank.setdefault(related_attraction, 0)
                    rank[related_attraction] += similarity_factor * pre
        except KeyError:
            # print ('catch an exception')
            c = 1

        # return the N best attractions
        return sorted(rank.items(), key=itemgetter(1), reverse=True)[:N]

    def evaluate(self):
        ''' 显示评估结果: precision, recall, coverage and popularity '''

        print('开始评估...', file=sys.stderr)

        N = self.nRecAttraction

        #  varables for precision and recall
        hit = 0
        rec_count = 0
        test_count = 0

        # varables for coverage
        all_rec_attractions = set()

        # varables for popularity
        popular_sum = 0

        for i, user in enumerate(self.trainset):
            if i % 500 == 0:
                print('recommended for %d users' % i, file=sys.stderr)
            test_attractions = self.testset.get(user, {})
            rec_attractions = self.recommend(user, flag=True)
            for attraction, _ in rec_attractions:
                if attraction in test_attractions:
                    hit += 1
                all_rec_attractions.add(attraction)
                popular_sum += math.log(1 + self.attractionPopular[attraction])
            rec_count += N
            test_count += len(test_attractions)

        precision = hit / (1.0 * rec_count)
        recall = hit / (1.0 * test_count)
        coverage = len(all_rec_attractions) / (1.0 * self.attractionCount)
        popularity = popular_sum / (1.0 * rec_count)

        print('准确率=%.4f\n召回率=%.4f\n覆盖率=%.4f\n流行度=%.4f' %
              (precision, recall, coverage, popularity), file=sys.stderr)


if __name__ == '__main__':
    baseDir = 'yfcc100m_dataset/'
    userAttractionFile = baseDir + 'user-attraction.csv'

    eptcf = ExportPriorTrustCollaborativeFiltering()
    eptcf.generateDataset(userAttractionFile)
    eptcf.calExportPriorTrustIdWithScore(0.15)
    eptcf.calculateAttractionSim()
    eptcf.calUser2AttractionPreBasedExportTrust()
    eptcf.evaluate()