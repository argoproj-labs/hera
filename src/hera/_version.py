# it would be ideal to have all types but pointless to bring in another package for such a brief usage
import pkg_resources  # type: ignore

version = pkg_resources.get_distribution("hera-workflows").version
