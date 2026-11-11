#include "composition.h"
#include "maidionis/training.h"
#include <cmath>
#include <iostream>
#include <limits>
#include <set>

using namespace maidionis;
namespace {
void require(bool value, const char* message) {
  if (!value) throw std::invalid_argument(message);
}
Json read_json(const std::filesystem::path& path, size_t cap = 4 * 1024 * 1024) {
  return parse_json(immutable_read(path, cap), cap);
}
Json floats(const torch::Tensor& value) {
  auto tensor = value.flatten();
  Json result = Json::array();
  for (int64_t i = 0; i < tensor.numel(); ++i) result.push_back(tensor[i].item<double>());
  return result;
}
Json metrics(ModelPtr model, const NumericalComposition& composition, const std::vector<Json>& rows) {
  require(!rows.empty(), "empty diagnostic split");
  model->eval();
  torch::NoGradGuard no;
  double total_loss = 0;
  int64_t correct = 0;
  for (size_t start = 0; start < rows.size(); start += 32) {
    const auto stop = std::min(rows.size(), start + 32);
    std::vector<Json> chunk(rows.begin() + start, rows.begin() + stop);
    auto batch = composition.encode(chunk);
    auto logits = model->forward(batch);
    total_loss += composition.objective(logits, batch).item<double>() * chunk.size();
    correct += logits.argmax(1).eq(batch.targets).sum().item<int64_t>();
  }
  return {{"samples", rows.size()}, {"correct", correct}, {"accuracy", double(correct) / rows.size()},
          {"cross_entropy", total_loss / rows.size()}, {"scope", "teacher_forced_next_token"}};
}
struct Loaded {
  NumericalComposition composition;
  ModelPtr model;
  Json manifest;
  std::string export_digest;
};
Loaded load_research_export(const std::filesystem::path& data_root, const std::string& data_digest,
                            const std::filesystem::path& export_root, const std::string& expected_export_digest) {
  auto c = music_research::composition(data_root);
  // This validates the pinned dataset identity, declared source splits, and all
  // admitted train/dev windows without changing any model parameter.
  auto data = training_data(data_root, data_digest, c);
  const auto raw_manifest = immutable_read(export_root / "manifest.json", 4 * 1024 * 1024);
  require(sha256(raw_manifest) == expected_export_digest, "trusted music export manifest digest");
  auto manifest = parse_json(raw_manifest, 4 * 1024 * 1024);
  const std::set<std::string> keys = {"schema_version", "purpose", "descriptor_digest", "dataset_digest", "build_digest",
                                    "environment_digest", "checkpoint_digest", "weights_digest", "model_config", "files"};
  require(manifest.is_object() && manifest.size() == keys.size(), "music research export envelope");
  for (const auto& key : keys) require(manifest.contains(key), "music research export member");
  require(manifest["schema_version"] == "research.music.export.v1" && manifest["purpose"] == "unadmitted_offline_research_checkpoint" &&
          manifest["descriptor_digest"] == sha256(canonical(c.registry.descriptor())) && manifest["dataset_digest"] == data_digest &&
          manifest["build_digest"] == music_research::build_digest() && manifest["environment_digest"] == sha256(numerical_environment()) &&
          manifest["model_config"] == c.model_config.json(), "music export identity/configuration");
  auto files = verified_snapshot(export_root, manifest["files"], 128 * 1024 * 1024, 64 * 1024 * 1024);
  const std::set<std::string> expected = {"best.pt", "final.pt", "state.json", "model.config.json", "training.json", "summary.json"};
  require(files.size() == expected.size(), "music export inventory coverage");
  for (const auto& name : expected) require(files.contains(name), "music export inventory member");
  require(sha256(files.at("best.pt")) == manifest["weights_digest"].get<std::string>() && parse_json(files.at("model.config.json")) == c.model_config.json(),
          "music selected weight binding");
  auto training = parse_json(files.at("training.json"), 4 * 1024 * 1024);
  auto state = parse_json(files.at("state.json"), 4 * 1024 * 1024);
  validate_record("training-state", state);
  require(training["state"] == state && training["weights_digest"] == manifest["weights_digest"] &&
          state["best_weights_digest"] == manifest["weights_digest"] && training["dataset_digest"] == data_digest &&
          training["descriptor_digest"] == manifest["descriptor_digest"] && training["build_digest"] == manifest["build_digest"] &&
          training["environment_digest"] == manifest["environment_digest"] && training["checkpoint_digest"] == manifest["checkpoint_digest"] &&
          training["model_config"] == c.model_config.json(), "music export training evidence");
  auto model = make_seeded_model(c.model_config, 42);
  load_model_bytes(model, files.at("best.pt"));
  model->eval();
  return {std::move(c), model, std::move(manifest), sha256(raw_manifest)};
}
Json export_identity(const Loaded& loaded) {
  return {{"export_digest", loaded.export_digest}, {"weights_digest", loaded.manifest["weights_digest"]},
          {"dataset_digest", loaded.manifest["dataset_digest"]}, {"build_digest", loaded.manifest["build_digest"]},
          {"status", "unadmitted_offline_research_checkpoint"}};
}
}

