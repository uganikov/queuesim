from QueueSim2 import QueueModel
from QueueSim2 import Simulation
from QueueSim2 import desired_distribute

class QueueSim4(Simulation):
  """
  QueueSim4 の具象クラス
  """
  def __init__(self):
    """
    QueueModel を設定する
    Notes:
      モデルは三段構成
      窓口処理時間は指数分布に従い
      平均処理時間は3分
      窓口数は1
    """
    super(QueueSim4, self).__init__()
    for i in range(3):
      self.qs.append(QueueModel(num_counters = 1,
                 service_time_algorithm = 'e',
                 average_service_time = 3*60)) # モデルのインスタンス

  def next_arrival(self, t):
    """
    次の顧客の到着予想時刻の算出
    Args:
      t: 現在時刻(単位時間)
    Returns:
      int: 次に顧客が到着する時刻 (単位時間)
    Notes:
      指数分布に従い, 平均5分間隔で到着する
    """
    return t + desired_distribute('e', 5*60)

sim = QueueSim4()
sim.simulate()
