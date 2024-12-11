
# Experimental Hera Features

From time to time, Hera will release a new feature under the "experimental feature" flag while we develop the feature
and ensure stability. Once the feature is stable and we have decided to support it long-term, it will "graduate" into
a fully-supported feature.

To enable experimental features you must set the feature by name to `True` in the `global_config.experimental_features`
dictionary before using the feature:

```py
global_config.experimental_features["NAME_OF_FEATURE"] = True
```

Note that experimental features are subject to breaking changes in future releases of the same major version. We will
usually announce changes in [the Hera slack channel](https://cloud-native.slack.com/archives/C03NRMD9KPY).

Read about current experimental features in [the user guide](../user-guides/experimental-features.md).
