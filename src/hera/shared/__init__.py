"""The shared module of Hera provides control over global configurations, hooks, and some base mixins."""

from hera.shared._global_config import BaseMixin, GlobalConfig, global_config, register_pre_build_hook

__all__ = ["global_config", "register_pre_build_hook", "GlobalConfig", "BaseMixin"]
