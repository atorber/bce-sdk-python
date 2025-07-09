pip install -r requirements.txt

python main.py

pyinstaller --onefile --windowed --add-data "assets;assets" main.py --name main --specpath .

pyinstaller --onefile --windowed --exclude PyQt5 --name aiak-desktop  main.py