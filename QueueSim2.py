import numpy
import bisect
import math
import random
from scipy import stats

def desired_distribute(a, l):
  """
  期待される分布関数
  Args:
    a: 分布アルゴリズム
       'e' 指数
       'r' 一様分布
　l: 分布の平均
  Returns:
    int: パラメータに従う次回生起までの時間(単位時間)
  Notes:
    デフォルトは一定分布に従う
  """
  #  指数分布
  if a is 'e':
    l = - l * math.log(random.random())
  #  一様分布
  elif a is 'r':
    l = l * 2 * random.random()
  return l

class QueueModel():
  """
  M/M/C キューのクラス
  Notes:
    多段接続を考慮して、到着処理は外だしにしている
  """
  def __init__(self, **kwargs):
    """
    コンストラクタ
    Args:
      kwargs: パラメータ辞書
    """
    #  待ちキュー
    self.wait_q = []
    #  カウンター
    self.counter_list = []
    #  カウンターの数。デフォルトは 1 (M/M/1)
    self.num_counters = kwargs["num_counters"] if "num_counters" in kwargs else 1
    #  サービス所要時間の分布が従うアルゴリズム。デフォルトは一様分布
    self.service_time_algorithm = kwargs["service_time_algorithm"] if "service_time_algorithm" in kwargs else 'e'
    #  平均サービス所要時間
    self.average_service_time = kwargs["average_service_time"] if "average_service_time" in kwargs else (3*60)
    self.lq = 0 # 単位時間毎のキューに入った顧客の累計
    self.lc = 0 # 単位時間毎のサービス提供中顧客の累計
    self.qmax = 0 # 単位時間毎のキューに入った顧客の累計
    self.cmax = 0 # 単位時間毎のサービス提供中顧客の累計
    self.last_tick = 0

  def desired_service_time(self):
    """
    必用なサービス時間の計算
    Notes:
      顧客が窓口で消費する時間をあらかじめアルゴリズムに従い計算しておく
    """
    return desired_distribute(self.service_time_algorithm, self.average_service_time)

  def enqueue(self, t, c=1):
    """
    顧客の到着
    Args:
      c: 到着数
    Notes:
      到着した顧客に必要なサービス時間を計算し、キューに投入する
    """
    for i in range(c):
      if(len(self.counter_list) < self.num_counters):
        bisect.insort(self.counter_list, self.desired_service_time() + t)
      else:
        self.wait_q.append(self.desired_service_time())

  def tick(self, t):
    """
    単位時間毎処理
    Args:
      t: 現在時刻(単位時間)
    Returns:
      int: 系外に出た顧客数
    Notes:
      到着した顧客に必要なサービス時間を計算し、キューに投入する
    """
    out = 0
    self.update_stat(t)
    # カウンターにいて、必要サービス時間が経過した顧客は系外に出る
    while len(self.counter_list) and self.counter_list[0] < t:
      self.counter_list.pop(0)
      out += 1
    # キューに顧客がいて、空きカウンターがある場合は空きカウンターに移動する
    while ((len(self.counter_list) < self.num_counters) and len(self.wait_q)):
      # カウンターは処理終了時刻が早い順にソートしておく
      bisect.insort(self.counter_list, self.wait_q.pop(0) + t)
    # 系外に出た顧客数を返す
    return out

  def next_ev(self):
    return self.counter_list[0] if len(self.counter_list) else float('inf')
    
  def update_stat(self, t):
    # 処理結果を統計値に反映
    dt = t - self.last_tick
    self.lq += (len(self.wait_q) * dt)
    self.lc += (len(self.counter_list) * dt)
    self.qmax = max(self.qmax, len(self.wait_q))
    self.cmax = max(self.cmax, len(self.counter_list))
    self.last_tick = t

  def getTotalLc(self):
    """
    窓口サービスを受けた顧客の累計を取得
    Returns:
      int: 窓口サービスを受けた顧客の累計
    """
    # 窓口の最大並列処理数を表示
    # M/M/1 であれば当然1となる
    print("cmax:", self.cmax)
    return self.lc

  def getTotalLq(self):
    """
    待ち行列に滞留した顧客の累計を取得
    Returns:
      int: 待ち行列に滞留した顧客の累計
    """
    # 待ち行列の最大長を表示
    print("qmax:", self.qmax)
    return self.lq

  def getQl(self):
    """
    現在の待ち行列長さを取得
    Returns:
      int: 現在の待ち行列長
    Notes:
      for QueueSim5
    """
    return len(self.wait_q)

  def clear(self):
    """
    モデルの初期化処理
    Notes:
      滞留客と統計情報をクリアする
    """
    self.wait_q.clear()
    self.counter_list.clear()
    self.lq = 0
    self.lc = 0
    self.qmax = 0
    self.cmax = 0
    self.last_tick = 0

