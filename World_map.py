import main
import bot2
import threading
import matplotlib
matplotlib.use('TkAgg')

if __name__ == '__main__':
    bot2_thread = threading.Thread(target=bot2.main)
    main_thread = threading.Thread(target=main.main)

    bot2_thread.start()
    main_thread.start()

    bot2_thread.join()
    main_thread.join()

