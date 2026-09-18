import os
import json
import numpy as np
import matplotlib.pyplot as plt

def load_experiment(experiment, time, lower_percentile=0, upper_percentile=100):
    steps = []
    steps_set = False
    returns = []

    for run_path in experiment if isinstance(experiment, list) else map(lambda x: os.path.join(experiment, x), os.listdir(experiment)):
        # run_path = os.path.join(experiment, seed)
        if os.path.exists(os.path.join(run_path, "return.json.set")):
            with open(os.path.join(run_path, "return.json")) as f:
                results = json.load(f)
                for i, evaluation_step in enumerate(results):
                    if not steps_set:
                        steps.append(evaluation_step["step"])
                        returns.append([])
                    returns[i].append(np.mean(evaluation_step["returns"]))
            steps_set = True

    returns = np.array(returns)
    returns = returns.reshape((len(steps), -1))
    steps = np.array(steps)

    # mean_returns = np.mean(returns, axis=1)
    # std_returns = np.std(returns, axis=1)
    wall_time = steps/(steps.max() / time)
    upper_percentile_values = np.percentile(returns, upper_percentile, axis=1)
    lower_percentile_values = np.percentile(returns, lower_percentile, axis=1)
    iqm_mask = np.logical_and(returns >= lower_percentile_values[:, None], returns <= upper_percentile_values[:, None])
    iqm_data = np.where(iqm_mask, returns, np.nan)
    iqm_mean_returns = np.nanmean(iqm_data, axis=1)
    iqm_std_returns = np.nanstd(iqm_data, axis=1)
    return steps, wall_time, iqm_mean_returns, iqm_std_returns, returns


def get_training_duration(seed_path):
    """İlk ve son checkpoint klasörünün mtime farkından gerçek eğitim süresini hesaplar."""
    steps_dir = os.path.join(seed_path, "steps")
    if not os.path.exists(steps_dir):
        return 1
    step_dirs = sorted(os.listdir(steps_dir))
    if len(step_dirs) < 2:
        return 1
    first = os.path.getmtime(os.path.join(steps_dir, step_dirs[0]))
    last  = os.path.getmtime(os.path.join(steps_dir, step_dirs[-1]))
    return max(last - first, 1)

def discover_experiments(base="experiments", env_filter="l2f"):
    """experiments/ altındaki tamamlanmış deneyleri otomatik bulur.
    Yapı: experiments/{tarih}/{grup}/{algo_env}/{seed}/return.json.set
    """
    found = {}
    if not os.path.exists(base):
        return found
    for date_hash in sorted(os.listdir(base)):
        date_root = os.path.join(base, date_hash)
        if not os.path.isdir(date_root):
            continue
        for group in os.listdir(date_root):
            group_root = os.path.join(date_root, group)
            if not os.path.isdir(group_root):
                continue
            for algo_env in os.listdir(group_root):
                if env_filter and env_filter not in algo_env:
                    continue
                exp_path = os.path.join(group_root, algo_env)
                if not os.path.isdir(exp_path):
                    continue
                completed_seeds = [
                    seed for seed in os.listdir(exp_path)
                    if os.path.isdir(os.path.join(exp_path, seed))
                    and os.path.exists(os.path.join(exp_path, seed, "return.json.set"))
                ]
                if completed_seeds:
                    # en uzun süren seed'i referans al
                    duration = max(get_training_duration(os.path.join(exp_path, s)) for s in completed_seeds)
                    label = f"{date_hash[:10]} {algo_env}"
                    found[label] = (exp_path, duration)
    return found

experiments = discover_experiments()


combinations = [
    (True, (0, 100)),
    (True, (25, 75)),
    (True, (90, 100)),
    (False, (0, 100)),
    (False, (25, 75)),
    (False, (90, 100)),
]



cols = 3
fig, axes = plt.subplots(2, cols, figsize=(12, 10))

for idx, (use_wall_time, (iqm_lower_percentile, iqm_upper_percentile)) in enumerate(combinations):
    ax = axes[idx // cols, idx % cols]
    for experiment_name, experiment in experiments.items():
        steps, wall_time, mean_returns, std_returns, returns = load_experiment(*experiment, lower_percentile=iqm_lower_percentile, upper_percentile=iqm_upper_percentile)
        x = wall_time if use_wall_time else steps
        ax.plot(x, mean_returns, label=experiment_name)
        ax.fill_between(x, mean_returns - std_returns, mean_returns + std_returns, alpha=0.2)
    
    xlabel = "Time [s]" if use_wall_time else "Step"
    ylabel = "Returns"
    title = f"Learning Curve ({'Wall Time' if use_wall_time else 'Steps'}, {f'IQM({iqm_lower_percentile}%:{iqm_upper_percentile}%)'})"
    
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.legend()

plt.tight_layout()
plt.show()


plt.figure()
for experiment_name, experiment in experiments.items():
    steps, wall_time, mean_returns, std_returns, returns = load_experiment(*experiment)
    plt.hist(returns[-1], bins=5, density=True, label=experiment_name)
plt.legend()
plt.show()


# plt.figure(figsize=(10, 6))

# for idx, (experiment_name, experiment) in enumerate(experiments.items()):
#     steps, wall_time, mean_returns, std_returns, returns = load_experiment(*experiment)
#     plt.hist(returns[-1], bins=10, density=True, label=experiment_name, alpha=0.5, histtype='bar')

# plt.legend()
# plt.xlabel('Returns')
# plt.ylabel('Density')
# plt.title('Distribution of Returns by Experiment')
# plt.show()