class Simulation():
  """
  基本的なシミュレーションの実装
  """
  def __init__(self):
    """
    コンストラクタ
    """
    #パラメータ
    self.totalTime = 10000000 #シミュレーション時間(秒)
    self.totalTry = 10        #シミュレーション回数(秒)
    self.qs = []              #シミュレーションに利用する待ち行列モデルの配列

  def next_arrival(self, t):
    """
    先頭段への顧客到着判定
    Args:
      t: 現在時刻
    Returns:
      int: 次回顧客到着時刻
    Notes:
      派生クラスで実装の必要あり
    """
    raise NotImplementedError()

  def tick(self, t):
    """
    一単位時間の処理
    Args:
      t: 現在時刻
    Notes:
      一単位時間の処理をシミュレートする
    """
    # モデルでの処理
    # モデルのリストを先頭から一単位時間進めて行く
    next_ev = float('inf')
    for i, q  in enumerate(self.qs):
      o = q.tick(t)
      # 系から出た顧客がいた場合、次段のモデルがあれば投入する
      if o and len(self.qs) > i + 1:
        self.qs[i+1].enqueue(t, o)
        next_ev = min(next_ev, self.qs[i+1].next_ev())
      next_ev = min(next_ev, q.next_ev())
    return next_ev

  def cal(self):
    """
    単一シミュレーションの実行
    Returns:
      int: 平均系内客数
      int: 平均待ち客数
    """
    # 初回到着時刻の計算 
    arrival = self.next_arrival(0)
    # totalTime になるまでループ
    tick = 0
    while tick < self.totalTime:
      # 単位時間処理を実行
      next_ev = self.tick(tick)
      # 到着した顧客が居れば
      while tick >= arrival:
        # 顧客をモデルに投入
        self.qs[0].enqueue(tick)
        next_ev = min(next_ev, self.qs[0].next_ev())
        # 次の到着時刻を計算(同着あり)
        arrival = self.next_arrival(arrival)
      next_ev = min(next_ev, arrival)
      tick = int(next_ev) + 1
#      tick += 1
    self.tick(self.totalTime)

    #結果の出力（平均系内客数，平均待ち客数）
    total_lc = 0
    total_lq = 0
    for q  in self.qs:
      total_lc += q.getTotalLc()
      total_lq += q.getTotalLq()
    l = ((total_lc + total_lq) / self.totalTime)
    lq = (total_lq / self.totalTime)
    print("L = ",  l)
    print("Lq = ", lq)
    return l, lq

  def clear_cal(self):
    """
    シミュレーションの初期化
    Notes:
      モデルのリストを初期化する
    """
    for q  in self.qs:
      q.clear()

  def simulate(self):
    """
    シミュレーションの実行
    Notes:
      指定回数シミュレーションを繰り返し、
      平均系内客数と平均待ち客数の試行毎の平均と 95%信頼区間を表示する
    """
    ls = []  #各試行における平均系内客数のリスト
    lqs = [] #各試行における平均待ち客数のリスト

    # 指定回数単一シミュレーションを繰り返す
    for i in range(self.totalTry):
      self.clear_cal()
      l, lq = self.cal()
      ls.append(l)
      lqs.append(lq)

    # 95% 信頼区間を計算する
    lmi, lma = stats.t.interval(alpha=0.95,
                   df=len(ls)-1,
                   loc=numpy.mean(ls), 
                   scale=math.sqrt(numpy.var(ls) / len(ls)))
    lqmi, lqma = stats.t.interval(alpha=0.95,
                   df=len(lqs)-1,
                   loc=numpy.mean(lqs), 
                   scale=math.sqrt(numpy.var(lqs) / len(lqs)))

    # 95% 信頼区間の平均値(シミュレーションの代表値)と 95% 信頼区間を表示する
    print("L ", (lmi+lma)/2, "(", lmi, "...", lma, ")")
    print("Lq ", (lqmi+lqma)/2, "(", lqmi, "...", lqma, ")")

if __name__ == "__main__":
  class QueueSim2(Simulation):
    """
    QueueSim2 の具象クラス
    """
    def __init__(self):
      """
      QueueModel を設定する
      Notes:
        モデルは一段構成
        窓口処理時間は一様分布に従い
        平均処理時間は3分
      """
      super(QueueSim2, self).__init__()
      self.qs.append(QueueModel(service_time_algorithm='r', average_service_time=3*60))

    def next_arrival(self, t):
      """
      次の顧客の到着予想時刻の算出
      Args:
        t: 現在時刻(単位時間)
      Returns:
        int: 次に顧客が到着する時刻 (単位時間)
      Notes:
        ポアソン分布に従い, 平均5分間隔で到着する
        ポアソン分布に従い生起する事象が次に生起するまでの間隔は指数分布に従う
      """
      return t + desired_distribute('e', 5*60)

  #QueueSim2 具象クラスのインスタンス化
  sim = QueueSim2()
  #シミュレーションの実行
  sim.simulate()
