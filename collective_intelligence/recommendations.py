# -*- coding: utf-8 -*-
from math import sqrt
import itertools

critics = {
    'Lisa Rose': {
        'Lady in the Water': 2.5,
        'Snakes on a Plane': 3.5,
        'Just My Luck': 3.0,
        'Superman Retuens': 3.5,
        'You, Me and Dupree': 2.5,
        'The Night Listener': 3.0,
    },
    'Gene Seymour': {
        'Lady in the Water': 3.0,
        'Snakes on a Plane': 3.5,
        'Just My Luck': 1.5,
        'Superman Retuens': 5.0,
        'You, Me and Dupree': 3.5,
        'The Night Listener': 3.0,
    },
    'Michael Phillips': {
        'Lady in the Water': 2.5,
        'Snakes on a Plane': 3.0,
        'Superman Retuens': 3.5,
        'The Night Listener': 4.0,
    },
    'Claudia Puig': {
        'Snakes on a Plane': 3.5,
        'Just My Luck': 3.0,
        'Superman Retuens': 4.0,
        'You, Me and Dupree': 2.5,
        'The Night Listener': 4.5,
    },
    'Mick LaSalle': {
        'Lady in the Water': 3.0,
        'Snakes on a Plane': 4.0,
        'Just My Luck': 2.0,
        'Superman Retuens': 3.0,
        'You, Me and Dupree': 2.0,
        'The Night Listener': 3.0,
    },
    'Jack Matthews': {
        'Lady in the Water': 3.0,
        'Snakes on a Plane': 4.0,
        'Superman Retuens': 5.0,
        'You, Me and Dupree': 3.5,
        'The Night Listener': 3.0,
    },
    'Toby': {
        'Snakes on a Plane': 4.5,
        'Superman Retuens': 4.0,
        'You, Me and Dupree': 1.0,
    }
}


# person1 と person2 のユークリッド距離を基にした類似性スコアを返す
def sim_distance(prefs, person1, person2):
    # ふたりとも評価しているアイテムのリストを得る
    si = {}
    for item in prefs[person1]:
        if item in prefs[person2]:
            si[item] = 1

    # 両者ともに評価しているものが1つもなければ0を返す
    if len(si) == 0:
        return 0

    # 全ての差の平方を足し合わせる
    sum_of_squares = sum([pow(prefs[person1][item] - prefs[person2][item], 2)
                         for item in prefs[person1] if item in prefs[person2]])

    return 1 / (1+sum_of_squares)


# person1 と person2 のピアソン相関係数を返す
def sim_pearson(prefs, p1, p2):
    si = {}
    for item in prefs[p1]:
        if item in prefs[p2]:
            si[item] = 1

    n = len(si)
    if n == 0:
        return 0

    # 全ての嗜好を合計する
    sum1 = sum([prefs[p1][it] for it in si])
    sum2 = sum([prefs[p2][it] for it in si])

    # 全ての平方を合計する
    sum1sq = sum([pow(prefs[p1][it], 2) for it in si])
    sum2sq = sum([pow(prefs[p2][it], 2) for it in si])

    # 積を合計する
    pSum = sum([prefs[p1][it] * prefs[p2][it] for it in si])

    # ピアソン相関によるスコアを計算する
    # TODO 式展開復習
    num = pSum-(sum1*sum2/n)
    den = sqrt((sum1sq-pow(sum1, 2)/n) * (sum2sq-pow(sum2, 2)/n))
    if den == 0:
        return 0

    r = (num*1.0) / den
    return r


# 最もマッチする人たち
def topMatches(prefs, person, n=5, similarity=sim_pearson):
    scores = [(similarity(prefs, person, other), other)
              for other in prefs if other != person]
    scores.sort()
    scores.reverse()
    return scores[0:n]


# 重み付き平均を使って、personへの推薦を行う
def getRecommendations(prefs, person, similarity=sim_pearson):
    scoreSums = {}
    simSums = {}
    sims = {}
    for other in prefs:
        if other == person:
            continue
        sims[other] = similarity(prefs, person, other)
        if sims[other] <= 0:
            continue
        for item in prefs[other]:
            if item not in prefs[person]:
                scoreSums[item] = scoreSums.get(item, 0) + \
                                  sims[other] * prefs[other][item]
                simSums[item] = simSums.get(item, 0) + sims[other]

    recommends = [(val / simSums[item], item)
                  for item, val in scoreSums.items()]
    recommends.sort()
    recommends.reverse()
    return recommends


def loadMovieLens(path='./data/movielens'):
    # 映画のタイトルを得る
    movies = {}
    for line in open(path+'/movies.csv'):
        (id, title) = line.split(',')[0:2]
        movies[id] = title

    # データの読み込み
    prefs = {}
    for line in open(path+'/ratings.csv'):
        (userid, movieid, rating, ts) = line.split(',')
        try:
            float(rating)
        except ValueError:
            continue
        prefs.setdefault(userid, {})
        print(rating)
        prefs[userid][movies[movieid]] = float(rating)
    return prefs


user_list = [
    'Lisa Rose',
    'Gene Seymour',
    'Michael Phillips',
    'Claudia Puig',
    'Mick LaSalle',
    'Jack Matthews',
    'Toby'
]
# ユークリッド距離で計算
cmd = list(itertools.combinations(user_list, 2))
most_similar_pair = ''
min_score = 1
for p1, p2 in cmd:
    score = sim_distance(critics, p1, p2)
    if score < min_score:
        min_score = score
        most_similar_pair = p1 + ' & ' + p2

print(most_similar_pair)
print(min_score)

# ピアソン相関係数で計算
cmd = list(itertools.combinations(user_list, 2))
most_similar_pair = ''
max_score = -1
for p1, p2 in cmd:
    score = sim_pearson(critics, p1, p2)
    if max_score < score:
        max_score = score
        most_similar_pair = p1 + ' & ' + p2

print(most_similar_pair)
print(max_score)

print(topMatches(critics, 'Toby', n=3))

print(getRecommendations(critics, 'Toby'))

ranking = {}
data = loadMovieLens()
max_user_id = max([int(k) for k, v in data.items()])
for i in range(1, max_user_id + 1):
    print(i)
    ranking[str(i)] = getRecommendations(data, str(i))[0:5]
