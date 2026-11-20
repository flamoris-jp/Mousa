#pragma once
#include <algorithm>
#include <cmath>
#include <stdexcept>
#include <vector>

namespace mousa {
inline void require(bool value, const char* message) {
  if (!value) throw std::runtime_error(message);
}

// Music semantics stay in Mousa. No learned parameter can widen this support.
struct ScaleRule {
  int tonic, period;
  std::vector<int> offsets;
  ScaleRule(int root, int repetition, std::vector<int> intervals)
      : tonic(root), period(repetition), offsets(std::move(intervals)) {
    require(tonic >= 48 && tonic <= 84, "tonic outside saved-model generation range");
    require(period >= 1 && period <= 48, "invalid scale repetition");
    require(!offsets.empty() && offsets.size() <= 64 && offsets.front() == 0,
            "scale must contain its tonic");
    for (size_t i=0; i<offsets.size(); ++i)
      require(offsets[i] >= 0 && offsets[i] < period &&
              (i == 0 || offsets[i-1] < offsets[i]), "invalid scale intervals");
  }
  bool contains(int pitch) const {
    int degree = ((pitch-tonic) % period + period) % period;
    return std::find(offsets.begin(), offsets.end(), degree) != offsets.end();
  }
  std::vector<int> allowed(int current) const {
    require(current >= 48 && current <= 84 && contains(current), "current pitch violates scale");
    std::vector<int> result;
    for (int label=12; label<=36; ++label) {
      int next = current + label - 24;
      if (next >= 48 && next <= 84 && contains(next)) result.push_back(label);
    }
    require(!result.empty(), "no allowed pitch");
    return result;
  }
};

inline std::vector<double> masked_distribution(const std::vector<double>& logits,
                                              const std::vector<int>& allowed) {
  require(logits.size() == 49 && !allowed.empty(), "empty or invalid categorical support");
  for (double value : logits) require(std::isfinite(value), "nonfinite model logits");
  std::vector<bool> seen(49, false);
  double maximum = -INFINITY;
  for (int label : allowed) {
    require(label >= 0 && label < 49 && !seen[label], "invalid/duplicate allowed label");
    seen[label] = true;
    maximum = std::max(maximum, logits[label]);
  }
  std::vector<double> probability(49, 0.0);
  double mass = 0.0;
  for (int label : allowed) mass += probability[label] = std::exp(logits[label] - maximum);
  require(std::isfinite(mass) && mass > 0, "no allowed probability mass");
  for (int label : allowed) probability[label] /= mass;
  return probability;
}
}  // namespace mousa
