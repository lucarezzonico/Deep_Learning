import torch
import torch.nn as nn
from torch import optim


from Miniproject_1.other.net import *
# model.py will be imported by the testing pipeline

class Model():
    def __init__(self, net='Net', lr=1e-3, optimizer='Adam', criterion='MSE', scheduler_gamma=1) -> None:
        ## instantiate model + optimizer + loss function + any other stuff you need

        if net == 'Net':
            self.model = Net()
        if net == 'Net2':
            self.model = Net2()
        if net == 'Net3':
            self.model = Net3()

        self.device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
        print(self.device)
        self.model.to(self.device)

        self.learning_rate = lr

        if criterion == 'MSE':
            self.criterion = nn.MSELoss()
        if criterion == 'CrossEntropyLoss':
            self.criterion = nn.CrossEntropyLoss()

        if optimizer == 'SGD':
            self.optimizer = optim.SGD(self.model.parameters(), lr=self.learning_rate)
        if optimizer == 'Adam':
            self.optimizer = optim.Adam(self.model.parameters(), lr=self.learning_rate)
        if optimizer == 'Adagrad':
            self.optimizer = optim.Adagrad(self.model.parameters(), lr=self.learning_rate)
        if optimizer == 'Adadelta':
            self.optimizer = optim.Adadelta(self.model.parameters(), lr=self.learning_rate)

        # self.scheduler = optim.lr_scheduler.StepLR(self.optimizer, step_size=1, gamma=scheduler_gamma)

    def save_model(self, path='Miniproject_1/bestmodel.pth') -> None:
        ## This saves the parameters of the model into bestmodel.pth
        torch.save(self.model.state_dict(), path)
        # print('model saved to bestmodel.pth')

    def load_pretrained_model(self, path='Miniproject_1/bestmodel.pth') -> None:
        ## This loads the parameters saved in bestmodel.pth into the model
        m_state_dict = torch.load(path)
        self.model.load_state_dict(m_state_dict)
        # print('model loaded')

    def train(self, train_input, train_target, num_epochs=7, mini_batch_size=8, lambda_l2=0) -> None:
        #: train_input : tensor of size (N, C, H, W) containing a noisy version of the images.
        #: train_target : tensor of size (N, C, H, W) containing another noisy version of the same images, which only differs from the input by their noise.

        train_input, train_target = train_input.to(self.device), train_target.to(self.device)

        train_input = train_input.float().div(255)
        train_target = train_target.float().div(255)

        for e in range(num_epochs):
            for b in range(0, train_input.size(dim=0), mini_batch_size):
                output = self.model(train_input.narrow(dim=0, start=b, length=mini_batch_size))  # takes time
                loss = self.criterion(output, train_target.narrow(dim=0, start=b, length=mini_batch_size))
                self.optimizer.zero_grad()

                # # L2 penalty term (to avoid overfitting the training data for an increasing number of epochs)
                # for p in self.model.parameters():
                #     loss += lambda_l2 * p.pow(2).sum()

                loss.backward()  # takes time
                self.optimizer.step()

            print('epoch {:d}/{:d}'.format(e + 1, num_epochs), 'training loss = {:.5f}'.format(loss))
            # self.scheduler.step()  # decrease learning rate

    def predict(self, test_input) -> torch.Tensor:
        #: test_input : tensor of size (N1 , C, H, W) that has to be denoised by the trained or the loaded network.
        #: returns a tensor of the size (N1 , C, H, W)

        test_input = test_input.to(self.device)

        test_input = test_input.float().div(255)
        predicted_output = self.model(test_input)
        predicted_output = predicted_output.mul(255).to(torch.uint8)

        return predicted_output
