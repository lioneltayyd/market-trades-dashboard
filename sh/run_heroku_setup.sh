# Initial setup for Heroku. 
mkdir -p logs/runtime;
mkdir -p ~/.streamlit/;
chmod -R 777 ~/.streamlit;

# Create config file for Streamlit. 
echo "\
[server]\n\
headless=true\n\
enableCORS=true\n\
port=$PORT\n\
" > ~/.streamlit/config.toml
