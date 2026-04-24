"""Point d'entrée principal de l'application Noxia Security Dashboard."""

import sys
from ui.app import App

if __name__ == "__main__":
    try:
        app = App()
        app.mainloop()
    except KeyboardInterrupt:
        sys.exit(0)