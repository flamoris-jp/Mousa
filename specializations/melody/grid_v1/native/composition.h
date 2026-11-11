#pragma once
#include "maidionis/model.h"

namespace music_research {
std::string build_digest();
std::string semantic_spec();
maidionis::NumericalComposition composition(const std::filesystem::path& dataset_root);
}
