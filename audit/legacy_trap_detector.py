# legacy_trap_detector.py
# CC0. stdlib only. Trajectories, not verdicts. Morality not substrate:
#   the structure holds energy allocation + environment drift ONLY.
#   the "calcification / persistence-seeking" reading lives in optics(), separable.
# Claim: a system splitting energy between maintain(fixed config) and adapt(track gradient)
#        diverges from its environment when maintenance stays locked while drift grows.
# Refute: if a high-maintenance allocation tracks a drifting environment with zero
#        deficit, the divergence model is wrong -> revise coupling, not the trace.

def step(config, env, maintain_frac, energy=1.0, k_adapt=1.0):
    # config tracks env only through the adapt budget; maintain budget holds config still
    adapt_budget = energy * (1.0 - maintain_frac)
    pull = k_adapt * adapt_budget * (env - config)
    config_next = config + pull
    deficit = abs(env - config_next)  # un-tracked environment = adaptation deficit
    return config_next, deficit

def run(maintain_frac, env_drift_rate=0.05, energy=1.0, T=40, config0=0.0):
    config, env, trace = config0, 0.0, []
    for t in range(T):
        env += env_drift_rate          # environment keeps evolving
        config, deficit = step(config, env, maintain_frac, energy)
        trace.append((t, round(env, 4), round(config, 4),
                      round(maintain_frac, 3), round(deficit, 4)))
    return trace

def optics(trace):
    # separate interpretive layer (NOT a structural field). reads the trace.
    final_deficit = trace[-1][4]
    slope = trace[-1][4] - trace[0][4]
    return {"final_deficit": final_deficit, "deficit_growing": slope > 0,
            "note": "rising deficit under locked maintenance = config persisting "
                    "against a moving gradient"}

if __name__ == "__main__":
    for mf in (0.1, 0.5, 0.9):
        tr = run(maintain_frac=mf)
        opt = optics(tr)
        print("maintain_frac=%.1f -> final_deficit=%.3f growing=%s"
              % (mf, opt["final_deficit"], opt["deficit_growing"]))
    print("\nsample trace @ maintain_frac=0.9 (env, config, deficit):")
    for t, e, c, m, d in run(0.9)[::8]:
        print("  t=%2d env=%.2f config=%.2f deficit=%.2f" % (t, e, c, d))
