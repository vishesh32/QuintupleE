from models import Tick
from pymongo import MongoClient
import torch


def get_db():
    client = MongoClient(
        "mongodb+srv://smartgrid_user:OzVu9hnKiaJULToP@autodocs.kwrryjv.mongodb.net/?retryWrites=true&w=majority&appName=Autodocs"
    )
    db = client["smartgrid"]
    return db


def compute_returns(rewards, gamma=0.99):
    rewards = torch.tensor(rewards, dtype=torch.float32)
    returns = []
    R = 0

    for r in reversed(rewards):
        R = r + gamma * R
        returns.insert(0, R)

    returns = torch.tensor(returns, dtype=torch.float32)
    mean = returns.mean()
    std = returns.std()

    # Print the mean and standard deviation
    print("Returns before normalization:", returns)
    print("Mean of returns:", mean.item())
    print("Standard deviation of returns:", std.item())

    returns = (returns - mean) / (std + 1e-8)  # Normalize returns
    return returns


def backprop(policy_network, log_probs, returns):
    returns = torch.tensor(returns, dtype=torch.float32)

    policy_loss = 0
    policy_network.optimizer.zero_grad()
    for log_prob, R in zip(log_probs, returns):
        policy_loss += -log_prob * R

    print(policy_loss)
    policy_loss.backward()
    policy_network.optimizer.step()

    return policy_loss.item()

    # policy_loss = policy_loss.mean()


def print_release_store(amt, text):
    if amt > 0:
        print(f"Rel {text}:", round(amt, 3))
    else:
        print(f"Sto {text}:", round(amt, 3))


def get_ema(data, N):
    alpha = 2 / (N + 1)
    ema = [data[0]]  # Start with the first value
    for i in range(1, len(data)):
        ema.append(alpha * data[i] + (1 - alpha) * ema[-1])
    return ema


def backprop(policy_network, log_probs, returns, states):

    returns = torch.tensor(returns, dtype=torch.float32)

    policy_loss = 0
    for i, (log_prob, R) in enumerate(zip(log_probs, returns)):
        policy_loss += -log_prob * R

    policy_loss /= len(log_probs)

    # Backward pass for policy network
    policy_network.optimizer.zero_grad()
    policy_loss.backward(retain_graph=True)
    policy_network.optimizer.step()

    return policy_loss.item()
