# Hera Governance

This document outlines the governance for the overall Hera Project.

Any changes to Hera's governance and this document require a unanimous vote by all TOC members.

All votes mentioned in this document follow a [lazy-consensus process](https://medlabboulder.gitlab.io/democraticmediums/mediums/lazy_consensus/) with a default time-period of 2 weeks unless they are mentioned to be unanimous in which case they require unanimous consensus from all binding voters.

## Roles and Membership

The current members are defined in [MEMBERS.md](MEMBERS.md)

### TOC

Hera TOC members are maintainers who have made substantial contributions to the project. The Hera TOC is modeled on the CNCF TOC as a technical governing body. It oversees all aspects of the project and has a mandate to drive consensus for:

- Defining and maintaining the technical vision for the project
- Fostering a healthy and welcoming community, including by defining and enforcing our Code of Conduct
- Defining the governance structure of the project
- Appointing maintainers and lead
- Defining the [HEP](proposals/README.md) process through which cross-cutting changes are proposed and approved
- Defining the annual roadmap
- Responsible for handling security reports and incidents
- Anything else that falls through the cracks

#### Nomination Process

For a new TOC member to be appointed they must -

- Be a seasoned maintainer of Hera
- Have driven multiple HEPs to implementation
- Be nominated by an existing TOC member
- Be unanimously elected by the TOC

#### Privileges

TOC members will have the following permissions:
- Admin permissions on the Hera Github repository
- Ability to approve releases to PyPI
- Binding votes on [HEPs](proposals/README.md)
- Binding votes on Governance changes
- Added to hera-security-reports@googlegroups.com

### Maintainers

Maintainers are in charge of the day to day maintenance of the project including:

- Ensuring contributions align with project goals and meet the project's quality standards
- Reviewing, approving, and merging PRs
- Planning release milestones, and releasing components under the team's area of responsibility
- Representing the work of the team to the community
- Supporting contributors
- Growing the team by mentoring aspiring contributors and maintainers

#### Nomination Process

For a new maintainer to be appointed they must -

- Be a committer to Hera for at-least 2 months
- Reviewer for or author of at least 10 substantial PRs to the codebase, with the definition of substantial subject to the TOC's discretion (e.g. refactors, enhancements rather than grammar correction or one-line pulls).
- Exhibiting sound technical judgment through PR contributions
- Exhibiting sound technical judgment through PR reviews
- Be nominated by an existing maintainer/TOC member and be voted in by remaining maintainers/TOC members (via a lazy-consensus vote lasting 2 weeks)

#### Privileges

Maintainers will have the following permissions:
- Maintain permissions on the Hera Github repository
- Ability to merge PRs to protected branches
- Cutting releases (PyPI publish will still require approval from a TOC member)

### Approvers

Approvers are seasoned contributors who are responsible for:

- Ensuring contributions align with project goals and meet the project's quality standards
- Reviewing and approving PRs
- Supporting contributors

#### Nomination Process

For a new approver to be appointed they must -

- Be an author or reviewer of multiple feature or bug-fix PRs
- Exhibiting sound technical judgment through PR contributions
- Exhibiting sound technical judgment through PR reviews
- Be nominated by an existing approver (or above) or self-nominate
- Be sponsored by a maintainer/TOC member

#### Privileges

Maintainers will have the following permissions:
- Push permissions on the Hera Github repository
- Ability to approve PRs to protected branches

### Member

Project members are contributors to the project.

#### Nomination Process

For a new member to be appointed they must -

- Be a Hera user
- Exhibit interest and time to help out the project
- Be sponsored by an existing approver or above

#### Privileges

Members will have the following permissions:
- Triage permissions on the Hera Github repository
- Ability to triage issues, PRs
- Ability to assign issues
