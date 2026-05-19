import sys
from ui.app import App

if __name__ == "__main__":
    try:
        # On lance l'app, elle gérera son propre état interne
        app = App()
        app.mainloop()
    except KeyboardInterrupt:
        sys.exit(0)