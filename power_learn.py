import sys
import numpy as np
import random
import math
import autograd.numpy as np
from autograd import grad
from matplotlib import pyplot as plt
import tableau as tab

def predict_probs (viols, e, w):
  harmonies = np.multiply(viols ** e, w)
  exp_harmonies = []
  for tab in harmonies:
    tab_harmonies = []
    for cand in tab:
      # print(sum(cand)*(-1))
      tab_harmonies.append(np.exp(sum(cand)*(-1)))
    exp_harmonies.append(tab_harmonies)
  exp_harmonies = np.array(exp_harmonies)

  Z = np.array([sum(h) for h in exp_harmonies])
  Z = np.reshape(np.repeat(Z, exp_harmonies.shape[1], axis=0), exp_harmonies.shape)

  pred = exp_harmonies / Z

  return pred

def loss_func (observed_probs, viols, e, w):

  pred_probs = predict_probs(viols, e, w)
  pred_probs_flat = np.clip(pred_probs.flatten(), 1e-20, 1)
  observed_probs_flat = observed_probs.flatten()
  loss = np.sum(-np.log(pred_probs_flat) * observed_probs_flat)  #smallest when two are equal
  return loss


def loss_grad(obs_prob, viols, e, w):
  g = grad(loss_func, [2, 3])
  dLde, dLdw = g(obs_prob, viols, e, w)
  return dLde, dLdw

def set_to_one(p): 
  if p < 1: p = float(1)
  return p

def learning (obs_probs, violations, powers, weights, max_iters, lr_w, lr_e):
  max_iters = max_iters
  lr_w = lr_w
  lr_e = lr_e

  losses = []

  for i in range(max_iters):
    dLde, dLdw = loss_grad(obs_probs, violations, powers, weights)
    powers = np.subtract(powers, np.multiply(dLde, lr_e))
    powers = np.array(list(map(set_to_one, powers)))
    weights = np.subtract(weights, np.multiply(dLdw, lr_w))
    new_probs = predict_probs(violations, powers, weights)
    loss = loss_func(obs_probs, violations, powers, weights)
    losses.append(loss)
    print(i, "{:.3f}".format(loss), ["{:.3f}".format(i) for i in weights], ["{:.3f}".format(i) for i in powers])
    print(np.round(new_probs, 3))
    print('\n')

    if len(losses) > 2:
      if loss > losses[-1]:
        print("converged")
        fig, ax1 = plt.subplots()
        ax1.plot(losses)
        ax1.set_xlabel('Iterations')
        ax1.set_ylabel('Loss')        
        plt.show()
        sys.exit()

  fig, ax1 = plt.subplots()
  ax1.plot(losses)
  ax1.set_xlabel('Iterations')
  ax1.set_ylabel('Loss')
  plt.show()


if __name__ == "__main__":
  inputfile = str(sys.argv[1])
  max_iters = int(sys.argv[2])
  lr_w = float(sys.argv[3]) # learning rate for weights (0.1)
  lr_e = float(sys.argv[4]) # learning rate for powers (0.01)
  tableau = tab.file_open(inputfile)
  cons, powers, weights = tab.cons_extractor(tableau)
  obs_probs, violations = tab.fv_extractor(tableau)
  learning(obs_probs, violations, powers, weights, max_iters, lr_w, lr_e)