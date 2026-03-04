import sys
import os

# Permite ejecutar el archivo directamente
if __name__ == "__main__" and __package__ is None:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from src.gui import App
else:
    from gui import App

def main():
    App().mainloop()

if __name__ == "__main__":
    main()