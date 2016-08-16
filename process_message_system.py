import sys
import os
import pickle
import time
import threading
import atexit
import queue


class MessageProc():

    global communcation_queue

    # set up communication mechanism (named pipes)
    def main(self):

        # create named pipe
        os.mkfifo('/tmp/pipe' + str(os.getpid()))

        communcation_queue = queue.Queue()

        # Get threading condition - robert lecture
        self.arriveCondition = threading.Condition()

        # set up thread
        transfer_thread = threading.Thread(target=self.extract_from_pipe, daemon=True)
        transfer_thread.start()



    # start up a new process and return process id to parent process
    def start(self):

        # fork
        pid = os.fork()

        # If child fork
        if pid == 0:
            # go into the main()
            self.main()

        # if parent fork
        else:
            # return pid of the child fork
            return pid


    # send the input parameter message items it receives to the recieve()
    # pid - pid of child fork
    # messageID - id type of message sent (what is checked in recieve)
    # values - not nessary to pass in
    def give(self, pid, messageID, *values):

        pipe = '/tmp/pipe' + str(pid)

        # check communitcation process is up else sleep for a bit
        if not os.path.exists(pipe):
            time.sleep(0.01)

        fifo = open(pipe, 'wb')

        # parent fork gives the message

        tup = []
        tup.append(pid)
        tup.append(messageID)

        if values:
            tup.append(*values)

        pickle.dump(tup, fifo)

        print(tup)



    # check out os atExit and clean up named pipes

    # check message does not exist in queue and remove executed messages
    def receive(self, *messages):
        pipe = '/tmp/pipe' + str(os.getpid())

        # check communitcation process is up else sleep for a bit
        if not os.path.exists(pipe):
            time.sleep(0.01)

        fifo = open(pipe, 'rb')

        print('in receive')

        #From rob's code in lecture recording 9
        while True:

            # From Tutorial 3 code
            # Automatic acquire/release of the underlying lock
            with self.messageCondition:
            # notify the waiting thread that the resource is now ready
                self.messageCondition.wait()

            #get data from queue
            data =  communcation_queue.get()

            print(data)

            for mess in messages:
                if mess.messageID == 'ANY' or mess.messageID == data[1]:
                    print('match')

                    #if there is no value given
                    if len(data)==2:
                        print('there is no value')
                        mess.action()

                    else:
                        mess.action(data[2])

                else:
                    pass





            # message = pickle.load(fifo)
            #
            # print('receive'+str(message))
            #
            # for mess in messages:
            #     if mess.messageID == 'ANY' or mess.messageID == message[1]:
            #         print('match')
            #
            #         #if there is no value given
            #         if len(message)==2:
            #             print('there is no value')
            #             mess.action()
            #
            #         else:
            #             mess.action(message[2])
            #
            #     else:
            #         pass




    #taken from Robert's lecture recording 9 video
    def extract_from_pipe(self):
        pipe = '/tmp/pipe' + str(os.getpid())

        with open(pipe,'rb') as readPipe:
            while True:
                try:
                    message = pickle.load(readPipe)
                    with self.arriveCondition:
                        self.communcation_queue.put(message)
                        self.arriveCondition.notify()
                except EOFError:
                    time.sleep(0.01)



# what to do when system ends
# def removeGarbage(self):
#     pass
#
#     # remove all pipes
#
#
# atexit.register(removeGarbage())


class Message():
    def __init__(self, messageID, action):
        self.messageID = messageID
        self.action = action

    # pass


class TimeOut():
    pass
