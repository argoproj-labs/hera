from hera.models import Toleration, OperatorModel, Effect


GPUToleration = Toleration(key="nvidia.com/gpu", operator=OperatorModel.equal, value="present", effect=Effect.no_schedule)
"""GPUToleration denotes a GPU toleration. This works on GKE and Azure but not necessarily on platforms like AWS"""
