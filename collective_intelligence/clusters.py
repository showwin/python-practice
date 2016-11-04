# -*- coding: utf-8 -*-
from math import sqrt
from PIL import Image, ImageDraw
import time
import sys
import random


def readfile(filename):
    lines = [line for line in file(filename)]

    # 最初の行はタイ凸
    colnames = lines[0].strip().split('\t')[1:]
    rownames = []
    data = []
    for line in lines[1:]:
        p = line.strip().split('\t')
        # それぞれの行の最初の列は行の名前
        rownames.append(p[0])
        # 残りの部分がその行のデータ
        data.append([float(x) for x in p[1:]])
    return rownames, colnames, data


# 1 - pearson にすることで、関連が強いほど0に近い値になる
def pearson(v1, v2):
    sum1 = sum(v1)
    sum2 = sum(v2)

    sum1Sq = sum([pow(v, 2) for v in v1])
    sum2Sq = sum([pow(v, 2) for v in v2])

    pSum = sum([v1[i] * v2[i] for i in range(len(v1))])

    num = pSum - (sum1*sum2/len(v1))
    den = sqrt((sum1Sq - pow(sum1, 2)/len(v1)) *
               (sum2Sq - pow(sum2, 2)/len(v1)))
    if den == 0:
        return 0

    return 1.0 - num/den


class bicluster:
    def __init__(self, vec, left=None, right=None, distance=0.0, id=None):
        self.left = left
        self.right = right
        self.vec = vec
        self.id = id
        self.distance = distance


def hcluster(rows, distance=pearson):
    distances = {}
    currentclustid = -1

    # クラスタは最初は行たち
    clust = [bicluster(rows[i], id=i) for i in range(len(rows))]

    while len(clust) > 1:
        lowestpair = (0, 1)
        closest = distance(clust[0].vec, clust[1].vec)

        # 全ての組をループして、最も距離の近い組を探す
        for i in range(len(clust)):
            for j in range(i+1, len(clust)):
                if (clust[i].id, clust[j].id) not in distances:
                    distances[(clust[i].id, clust[j].id)] = \
                        distance(clust[i].vec, clust[j].vec)

                d = distances[(clust[i].id, clust[j].id)]

                if d < closest:
                    closest = d
                    lowestpair = (i, j)

        # 2つのクラスタの平均を計算する
        mergevec = [
            (clust[lowestpair[0]].vec[i] + clust[lowestpair[1]].vec[i]) / 2.0
            for i in range(len(clust[0].vec))
        ]

        # 新たなクラスタを作る
        newcluster = bicluster(mergevec, left=clust[lowestpair[0]],
                               right=clust[lowestpair[1]], distance=closest,
                               id=currentclustid)

        currentclustid -= 1
        del clust[lowestpair[0]]
        del clust[lowestpair[1] - 1]
        clust.append(newcluster)

    return clust[0]


def printclust(clust, labels=None, n=0):
    # 階層型のレイアウトにするためにインデントする
    for i in range(n):
        sys.stdout.write('  ')
    if clust.id < 0:
        # 枝の情報
        print('-')
    else:
        # 葉 (終端)
        if labels is None:
            print(clust.id)
        else:
            print(labels[clust.id])

    if clust.left is not None:
        printclust(clust.left, labels, n=n + 1)
    if clust.right is not None:
        printclust(clust.right, labels, n=n + 1)


def getHeight(clust):
    if clust.left is None and clust.right is None:
        return 1

    return getHeight(clust.left) + getHeight(clust.right)


def getDepth(clust):
    # 終端への距離は0.0
    if clust.left is None and clust.right is None:
        return 0

    # 枝の距離は2つの方向の大きい方にそれ自身の距離を足したもの
    return max(getDepth(clust.left), getDepth(clust.right)) + clust.distance


