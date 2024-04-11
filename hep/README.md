# Hera Enhancement Proposals (HEP)

This folder is used to manage Hera Enhancement Proposals (HEPs). An enhancement proposal is recommend for any significant change, including new features and enhancements.

## HEP Process

To get a significant feature into Hera, first, a HEP needs to be approved and merged into the hera repo. Once it is merged, it's considered 'Accepted' and may be 'Implemented' to be included in the project. These steps will get an HEP to be considered:

1. Fork the hera repo: https://github.com/argoproj-labs/hera
2. Copy 0000-template.md to `proposals/0000-<proposal-name>.md` (where '<proposal-name>' is descriptive.).
3. Fill in the details for the HEP. Any section can be marked as "N/A" if not applicable.
4. Submit a pull request. The pull request is the time to get review of the proposal from the larger community.
5. Once the pull request is approved by a maintainer, the HEP will enter the 'Final Comment Period'.

### Final Comment Period

When a HEP enters the FCP the following will happen:

1. A maintainer will apply the "Final Comment Period" label.
2. The FCP will last 7 days. If there's unanimous agreement amongst the maintainers the FCP can close early.
3. For voting, the binding votes are comprised of the maintainers. Acceptance requires ALL binding votes in favor. The absence of a vote from a party with a binding vote in the process is considered to be a vote in the affirmative. Non-binding votes are of course welcome. 
4. Each maintainer gets a veto on the proposal. If there is a veto, the HEP will go back to the development phase until consensus is met.
5. If no substantial new arguments or ideas are raised, the FCP will follow the outcome decided.
