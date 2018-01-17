import subprocess
import os

importers = 1


def run():
    processes = []
    print('Sending data')

    for i in range(importers):
        processes.append(subprocess.Popen(['python', 'coosto_importer.py', '--files', 'sample_alltweets.csv']))

    processes[::-1][0].wait()
    exit(0)


if __name__ == '__main__':
    os.chdir(os.getcwd())
    run()
