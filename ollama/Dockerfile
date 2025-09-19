# Use the official Ollama image as a base
FROM ollama/ollama

# Start the server in the background, wait a moment for it to initialize,
# and then run the pull command. This must all be in one RUN instruction.
RUN /bin/sh -c "ollama serve & sleep 5 && ollama pull llama3"