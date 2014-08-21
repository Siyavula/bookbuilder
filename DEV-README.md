# Notes for developers

## git branches

`master` should be kept clean and only used for releasing 'stable' versions of
the app. All additions to Master should via **Pull Request** from `develop`.

`develop` is the branch where work can be done, however, this branch must be
kept in working condition. Please do not push broken code to this branch. For
development of new features, please make a branch from `develop` and merge back
into `develop` once the feature is reasonably stable and ready for testing.

### Merging into master

Do this via Github's Pull Request feature. Remember the following:

  1. Update the version number in setup.py
  2. Update the **Changes** section in `README.md` to reflect new features and bug fixes


## Code Style

At the very minimum the code should not give any errors or warnings if run
through `pep8`. This will ensure consistent *style* through the code but will
say nothing about design.

For more detailed analysis of the code, I'm using `pylint` and I'm aiming for a
score of 9 / 10. This is of course not always possible within time constraints.
