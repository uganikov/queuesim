from QueueSim2 import QueueModel
from QueueSim2 import Simulation
from QueueSim2 import desired_distribute

class QueueSim3(Simulation):
  """
  QueueSim3 の具象クラス
  """
  def __init__(self):
    """
    QueueModel を設定する
    Notes:
      モデルは一段構成
      窓口処理時間は指数分布に従い
      平均処理時間は2分
      窓口数は4
    """
    super(QueueSim3, self).__init__()
    self.qs.append(QueueModel(num_counters = 4,
                 service_time_algorithm = 'e',
                 average_service_time = 2*60)) # モデルのインスタンス

  def next_arrival(self, t):
    """
    次の顧客の到着予想時刻の算出
    Args:
      t: 現在時刻(単位時間)
    Returns:
      int: 次に顧客が到着する時刻 (単位時間)
    Notes:
      ポアソン分布に従い, 平均1分間隔で到着する
      ポアソン分布に従い生起する事象が次に生起するまでの間隔は指数分布に従う
    """
    return t + desired_distribute('e', 1*60)

sim = QueueSim3()
sim.simulate()
