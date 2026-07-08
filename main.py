import uvicorn
from api.api import app


# Run the application at Vercel
if __name__ == '__main__': #this indicates that this a script to be run
   uvicorn.run("api:app", host='0.0.0.0', port=8000, log_level="info", reload = True)