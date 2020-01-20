# pylint: disable=not-callable
# pylint: disable=no-member

import torch
import numpy as np


class Buffer(object):
    def __init__(
        self,
        state_size,
        action_size,
        ensemble_size,
        normalizer,
        buffer_size=10 ** 6,
        device="cpu",
    ):
        self.state_size = state_size
        self.action_size = action_size
        self.ensemble_size = ensemble_size
        self.buffer_size = buffer_size
        self.device = device

        self.states = torch.zeros(buffer_size, state_size).float().to(self.device)
        self.actions = torch.zeros(buffer_size, action_size).float().to(self.device)
        self.rewards = torch.zeros(buffer_size, 1).float().to(self.device)
        self.state_deltas = torch.zeros(buffer_size, state_size).float().to(self.device)
        self.terminals = torch.zeros(buffer_size, 1).long().to(self.device)

        self.normalizer = normalizer

        self.n_elements = 0

    def add(self, state, action, reward, next_state, terminal):
        idx = self.n_elements % self.buffer_size

        state_delta = next_state - state

        self.states[idx] = state
        self.actions[idx] = action
        self.rewards[idx] = reward
        self.state_deltas[idx] = state_delta
        self.terminals[idx] = terminal

        self.n_elements += 1

        if self.normalizer is not None:
            self.normalizer.update(state, action, state_delta)

    def get_train_batches(self, batch_size):
        size = len(self)
        indices = [
            np.random.permutation(range(size)) for _ in range(self.ensemble_size)
        ]
        indices = np.stack(indices).T

        for i in range(0, size, batch_size):
            j = min(size, i + batch_size)

            if (j - i) < batch_size and i != 0:
                return

            batch_size = j - i

            batch_indices = indices[i:j]
            batch_indices = batch_indices.flatten()

            states = self.states[batch_indices]
            actions = self.actions[batch_indices]
            rewards = self.rewards[batch_indices]
            state_deltas = self.state_deltas[batch_indices]
            terminals = self.terminals[batch_indices]

            states = states.reshape(self.ensemble_size, batch_size, self.state_size)
            actions = actions.reshape(self.ensemble_size, batch_size, self.action_size)
            rewards = rewards.reshape(self.ensemble_size, batch_size, 1)
            state_deltas = state_deltas.reshape(
                self.ensemble_size, batch_size, self.state_size
            )
            terminals = terminals.reshape(self.ensemble_size, batch_size, 1)

            yield states, actions, rewards, state_deltas, terminals

    @property
    def size(self):
        return self.n_elements

    def __len__(self):
        return min(self.n_elements, self.buffer_size)