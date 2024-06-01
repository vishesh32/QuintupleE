from torch import nn
import torch
import os


def init_price_lstm():
    # input_size = 1  # price
    # print(os.getcwd())
    model = PriceLSTM(1)
    model.load_state_dict(torch.load("server/price_model/model.pth"))
    model.eval()
    return model


def create_dataset(dataset: list, lookback):
    X, y = [], []
    for i in range(len(dataset) - lookback):
        # target = dataset[i + lookback][2]
        X.append([[x.sell_price] for x in dataset[i : i + lookback]])
        # y.append(dataset[i + lookback].sell_price)
        # torch.FloatTensor(y)
    return torch.FloatTensor(X)


def predict_future(model, ticks, number_of_ticks):
    # Ticks should be of size 10
    input = create_dataset(ticks, 10)

    # predict future prices
    # return list of prices
    pass


class PriceLSTM(nn.Module):
    def __init__(self, input_size, hidden_size=50, output_size=1):
        super().__init__()
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=1,
            batch_first=True,
        )
        self.linear = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        x, _ = self.lstm(x)
        last_time_step = x[:, -1, :]
        out = self.linear(last_time_step)
        return out
