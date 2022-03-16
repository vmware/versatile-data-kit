# Setup environment for AMLD workshop

Here are scripts that preapre the backend enviornment to be used in AMLD workshop.
They are installed in same kubernetes cluster as one used by CICD - See https://github.com/vmware/versatile-data-kit/wiki/Gitlab-CICD#how-to-connect-to-cicd-kubernetes
The kubernetes namespace is "vdk-amld"

The entry point is the setup-env.sh script.
It will
- Install Pipelins Control Service
- Install trino with mysql as backend catalog

Aside from that because my binder allows connections only on port 80 or 443 (and a few more: https://github.com/jupyterhub/mybinder.org-deploy/blob/master/mybinder/values.yaml#L46)
we use API gateway to expose those :

https://us-west-1.console.aws.amazon.com/apigateway/main/develop/auth/attach?api=iaclqhm5xk&integration=qbji9io&region=us-west-1&routeKey=&routes=taal8qu&stage=$default

1. Go to API Gateway -> Click Create API -> Follow instructions
2. Then make sure to set in routes configuration . "$default" so that all paths are proxied
