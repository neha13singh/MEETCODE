# 1. Use Alpine Linux as the base image for a lightweight container
FROM alpine:latest

# 2. Set the working directory
WORKDIR /app

# 3. Install G++ (for C++), Make (build tool), and Python3 (for the runner script)
RUN apk add --no-cache build-base python3

# 4. Create a non-root user 'coderunner' for security
RUN adduser -D coderunner

# 5. Copy the compiled runner script into the container as 'runner.py'
COPY execution/runner_compiled.py runner.py

# 6. Change ownership of the app directory to the non-root user
RUN chown -R coderunner:coderunner /app

# 7. Switch to the non-root user
USER coderunner

# 8. Set environment variables
ENV PYTHONUNBUFFERED=1
ENV LANGUAGE=cpp

# 9. Default command to run the python runner script
CMD ["python3", "runner.py"]
