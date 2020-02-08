from QueueSim2 import QueueModel
from QueueSim2 import Simulation
from QueueSim2 import desired_distribute

class QueueSim5(Simulation):
  """
  QueueSim5 の具象クラス
  """
  def __init__(self):
    """
    QueueModel を設定する
    Notes:
      モデルは三段構成だが、2段目が並列化されているため4つ作成
      窓口処理時間は指数分布に従い
      平均処理時間は3分
      窓口数は1
    """
    super(QueueSim5, self).__init__()
    for i in range(4):
      self.qs.append(QueueModel(num_counters = 1,
                 service_time_algorithm = 'e',
                 average_service_time = 3*60)) # モデルのインスタンス
    self.l1 = 0 # lambda1 からの次回到着時刻
    self.l2 = 0 # lambda2 からの次回到着時刻

  def next_arrival(self, t):
    """
    次の顧客の到着予想時刻の算出
    Args:
      t: 現在時刻(単位時間)
    Returns:
      int: 次に顧客が到着する時刻 (単位時間)
    Notes:
      指数分布に従い, 平均10分間隔で到着するlambda1 と、同 lambda2 の合成
    """
    if self.l1 <= t:
      # lambda1 の次回到着時刻の計算
      self.l1 = t + desired_distribute('e', 10*60)
    elif self.l2 <= t:
      # lambda2 の次回到着時刻の計算
      self.l2 = t + desired_distribute('e', 10*60)
    # lambda1 と lambda2 の内早く到着する方の時刻を返す
    return min(self.l1, self.l2)
  
  def clear_cal(self):
    """
    シミュレーションの初期化
    Notes:
      lambda1 と lambda2 の次回到着時刻を初期化するためにオーバーライド
    """
    super(QueueSim5, self).clear_cal()
    self.l1 = 0
    self.l2 = 0
 
  def tick(self, tick):
    """
    一単位時間の処理
    Args:
      tick: 現在時刻
    Notes:
      モデル間の配送が特殊なためオーバーライド
    """
    # モデルでの処理
    next_ev = float('inf')
    for i, q  in enumerate(self.qs):
      o = q.tick(tick)
      if o:
        #先頭のモデルからの出力は、2段目のうちキューが短い方へ配送
        if i is 0:
          # モデルの窓口数が1であり、1tick1出力である為、出力毎に振り分ける必要はない。
          target_q = 2 if self.qs[1].getQl() > self.qs[2].getQl() else 1
          self.qs[target_q].enqueue(tick,o)
          next_ev = min(next_ev, self.qs[target_q].next_ev())
        #2段目のモデルからの出力は最終段へ配送
        elif i is not 3:
          self.qs[3].enqueue(tick,o)
          next_ev = min(next_ev, self.qs[3].next_ev())
      next_ev = min(next_ev, q.next_ev())
    return next_ev

sim = QueueSim5()
sim.simulate()
