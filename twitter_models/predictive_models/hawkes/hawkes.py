import functools
import numpy as np
import numexpr as ne
from scipy.optimize import (minimize, root)

default_hyper_params = {
    'gap_hrs': 1 / 60 / 60  # minimum gap (in hrs) between tweets
}
default_initial_params = [0.5, 0.5, 1, 0.5, 0.5, 0.5]


def unpack_params(params):
  mu = params[0]
  alpha = params[1]
  beta = params[2]
  c_0 = params[3]
  c_1 = params[4]
  c_2 = params[5]
  return (mu, alpha, beta, c_0, c_1, c_2)


def lam_vec(t, params, timestamps):
  (mu, alpha, beta, c_0, c_1, c_2) = unpack_params(params)
  t = np.array(t)
  vt = np.vstack(t)
  dstack = np.tile(timestamps, (len(t), 1))
  past_times = dstack < vt
  dstack[np.invert(past_times)] = np.nan
  # dstack = mu + alpha*np.nansum(np.exp(-beta*(vt-dstack)),axis=1)
  # faster way because np.exp is slow:
  dif = -beta*(vt-dstack)  # pylint: disable=W0612
  e = ne.evaluate('exp(dif)')
  # e = np.exp(dif)
  nansum = np.nansum(e, axis=1)
  res = mu + c_0*np.sin(c_1*t + c_2) + alpha*nansum
  res[res <= 0] = 0.00001
  return res


def ll(params, timestamps, end_time=None):
  if end_time is None:
    end_time = timestamps[-1]
  T = end_time
  (mu, alpha, beta, c_0, c_1, c_2) = unpack_params(params)
  if mu <= 0:
    return 9999
  if beta <= 0:
    return 9999
  if beta <= alpha:
    return 9999
  term1 = -1 * np.sum((c_0*(np.cos(c_2) - np.cos(c_1*T + c_2)))/c_1 + mu*T)
  term2 = (alpha/beta) * np.sum(np.exp(-beta*(T-timestamps)) - 1)
  term3 = np.sum(np.log(lam_vec(timestamps, params, timestamps)))
  score = term1+term2+term3
  return -score


@functools.lru_cache(maxsize=3000)
def S(k, beta, history):
  if k <= 1:
    return 1
  mult = np.exp(-beta*(history[k] - history[k - 1]))
  # Stop recursing once effect gets too small.
  if mult < 0.00001:
    return 1
  return mult*S(k-1, beta, history) + 1

# from: http://radhakrishna.typepad.com/mle-of-hawkes-self-exciting-process.pdf


def simulate_next(params, history):
  (mu, alpha, beta, c_0, c_1, c_2) = unpack_params(params)

  def mu_integral(u, t_k):
    return (c_0*(np.cos(c_1*t_k + c_2) - np.cos(c_1*u + c_2)))/c_1 + mu*(u - t_k)

  def fu(u, U, k):
    rand_term = np.log(U)
    mu_term = mu_integral(u, history[k])
    s_term = S(k, beta, tuple(history))
    recursive_term = alpha/beta * s_term * \
        (1 - np.exp(-beta * (u - history[k])))
    return rand_term + mu_term + recursive_term

  U = np.random.uniform()
  solver = root(fu, history[-1], (U, len(history) - 1))
  if solver.x[0] <= history[-1]:
    raise 'error: projected timestamp before last historical timestamp'
  return solver.x[0]


def s_to_hr(s):
  return s / 60 / 60


def normalize_timestamps(timestamp_s_utc, start_time_s_utc, end_time_s_utc):
  start_time = s_to_hr(start_time_s_utc)
  timestamps = s_to_hr(timestamp_s_utc) - start_time
  timestamps = timestamps[timestamps >= 0]
  end_time = s_to_hr(end_time_s_utc) - start_time
  start_time = 0
  return (timestamps, start_time, end_time)


def estimate(data, start_time_s_utc, end_time_s_utc, initial_params=None):
  if initial_params is None:
    initial_params = default_initial_params
  (est_timestamps, _, _) = normalize_timestamps(
      np.array(data['timestamp_s_utc']), start_time_s_utc, end_time_s_utc)
  result = minimize(ll, initial_params, method='nelder-mead',
                    args=(est_timestamps))
  params = result.x
  return params


def predict(data, params, hyper_params, est_start_time_s_utc, pred_start_time_s_utc, end_time_s_utc, max_count=500):
  if pred_start_time_s_utc >= end_time_s_utc:
    raise 'Start time cannot be greater than end time'
  if pred_start_time_s_utc < data['timestamp_s_utc'][len(data['timestamp_s_utc']) - 1]:
    raise 'Start time cannot be less than the last timestamp'
  (timestamps, pred_start_time, end_time) = normalize_timestamps(
      np.array(data['timestamp_s_utc']), est_start_time_s_utc, end_time_s_utc)
  simulated_ts = []
  for _ in range(0, max_count):
    next_timestamp = simulate_next(params, timestamps.tolist() + simulated_ts)
    if next_timestamp > end_time:
      break
    if next_timestamp > pred_start_time + hyper_params['gap_hrs'] and (len(simulated_ts) == 0 or next_timestamp - simulated_ts[-1] > hyper_params['gap_hrs']):
      # only keep this if it is greater than the start time
      # and greater than the gap (10s by default) that must exist between obs
      simulated_ts.append(next_timestamp)
  return len(simulated_ts)
