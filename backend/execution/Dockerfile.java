# 1. Use Eclipse Temurin (OpenJDK) on Alpine for Java 17 support
FROM eclipse-temurin:17-alpine

# 2. Set the working directory
WORKDIR /app

# 3. Install Python3 needed for the runner script
RUN apk add --no-cache python3

# 4. Create a non-root user 'coderunner'
RUN adduser -D coderunner

# 5. Copy the compiled runner script
COPY execution/runner_compiled.py runner.py

# 6. Change ownership to the non-root user
RUN chown -R coderunner:coderunner /app

# 7. Switch to non-root user
USER coderunner

# 8. Set environment variables
ENV PYTHONUNBUFFERED=1
ENV LANGUAGE=java

# 9. Default command to run the python runner script
CMD ["python3", "runner.py"]
