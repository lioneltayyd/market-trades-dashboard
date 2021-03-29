FROM python:3.8

# Make directory inside the container. 
RUN mkdir -p /.streamlit
RUN chmod -R 777 /.streamlit
RUN mkdir -p /app

# Set the working directory inside the container.  
WORKDIR /app

# Copy the files to the working directory. 
COPY requirements.txt . 
COPY run_streamlit.py . 

# Install the dependencies. 
RUN pip install --no-cache-dir -r requirements.txt 

# Expose the container port. 
EXPOSE 8501/tcp

# By best practices, don't run the code with root user. 
USER 1000:1000

# Run the app. 
CMD ["streamlit", "run", "run_streamlit.py"] 
