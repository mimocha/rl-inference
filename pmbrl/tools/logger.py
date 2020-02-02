import os
from datetime import datetime

from torch.utils.tensorboard import SummaryWriter


class Logger(object):
    def __init__(self, logdir="log", seed=None, log_every=20):
        self.log_every = log_every
        self.path = logdir + "/" + str(seed)
        self.writer = SummaryWriter(self.path)

        self.outfile = self.path + "/out.txt"
        f = open(self.outfile, "w")
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        f.write(current_time)
        f.close()

    def log(self, string):
        f = open(self.outfile, "a")
        f.write("\n")
        f.write(str(string))
        f.close()
        print(string)

    def log_scalar(self, name, value, episode):
        self.writer.add_scalar(name, value, episode)
        msg = "[{}] {}: {:.2f}"
        self.log(msg.format(episode, name, value))

    def log_figure(self, name, fig, episode):
        self.writer.add_figure(name, fig, episode, close=True)

    def close(self):
        self.writer.close()

