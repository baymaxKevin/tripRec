# tripRec
## 环境
Anaconda3-2019.03-Windows-x86_64

python=python37

依赖包: numpy+pandas+scikit-learn+matplotlib+Basemap+geopy

依赖包安装方法：
进入cmd，conda install numpy pandas scikit-learn matplotlib Basemap

geopy安装需要特别注意：
conda默认路径不支持直接下载！！！

geopy安装技巧：

```
anaconda search -t conda geopy
# 这里(anaconda search -t conda 库名)可以选择自己安装的源

# return the available packages and the location
# 我们在列出的表里面见到Primer文件夹下有可用的包，于是
anaconda show Primer/geopy

# prompt给出提示，可以指定源安装
# 把它提示的语句抄一遍：
conda install --channel https://canda/anaconda.org/Primer geopy

#提示yes no后，选择 yes

#安装完成后，使用
conda list
#查看现在安装的包
#可以看到 geopy
```
# 数据集
YFCC 100M数据库是2014年来基于雅虎Flickr的影像数据库。该库由1亿条产生于2004年至2014年间的多条媒体数据组成，其中包含了9920万的照片数据以及80万条视频数据。

YFCC 100M数据集并不包含照片或视频数据，而是一个文本数据文档，文档中每一行都是一条照片或视频的元数据。每一行包含23个项目，他们分别代表：

```
[0]     Photo/video identifier    照片/视频标识符
[1]     User NSID    用户NSID
[2]     User nickname    用户昵称
[3]     Date taken    拍摄日期
[4]     Date uploaded    上传日期
[5]     Capture device    使用设备
[6]     Title    标题
[7]     Description    描述
[8]     User tags (comma-separated)    用户标签（逗号分隔）
[9]     Machine tags (comma-separated)    机器标签（逗号分隔）
[10]    Longitude    经度
[11]    Latitude    纬度
[12]    Accuracy    准确性
[13]    Photo/video page URL    照片/视频页面URL
[14]    Photo/video download URL    照片/视频下载网址
[15]    License name    许可证名称
[16]    License URL    许可网址
[17]    Photo/video server identifier    照片/视频服务器标识符
[18]    Photo/video farm identifier    照片/视频农场标识符
[19]    Photo/video secret    照片/视频秘密
[20]    Photo/video secret original    照片/视频秘密原件
[21]    Extension of the original photo    扩展原始照片
[22]    Photos/video marker (0 = photo, 1 = video)    照片/视频标记（0 =照片，1 =视频）
```
## ETL
清洗过滤数据，保留用户id, 景点id, 拍照数量, 用户标签, 拍照时间字段
User NSID,Photo/video identifier,photoNum,User tags,Date taken

## 样本
训练集: 测试集=0.7: 0.3
召回用的评分为拍照数量

# 内容
## 创新点
[基于专家信任的协同过滤](http://xueshu.baidu.com/usercenter/paper/show?paperid=58e5eacfc7898fcda421a0e3cd3a2ce6&site=xueshu_se)

[群组]

[BIPM]

## 基于专家信任的协同过滤
python ExportPriorTrustCollaborativeFiltering.py
