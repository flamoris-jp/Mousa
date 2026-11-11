#include "composition.h"
#include "maidionis/storage.h"
#include <algorithm>
#include <map>
#include <regex>

using namespace maidionis;
namespace music_research {
namespace {
constexpr auto prefix = "research.music-next-token.";
void require(bool value, const char* message) {
  if (!value) throw std::invalid_argument(message);
}
Json object_schema(const Json& properties, const Json& required) {
  return {{"type", "object"}, {"properties", properties}, {"required", required}, {"additionalProperties", false}};
}
Json reference(const std::string& name, const Json& config) {
  return {{"id", std::string(prefix) + name}, {"version", "1"}, {"config_digest", sha256(canonical(config))}};
}
struct Work { std::vector<int64_t> tokens; std::string split; };
}

std::string build_digest() {
  return sha256("maidionis-music-build-v1\n" + compiled_build_digest() + "\n" + MUSIC_SOURCE_DIGEST + "\n");
}
std::string semantic_spec() {
  return "Music Next Token v1: predict one sixteenth-grid token from the previous eight tokens and position modulo 16. Token 0 is REST, 1 is HOLD, and 2..26 are MIDI pitches 60..84. Work SHA-256 is provenance only and is excluded from model features. Offline research; no musical-quality or production claim.\n";
}

NumericalComposition composition(const std::filesystem::path& root) {
  auto read = [&](const std::string& path) {
    return parse_json(immutable_read(root / path, 4 * 1024 * 1024), 4 * 1024 * 1024);
  };
  const auto descriptor = read("descriptor.json");
  RegistryBuilder builder(build_digest());
  Json integer_token = {{"type", "integer"}, {"minimum", 0}, {"maximum", 26}};
  const auto input = object_schema({
      {"work_sha256", {{"type", "string"}, {"pattern", "^[a-f0-9]{64}$"}}},
      {"tokens", {{"type", "array"}, {"minItems", 8}, {"maxItems", 8}, {"items", integer_token}}},
      {"position", {{"type", "integer"}, {"minimum", 0}, {"maximum", 15}}}},
      {"work_sha256", "tokens", "position"});
  const auto token_output = object_schema({{"token", integer_token}}, {"token"});
  for (const auto& name : {"input", "target", "output"}) {
    const auto expected = std::string(name) == "input" ? input : token_output;
    const auto definition = read(std::string(name) + ".schema.json");
    const auto& ref = descriptor[std::string(name) + "_schema"];
    require(ref["id"] == std::string(prefix) + name && ref["version"] == "1" && definition == expected,
            "music compiled schema binding");
    builder.add_schema(ref, definition);
  }
  const std::map<std::string, Json> configs = {
    {"input_codec", {{"context_steps", 8}, {"classes", 27}, {"positions", 16}, {"encoding", "onehot-context-position-v1"}, {"features", 232}}},
    {"output_codec", {{"decode", "argmax-first-v1"}, {"classes", 27}}},
    {"architecture", {{"kind", "dense"}, {"input_width", 232}, {"hidden_width", 64}, {"output_width", 27}, {"dropout_milli", 0}}},
    {"head", {{"outputs", 27}}},
    {"objective", {{"kind", "categorical"}, {"reduction", "mean"}, {"eligibility", "all-rows"}}},
    {"numerical_compatibility", {{"profile", "linux.cpu.fp32.serial.v1"}, {"libtorch", "2.5.1"}, {"archive", 1}}}
  };
  for (const auto& [name, expected] : configs) {
    const auto& ref = name == "head" ? descriptor["heads"][0] : descriptor[name];
    const auto actual = read(name + ".config.json");
    require(ref == reference(name, expected) && actual == expected, "music compiled operation binding");
    builder.add_operation(ref, actual, [expected](const Json& config) {
      require(config == expected, "music operation configuration");
    });
  }
  require(descriptor["specialization_id"] == "research.music-next-token" && descriptor["specialization_version"] == "1" &&
          descriptor["task_id"] == "research.music-next-token" && descriptor["task_version"] == "1" &&
          descriptor["diagnostics_schema"] == nullptr && descriptor["heads"].size() == 1 &&
          descriptor["semantic_spec"]["path"] == "semantic.txt", "music descriptor identity");
  const auto spec = immutable_read(root / "semantic.txt", 4096);
  require(spec == semantic_spec() && sha256(spec) == descriptor["semantic_spec"]["sha256"].get<std::string>(), "music semantic binding");

  const auto source_bytes = immutable_read(root / "sources.json", 4 * 1024 * 1024);
  const auto source_digest = sha256(source_bytes);
  const auto manifest = read("manifest.json");
  validate_record("dataset", manifest);
  size_t source_entries = 0;
  for (const auto& entry : manifest["files"]) if (entry["path"] == "sources.json") {
    ++source_entries;
    require(entry["sha256"] == source_digest && entry["bytes"] == source_bytes.size(), "music source inventory binding");
  }
  require(source_entries == 1, "music source inventory coverage");
  const auto sources = parse_json(source_bytes, 4 * 1024 * 1024);
  require(sources.is_object() && sources.size() == 2 && sources["schema_version"] == "music.sources.v1" &&
          sources["works"].is_array() && !sources["works"].empty() && sources["works"].size() <= 128,
          "music source corpus shape");
  require(canonical(sources) == source_bytes, "music source canonical bytes");
  std::map<std::string, Work> works;
  for (const auto& source : sources["works"]) {
    require(source.is_object() && source.size() == 3 && source.contains("work_sha256") && source.contains("tokens") &&
            source.contains("split") && source["work_sha256"].is_string() && source["tokens"].is_array() &&
            source["tokens"].size() > 8 && source["tokens"].size() <= 65536 && source["split"].is_string(), "music source shape");
    const auto key = source["work_sha256"].get<std::string>();
    const auto split = source["split"].get<std::string>();
    require(std::regex_match(key, std::regex("[a-f0-9]{64}")) && (split == "train" || split == "dev" || split == "test"),
            "music source identity/split");
    std::vector<int64_t> tokens;
    for (const auto& token : source["tokens"]) {
      require(token.is_number_integer() && token.get<int64_t>() >= 0 && token.get<int64_t>() < 27, "music source token range");
      tokens.push_back(token.get<int64_t>());
    }
    require(works.emplace(key, Work{std::move(tokens), split}).second, "duplicate music source identity");
  }

  NumericalComposition c;
  c.registry = builder.freeze(descriptor);
  c.model_config.kind = "dense";
  c.model_config.input_width = 232;
  c.model_config.hidden_width = 64;
  c.model_config.output_width = 27;
  c.model_config.dropout_milli = 0;
  c.encode = [registry = c.registry](const std::vector<Json>& rows) {
    std::vector<std::vector<float>> features;
    std::vector<int64_t> targets;
    bool with_targets = !rows.empty() && rows.front().contains("input");
    for (const auto& row : rows) {
      require(row.contains("input") == with_targets, "mixed music batch framing");
      const auto& payload = with_targets ? row["input"] : row;
      if (with_targets) registry.sample(row); else registry.payload("input_schema", payload);
      std::vector<float> feature(232, 0.f);
      for (size_t i = 0; i < 8; ++i) feature[i * 27 + payload["tokens"][i].get<size_t>()] = 1.f;
      feature[216 + payload["position"].get<size_t>()] = 1.f;
      features.push_back(std::move(feature));
      if (with_targets) targets.push_back(row["target"]["token"].get<int64_t>());
    }
    auto batch = dense_batch(features, {}, 232, 27);
    if (with_targets) {
      batch.targets = torch::tensor(targets, torch::TensorOptions().dtype(torch::kInt64));
      batch.target_mask = torch::ones({int64_t(targets.size())}, torch::TensorOptions().dtype(torch::kBool));
    }
    return batch;
  };
  c.objective = [](const torch::Tensor& logits, const Batch& batch) {
    return categorical_loss(logits, batch.targets, batch.target_mask);
  };
  c.decode = [](const torch::Tensor& logits) {
    require(logits.numel() == 27 && torch::isfinite(logits).all().item<bool>(), "music output shape/finiteness");
    return Json{{"token", logits.flatten().argmax().item<int64_t>()}};
  };
  const auto group = reference("group", {{"projection", "work-sha256-v1"}});
  const auto dedup = reference("dedup", {{"projection", "work-window-v1"}});
  const auto hook = reference("dataset-hooks", {{"implementation", "music-sources-v1"}, {"build_digest", build_digest()}});
  const auto verification = reference("source-verifier", {{"verification", "source-window-target-v1"}, {"sources_digest", source_digest}});
  const Json generator_config = {{"pipeline", "midi-monophonic-grid-v1"}, {"context_steps", 8}, {"classes", 27}, {"sources_digest", source_digest}};
  c.split_algorithm = "research.music.by-work.v1";
  c.assign_family = [works](const Json& family, const Json&, const Json&) {
    require(family["roots"].size() == 1, "music family root count");
    const auto key = family["roots"][0]["content"]["work_sha256"].get<std::string>();
    require(works.contains(key), "unregistered music family");
    return works.at(key).split;
  };
  c.verify_dataset_row = [works, group, dedup, hook, verification, generator_config](
      const Json& row, const Json& family, const Json& data_manifest, const Json& split_config) {
    const auto& input = row["input"];
    const auto key = input["work_sha256"].get<std::string>();
    require(works.contains(key), "music source missing");
    const auto& source = works.at(key);
    const auto id = row["sample_id"].get<std::string>();
    const auto beginning = "midi:" + key + ":";
    require(id.starts_with(beginning), "music window sample identity");
    const auto suffix = id.substr(beginning.size());
    require(std::regex_match(suffix, std::regex("[0-9]{1,6}")), "music window index");
    const auto index = std::stoull(suffix);
    require(index >= 8 && index < source.tokens.size() && suffix == std::to_string(index), "music window bound");
    const Json expected_context = std::vector<int64_t>(source.tokens.begin() + index - 8, source.tokens.begin() + index);
    const Json root = {{"work_sha256", key}};
    require(input["tokens"] == expected_context && input["position"] == index % 16 && row["target"] == Json{{"token", source.tokens[index]}} &&
            row["split"] == source.split && row["supersedes"] == nullptr, "music source window/target binding");
    require(family["roots"] == Json::array({Json{{"digest", sha256(canonical(root))}, {"content", root}}}) &&
            split_config["grouping"] == group && split_config["hook"] == hook &&
            data_manifest["dedup_profile"] == dedup && data_manifest["verification_profile"] == verification &&
            row["verification_profile"] == verification &&
            data_manifest["generator"] == Json{{"code_digest", build_digest()}, {"config_digest", sha256(canonical(generator_config))}},
            "music frozen eligibility/profile binding");
  };
  c.validate();
  return c;
}
}
