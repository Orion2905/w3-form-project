from w3form import create_app
import os
from dotenv import load_dotenv

load_dotenv()
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True)
