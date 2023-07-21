# Used to trigger a build for a data job image.

FROM versatiledatakit/job-builder:latest

# overwrite the Dockerfile used to build VDK jobs with our own with extra security hardening.
COPY Dockerfile.python.vdk /workspace/Dockerfile
