import signal
import subprocess
import sys
import os


from smug.connection_manager import ConnectionManager

processes = []

cleaners = 2
preprocessors = 1
processors = 2
savers = 1

importers = 0


def run():
    subprocess.run(['python', 'initializers/initializer.py'])

    for i in range(cleaners):
        processes.append(subprocess.Popen(['python', 'cleaners/cleaner.py']))
    for i in range(preprocessors):
        processes.append(subprocess.Popen(['python', 'preprocessors/preprocessing.py']))
    for i in range(processors):
        processes.append(subprocess.Popen(['python', 'processors/word_vectoring_processor.py']))
    for i in range(savers):
        processes.append(subprocess.Popen(['python', 'savers/mongo_save.py']))

    print('Workers running')

    processes[::-1][0].wait()


def signal_handler(signal, frame):
    print('Killing all processes')
    for process in processes:
        process.kill()
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)

if __name__ == '__main__':
    os.chdir(os.getcwd())
    run()
