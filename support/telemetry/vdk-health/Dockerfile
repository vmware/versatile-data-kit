FROM grimoirelab/full
ADD vdk_project.cfg /project.cfg
ADD vdk_github_token.cfg /override.cfg
ADD vdk_projects.json /projects.json
ENTRYPOINT ["/entrypoint.sh"]
CMD [ "-c", "/infra.cfg", "/dashboard.cfg", "/project.cfg", "/override.cfg"]