int main(int argc, char** argv) {
  try {
    if (argc == 2 && std::string(argv[1]) == "build-identity") {
      std::cout << canonical(Json{{"build_digest", music_research::build_digest()}, {"core_build_digest", compiled_build_digest()}});
      return 0;
    }
    if ((argc == 8 || argc == 9) && std::string(argv[1]) == "train") {
      auto c = music_research::composition(argv[2]);
      auto data = training_data(argv[2], argv[3], c);
      TrainingConfig config;
      config.seed = 42;
      config.epochs = argc == 9 ? std::stoll(argv[8]) : 30;
      config.batch_size = 32;
      config.learning_rate = .005;
      config.selection_scope = "dev";
      config.validate();
      require(std::string(argv[7]) == "0" || std::string(argv[7]) == "1", "resume flag must be 0 or 1");
      const auto max_epochs = std::stoll(argv[6]);
      auto initial = make_seeded_model(c.model_config, config.seed);
      const auto initial_train = metrics(initial, c, data.training_rows());
      const auto initial_dev = metrics(initial, c, data.development_rows());
      auto result = train(c, data, config, argv[4], std::string(argv[7]) == "1", max_epochs);
      const auto best_train = metrics(result.best_model, c, data.training_rows());
      const auto best_dev = metrics(result.best_model, c, data.development_rows());
      double parameter_delta = 0;
      int64_t parameters = 0;
      for (const auto& parameter : result.final_model->named_parameters()) {
        parameters += parameter.value().numel();
        parameter_delta += (parameter.value() - initial->named_parameters()[parameter.key()]).abs().sum().item<double>();
      }
      Files files = {{"final.pt", save_model_bytes(result.final_model)}, {"best.pt", save_model_bytes(result.best_model)},
                     {"state.json", canonical(result.state)}, {"model.config.json", canonical(c.model_config.json())}};
      const auto environment = numerical_environment();
      const auto weight_digest = sha256(files.at("best.pt"));
      Json training = {{"training_run_id", "research:music:train:1"}, {"config", config.json()}, {"state", result.state},
                       {"checkpoint_digest", result.checkpoint_digest}, {"dataset_digest", data.manifest_digest()},
                       {"environment_digest", sha256(environment)}, {"descriptor_digest", sha256(canonical(c.registry.descriptor()))},
                       {"build_digest", c.registry.build_digest()}, {"model_config", c.model_config.json()}, {"weights_digest", weight_digest}};
      files["training.json"] = canonical(training);
      Json summary = {{"state", result.state}, {"gradient_l1", result.gradient_l1}, {"parameter_delta_l1", parameter_delta},
                      {"parameters_changed", parameter_delta > 0}, {"parameter_count", parameters},
                      {"initial_train", initial_train}, {"initial_dev", initial_dev}, {"best_train", best_train}, {"best_dev", best_dev},
                      {"environment_digest", sha256(environment)}, {"environment", parse_json(environment)},
                      {"final_sha256", sha256(files.at("final.pt"))}, {"best_sha256", weight_digest},
                      {"checkpoint_digest", result.checkpoint_digest}, {"dataset_digest", data.manifest_digest()},
                      {"build_digest", c.registry.build_digest()}, {"tensor_inventory", tensor_inventory(result.best_model)},
                      {"claim", "Bounded MIDI next-token training mechanics; no musical-quality or production claim."}};
      files["summary.json"] = canonical(summary);
      Json manifest = {{"schema_version", "research.music.export.v1"}, {"purpose", "unadmitted_offline_research_checkpoint"},
                       {"descriptor_digest", training["descriptor_digest"]}, {"dataset_digest", data.manifest_digest()},
                       {"build_digest", c.registry.build_digest()}, {"environment_digest", sha256(environment)},
                       {"checkpoint_digest", result.checkpoint_digest}, {"weights_digest", weight_digest},
                       {"model_config", c.model_config.json()}, {"files", inventory(files)}};
      files["manifest.json"] = canonical(manifest);
      publish_tree(argv[5], files);
      summary["export_digest"] = sha256(files.at("manifest.json"));
      std::cout << canonical(summary);
      return 0;
    }
    if (argc == 7 && std::string(argv[1]) == "infer") {
      auto loaded = load_research_export(argv[2], argv[3], argv[4], argv[6]);
      auto inputs = read_json(argv[5]);
      require(inputs.is_array() && !inputs.empty() && inputs.size() <= 4096, "music inference input count");
      Json predictions = Json::array();
      torch::NoGradGuard no;
      for (size_t i = 0; i < inputs.size(); ++i) {
        const auto& input = inputs[i];
        loaded.composition.registry.payload("input_schema", input);
        auto logits = loaded.model->forward(loaded.composition.encode({input})).flatten();
        auto output = loaded.composition.decode(logits);
        loaded.composition.registry.payload("output_schema", output);
        predictions.push_back({{"index", i}, {"input", input}, {"output", output}, {"token", output["token"]},
                               {"raw_output", floats(logits)}, {"probabilities", floats(torch::softmax(logits, 0))}});
      }
      std::cout << canonical(Json{{"predictions", predictions}, {"identity", export_identity(loaded)}});
      return 0;
    }
    if (argc == 10 && std::string(argv[1]) == "generate") {
      auto loaded = load_research_export(argv[2], argv[3], argv[4], argv[9]);
      auto input = read_json(argv[5], 64 * 1024);
      loaded.composition.registry.payload("input_schema", input);
      const auto steps = std::stoll(argv[6]);
      const auto seed = std::stoll(argv[7]);
      const auto temperature = std::stod(argv[8]);
      require(steps >= 1 && steps <= 128 && seed >= 0 && std::isfinite(temperature) && temperature >= 0 && temperature <= 2,
              "music generation bounds");
      const auto primer = input;
      auto context = input["tokens"].get<std::vector<int64_t>>();
      bool active = false;
      for (auto token : context) { if (token == 0) active = false; else if (token >= 2) active = true; }
      torch::manual_seed(seed);
      torch::NoGradGuard no;
      Json generated = Json::array(), diagnostics = Json::array();
      int64_t hold_masks = 0;
      double log_probability_sum = 0;
      for (int64_t step = 0; step < steps; ++step) {
        input["tokens"] = context;
        auto logits = loaded.model->forward(loaded.composition.encode({input})).flatten();
        auto constrained_logits = logits.clone();
        const bool mask_hold = !active;
        if (mask_hold) { constrained_logits[1] = -1e9; ++hold_masks; }
        auto probabilities = torch::softmax(constrained_logits / (temperature > 0 ? temperature : 1.), 0);
        const auto token = temperature == 0 ? constrained_logits.argmax().item<int64_t>() : torch::multinomial(probabilities, 1).item<int64_t>();
        const auto probability = probabilities[token].item<double>();
        const auto log_probability = std::log(probability);
        require(std::isfinite(log_probability) && token >= 0 && token < 27 && !(mask_hold && token == 1), "music generated token validity");
        loaded.composition.registry.payload("output_schema", Json{{"token", token}});
        generated.push_back(token);
        diagnostics.push_back({{"step", step}, {"position", input["position"]}, {"token", token},
                               {"hold_masked", mask_hold}, {"selected_probability", probability}, {"log_probability", log_probability},
                               {"raw_output", floats(logits)}, {"probabilities", floats(probabilities)}});
        log_probability_sum += log_probability;
        if (token == 0) active = false; else if (token >= 2) active = true;
        context.erase(context.begin());
        context.push_back(token);
        input["position"] = (input["position"].get<int64_t>() + 1) % 16;
      }
      std::cout << canonical(Json{{"identity", export_identity(loaded)}, {"primer", primer}, {"generated_tokens", generated},
                                 {"steps", steps}, {"seed", seed}, {"temperature", temperature},
                                 {"sampling", temperature == 0 ? "greedy" : "torch-multinomial-cpu"},
                                 {"hold_mask_applications", hold_masks}, {"active_note_context", "inferred_from_eight_step_primer_only"},
                                 {"log_probability_sum", log_probability_sum}, {"diagnostics", diagnostics}});
      return 0;
    }
    throw std::invalid_argument(
      "usage: music_driver build-identity | train DATA DIGEST CHECKPOINT EXPORT EPOCHS_THIS_CALL RESUME [TOTAL_EPOCHS] | "
      "infer DATA DIGEST EXPORT INPUT_JSON EXPECTED_EXPORT_DIGEST | "
      "generate DATA DIGEST EXPORT PRIMER_JSON STEPS SEED TEMPERATURE EXPECTED_EXPORT_DIGEST");
  } catch (const std::exception& error) {
    std::cerr << "native music operation rejected: " << error.what() << '\n';
    return 1;
  }
}
