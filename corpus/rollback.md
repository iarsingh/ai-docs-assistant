# Rollback

Rollback is reverting the commit in the GitOps repository. Argo CD syncs the previous manifest. Nobody runs kubectl against production by hand.

# Who approves

A change to staging needs one reviewer from the owning team. The person who opened the pull request cannot approve it.
