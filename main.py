import sys
from app import AppNoxia

if __name__ == "__main__":
    try :
        app = AppNoxia()
        app.mainloop()
    except KeyboardInterrupt:
        sys.exit(0)