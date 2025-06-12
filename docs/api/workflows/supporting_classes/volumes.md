Argo Workflows allows you to mount volumes from many different sources. Hera provides wrappper classes for all of the
first-party Kubernetes volumes (such as [Volume][hera.workflows.volume.Volume] and
[EmptyDirVolume][hera.workflows.volume.EmptyDirVolume]), as well as third-party volumes (such as
[CinderVolume][hera.workflows.volume.CinderVolume]).

::: hera.workflows.volume
    options:
        heading: "Base Classes"
        members:
        - Volume
        - AccessMode
