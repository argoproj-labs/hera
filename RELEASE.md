# Hera release process

Hera's release process relies on [Release drafter](https://github.com/release-drafter/release-drafter) for automatically deciding the version to bump, generating a changelog in the Github Release.

Release drafter automatically creates draft releases that are visible to maintainers and keep it up-to-date with the appropriate git-tag, version number and changelog based on the merged pull-requests and their labels.

## Versioning

Each pull-request must be labeled with one of the following labels -

- semver:major
- semver:minor
- semver:patch

Once the pull-request is merged, based on the semver label on the merged pull-request, Release drafter will automatically bump up the draft release version.

## Changelog

Each pull-request must be labeled with one of the following labels -

- type:bug
- type:dependency-upgrade
- type:documentation
- type:enhancement
- type:question
- type:task
- type:skip-changelog

Once the pull-request is merged, based on the type label on the merged pull-request, Release drafter will automatically generate changelog entries with the PR title and the PR type.

## Publishing a new version

Once the maintainers are ready to publish a new version, they can go to the Github draft release at https://github.com/argoproj-labs/hera-workflows/releases.

They will find a draft release with the appropriate version and changelog that is only visible to maintainers on the repository.

<img width="1032" alt="image" src="https://user-images.githubusercontent.com/16130816/206037787-a72d4356-df29-4a41-969b-b96e42942fca.png">

They should then click on the edit icon on the top left, and make minor updates to the release if needed.

Once ready, they can click "Publish release".

<img width="492" alt="image" src="https://user-images.githubusercontent.com/16130816/206037939-72fde009-b5e1-41ed-8f6a-8da7557ca08a.png">

This will create a new git tag and release on the repository and kick off a Github action that will automatically publish the current contents on the hera repository to PyPI with the release version.
