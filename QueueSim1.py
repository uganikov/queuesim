#分布付きランダム関数用
import numpy
import random
#list への順序を維持した insert 用
import bisect
#統計処理用 (95%信頼区間)
import math
from scipy import stats

#パラメータ
totalTry = 10
totalTime = 10000000 #試行時間(秒)
little_L = 60    #館内人数、リトルの公式のL
little_W = 300   #平均滞在時間(分)、リトルの公式のW

def cal():
  #館内滞在者リストの辞書
  visitors = {}
  #リストには滞在者が退館する時間がシミュレーション開始時点からの経過時間(分)で記録される
  #リストは退館時間順にソートされている
  visitors['e'] = []  #滞在時間が指数分布に従った際の館内滞在者のリスト
  visitors['r'] = []  #滞在時間が一様分布に従った際の館内滞在者のリスト
  visitors['c'] = []  #滞在時間が一定分布に従った際の館内滞在者のリスト

  #入館者の累計の辞書
  num_visitors = {}
  num_visitors['e'] = 0 #滞在時間が指数分布に従った際の入館者の累計
  num_visitors['r'] = 0 #滞在時間が一様分布に従った際の入館者の累計
  num_visitors['c'] = 0 #滞在時間が一定分布に従った際の入館者の累計

  #最小と最大滞在時間
  min_stay = {}
  max_stay = {}

  #入館処理
  #引数 type: 入館者が従う滞在時間の分布
  #引数 avg:  平均滞在時間
  #戻り値 パラメータから計算された入館者の滞在時間
  def checkin(type, avg):
    # デフォルトは一定分布であり、平均滞在時間滞在する
    ret = avg
    if type == 'e':
      # 指数分布に従う場合
      ret = - ret * math.log(random.random()) 
    elif type == 'r':
      # 一様分布に従う場合
      ret = ret * 2 * random.random()
    # 最小滞在時間、最大滞在時間を更新
    if type in min_stay:
      min_stay[type] = min(min_stay[type], ret)
    else:
      min_stay[type] = ret
    if type in max_stay:
      max_stay[type] = max(max_stay[type], ret)
    else:
      max_stay[type] = ret
    return ret

  tick = 0
  while tick < totalTime+1:
    for type in ['e', 'r', 'c']:
      #退場処理 退場時間に達した人は退場する
      #リストはソート済みであるため、リストの先頭要素の退館時刻がtickを下回っているものを削除する
      while len(visitors[type]) and visitors[type][0] < tick:
        visitors[type].pop(0)

      #入場処理 little_L に達するまで入場する
      while len(visitors[type]) < little_L:
        num_visitors[type] += 1
        bisect.insort(visitors[type], tick + checkin(type, little_W * 60))
    # 次回処理時刻の計算。最も早く退館する者が退館した直後の単位時刻
    tick = int(min(visitors['e'][0], visitors['r'][0], visitors['c'][0])) + 1

  #最終結果の出力
  print('lambda  ', 
      '{:.6}'.format(totalTime/num_visitors['e']), 
      '{:.6}'.format(totalTime/num_visitors['r']), 
      '{:.6}'.format(totalTime/num_visitors['c']))
  print('     min', 
      '{:>7}'.format(int(min_stay['e'])), 
      '{:>7}'.format(int(min_stay['r'])), 
      '{:>7}'.format(int(min_stay['c'])))
  print('     max', 
      '{:>7}'.format(int(max_stay['e'])), 
      '{:>7}'.format(int(max_stay['r'])), 
      '{:>7}'.format(int(max_stay['c'])))
  return totalTime/num_visitors['e'], totalTime/num_visitors['r'], totalTime/num_visitors['c']

results={}
results['e'] = []  #滞在時間が指数分布に従った際のシミュレーション結果のリスト
results['r'] = []  #滞在時間が一様分布に従った際のシミュレーション結果のリスト
results['c'] = []  #滞在時間が一定分布に従った際のシミュレーション結果のリスト
print('             exp    rand   const')
for i in range(totalTry):
  e, r, c = cal()
  results['e'].append(e)
  results['r'].append(r)
  results['c'].append(c)

for k, result in results.items():
  # 95% 信頼区間を計算する
  mi, ma = stats.t.interval(alpha=0.95,
                   df=len(result)-1,
                   loc=numpy.mean(result),
                   scale=math.sqrt(numpy.var(result) / len(result)))
  print(k, (mi+ma)/2, "(", mi, "...", ma, ")")


