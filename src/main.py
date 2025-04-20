from models import update_info
from web_interface import app

def main():
    update_info()

    app.run()

if __name__ == "__main__":
    main()