def drawdendrogram(clust, labels, jpeg='clusters.jpg'):
    # 高さと幅
    h = getHeight(clust) * 20
    w = 1200
    depth = getDepth(clust)

    # 幅は固定されているため、適宜縮尺する
    scaling = float(w - 150)/depth

    # 白を背景とする新しい画像を作る
    img = Image.new('RGB', (w, h), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.line((0, h/2, 10, h/2), fill=(255, 0, 0))

    # 最初のノードを書く
    drawnode(draw, clust, 10, (h/2), scaling, labels)
    img.save(jpeg, 'JPEG')


def drawnode(draw, clust, x, y, scaling, labels):
    if clust.id < 0:
        h1 = getHeight(clust.left) * 20
        h2 = getHeight(clust.right) * 20
        top = y - (h1 + h2) / 2
        bottom = y + (h1 + h2) / 2
        # 直線の長さ
        ll = clust.distance*scaling

        # クラスタから子への垂直な直線
        draw.line((x, top + h1 / 2, x, bottom - h2 / 2), fill=(255, 0, 0))

        # 左側のアイテムへの水平な直線
        draw.line((x, top + h1 / 2, x + ll, top + h1 / 2), fill=(255, 0, 0))

        # 右側のアイテムへの水平な直線
        draw.line((x, bottom - h2 / 2, x + ll, bottom - h2 / 2),
                  fill=(255, 0, 0))

        # 左右のノードたちを描く関数を呼び出す
        drawnode(draw, clust.left, x + ll, top + h1 / 2, scaling, labels)
        drawnode(draw, clust.right, x + ll, bottom - h2 / 2, scaling, labels)

    else:
        # 終点であればアイテムのラベルを描く
        draw.text((x + 5, y - 7), labels[clust.id], (0, 0, 0))


def rotatematrix(data):
    newdata = []
    for i in range(len(data[0])):
        newrow = [data[j][i] for j in range(len(data))]
        newdata.append(newrow)
    return newdata


def kcluster(rows, distance=pearson, k=4):
    # それぞれのポイントの最小値と最大値を決める
    ranges = [(min([row[i] for row in rows]), max([row[i] for row in rows]))
              for i in range(len(rows[0]))]

    # 重心をランダムにk個配置する
    clusters = [[random.random() * (ranges[i][1] - ranges[i][0]) + ranges[i][0]
                for i in range(len(rows[0]))] for j in range(k)]

    lastmatches = None

    for t in range(100):
        print('Iteration %d' % t)
        bestmatches = [[] for i in range(k)]

        # それぞれの行に対して、もっとも近い重心を探し出す
        for j in range(len(rows)):
            row = rows[j]
            bestmatch = 0
            for i in range(k):
                d = distance(clusters[i], row)
                if d < distance(clusters[bestmatch], row):
                    bestmatch = i
            bestmatches[bestmatch].append(j)

        if bestmatches == lastmatches:
            break
        lastmatches = bestmatches

        # 重心をそのメンバーの平均に移動する
        for i in range(k):
            avgs = [0.0] * len(rows[0])
            if len(bestmatches[i]) > 0:
                for rowid in bestmatches[i]:
                    for m in range(len(rows[rowid])):
                        avgs[m] += rows[rowid][m]
                for j in range(len(avgs)):
                    avgs[j] /= len(bestmatches[i])
                clusters[i] = avgs

    return bestmatches

# データ読み込み
print('Loading Data...')
loadstart = time.time()
blognames, words, data = readfile('./data/cluster/blogdata.txt')
print(str(time.time() - loadstart) + ' sec')

# ブログ記事のクラスタ作成
print('construct blog clustering...')
clustering_start = time.time()
clust = hcluster(data)
print(str(time.time() - clustering_start) + ' sec')

# printclust(clust, labels=blognames)
drawdendrogram(clust, blognames, jpeg='blogclust.jpg')

# 単語のクラスタ生成
'''
print('construct word clustering...')
clustering_start = time.time()
rdata = rotatematrix(data)
wordclust = hcluster(rdata)
print(str(time.time() - clustering_start) + ' sec')
drawdendrogram(wordclust, words, jpeg='wordclust.jpg')
'''

kclust = kcluster(data, k=10)
