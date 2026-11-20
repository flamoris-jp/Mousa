#include "maidionis/model.h"
#include <torch/torch.h>
#include <fstream>
#include <iostream>
#include <ctime>
#include <cmath>
using namespace maidionis;
Batch batch(const Json& rows){
 std::vector<int64_t> x,y;
 for(const auto& r:rows){for(auto v:r.at("input"))x.push_back(v.get<int64_t>());y.push_back(r.at("label").get<int64_t>());}
 Batch b;b.inputs=torch::from_blob(x.data(),{int64_t(rows.size()),3},torch::kInt64).clone();b.targets=torch::from_blob(y.data(),{int64_t(rows.size())},torch::kInt64).clone();b.mask=b.inputs.ne(0);b.segments=torch::zeros_like(b.inputs);b.target_mask=torch::ones_like(b.targets,torch::kBool);return b;
}
Json evaluate(ModelPtr m,const Batch& b){
 m->eval();torch::NoGradGuard no;auto logits=m->forward(b);auto pred=logits.argmax(1);auto probs=torch::softmax(logits,1);double diff=0;Json rows=Json::array();
 for(int64_t i=0;i<b.inputs.size(0);++i){rows.push_back({{"target",b.targets[i].item<int64_t>()},{"prediction",pred[i].item<int64_t>()},{"probability1",probs[i][1].item<double>()}});if(i%2==0)diff=std::max(diff,(logits[i]-logits[i+1]).abs().max().item<double>());}
 return {{"n",b.targets.size(0)},{"accuracy",pred.eq(b.targets).to(torch::kFloat32).mean().item<double>()},{"nll",categorical_loss(logits,b.targets,b.target_mask).item<double>()},{"reverse_pair_max_logit_difference",diff},{"predictions",rows}};
}
int main(int argc,char**argv){try{
 if(argc!=4)throw std::runtime_error("usage: order_diagnostic DATASET PLAN OUTPUT");Json data,plan;std::ifstream(argv[1])>>data;std::ifstream(argv[2])>>plan;
 auto tr=batch(data.at("train")),te=batch(data.at("test"));Json results=Json::array();const auto start=std::clock();
 for(const auto& kind:{"pooled","encoder"})for(auto seed:plan.at("seeds")){
  ModelConfig c;c.kind=kind;c.hidden_width=256;c.input_width=2;c.output_width=2;c.vocabulary=10;c.controls={1};c.dropout_milli=0;
  auto m=make_seeded_model(c,seed.get<int64_t>());std::vector<torch::Tensor> initial;int64_t params=0;for(auto& p:m->parameters()){initial.push_back(p.detach().clone());params+=p.numel();}
  Json result={{"kind",kind},{"seed",seed},{"parameters",params},{"initial_train",evaluate(m,tr)},{"initial_test",evaluate(m,te)}};
  torch::optim::AdamW opt(m->parameters(),torch::optim::AdamWOptions(plan.at("learning_rate").get<double>()).weight_decay(0));double grad_sum=0;Json history=Json::array();
  for(int step=0;step<plan.at("steps").get<int>();++step){
   if(double(std::clock()-start)/CLOCKS_PER_SEC>plan.at("maximum_run_cpu_seconds").get<double>())throw std::runtime_error("CPU budget exceeded");
   m->train();opt.zero_grad();auto loss=categorical_loss(m->forward(tr),tr.targets,tr.target_mask);loss.backward();
   for(auto& p:m->parameters()){if(!p.grad().defined()||!torch::isfinite(p.grad()).all().item<bool>())throw std::runtime_error("bad gradient");grad_sum+=p.grad().abs().sum().item<double>();}
   torch::nn::utils::clip_grad_norm_(m->parameters(),1.0);opt.step();m->enforce_constraints();history.push_back(loss.item<double>());
  }
  double delta=0;auto ps=m->parameters();for(size_t i=0;i<ps.size();++i)delta+=(ps[i].detach()-initial[i]).abs().sum().item<double>();
  result["final_train"]=evaluate(m,tr);result["final_test"]=evaluate(m,te);result["gradient_l1_sum"]=grad_sum;result["parameter_delta_l1"]=delta;result["training_losses"]=history;
  auto bytes=save_model_bytes(m);auto reload=make_seeded_model(c,9);load_model_bytes(reload,bytes);reload->eval();m->eval();{torch::NoGradGuard n;result["archive_reload_exact"]=torch::equal(m->forward(te),reload->forward(te));}
  results.push_back(result);std::cerr<<kind<<" "<<seed<<" complete train="<<result["final_train"]["accuracy"]<<" test="<<result["final_test"]["accuracy"]<<"\n";
 }
 Json out={{"plan",plan},{"results",results},{"cpu_seconds",double(std::clock()-start)/CLOCKS_PER_SEC},{"numerical_environment",parse_json(numerical_environment())}};std::ofstream f(argv[3]);f<<out.dump(2)<<"\n";return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<"\n";return 1;}}
